#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import os
import json
import codecs
import datetime
import glob
import unicodedata
import subprocess
import tempfile
import time
import re
import sys
import syslog
import urllib.request
from os import listdir
from os.path import isfile,isdir,join
from jsondiff import diff
import n4d.client
import copy

class GuardManager(object):

	MISSING_LIST_NAME_ERROR=-1
	LIST_NAME_DUPLICATE=-2
	SAVING_FILE_ERROR=-5
	CHANGE_GUARDMODE_ERROR=-9
	RESTARTING_DNSMASQ_ERROR=-10
	READ_LIST_INFO_ERROR=-13
	LOADING_FILE_ERROR=-16
	REMOVING_LIST_ERROR=-19
	ACTIVATING_LIST_ERROR=-20
	DEACTIVATING_LIST_ERROR=-21
	READ_GUARDMODE_ERROR=-23
	READ_GUARDMODE_HEADERS_ERROR=-25
	EMPTY_FILE_ERROR=-27
	LOAD_FILE_SIZE_OFF_LIMITS_ERROR=-30
	EDIT_FILE_SIZE_OFF_LIMITS_ERROR=-31
	READ_FILE_ERROR=-34
	EMPTY_LIST_ERROR=-35

	ALL_CORRECT_CODE=0
	LIST_CREATED_SUCCESSFUL=3
	LIST_EDITED_SUCCESSFUL=4
	CHANGE_GUARDMODE_SUCCESSFUL=8
	READ_LIST_INFO_SUCCESSFUL=12
	LOAD_FILE_SUCCESSFUL=15
	CHANGES_APPLIED_SUCCESSFUL=18
	READ_GUARDMODE_SUCCESSFUL=22
	READ_GUARDMODE_HEADERS_SUCCESSFUL=24
	READ_FILE_SUCCESSFUL=35


	def __init__(self,server=None):

		super(GuardManager, self).__init__()

		self.dbg=0
		self.userValidated=False
		self.limitLines=2500
		self.limitFileSize=28000000
		self.garbageFiles=[]
		self.credentials=[]
		self.guardMode="DisableMode"
		self.listsConfig={}
		self.listsConfigOrig={}
		self.listsConfigData=[]
		self.urlConfigData=[]
		self.detectFlavour()
		self._getSystemLocale()
		self.initValues()

	
	#def __init__	
			
	def detectFlavour(self):
		
		self.is_server=""
		self.is_client=""
		self.is_desktop=""

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]

		for item in flavours:
			if 'server' in item:
				self.is_server=True
				self.is_desktop=False
				self.server_ip="server"
				break
			elif 'client' in item:
				self.is_client=True
				self.is_desktop=False
				self.server_ip="server"
				break
			elif 'desktop' in item:
				self.is_desktop=True
				self.server_ip="localhost"	

	#def detect_flavour

	def _getSystemLocale(self):

		language=os.environ["LANGUAGE"]

		if language!="":
			tmpLang=language.split(":")
			self.systemLocale=tmpLang[0]
		else:
			self.systemLocale=os.environ["LANG"]

	#def _getSystemLocale	
	
	def createN4dClient(self,ticket,passwd):

		ticket=ticket.replace('##U+0020##',' ')
		self.credentials.append(ticket.split(' ')[2])
		self.credentials.append(passwd)

		self.tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=self.tk)

		self.localClient=n4d.client.Client("https://localhost:9779",self.credentials[0],self.credentials[1])
		local_t=self.localClient.get_ticket()
		if local_t.valid():
			self.localClient=n4d.client.Client(ticket=local_t)
			self.userValidated=True
		else:
			self.userValidated=False

		msgLog='Session user: %s Lliurex-Guard user: %s'%(os.environ["USER"],self.credentials[0])
		self.writeLog(msgLog)


	#def create_n4dClient

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[LLIUREX_GUARD]: "+ str(function) + str(msg))

	#def _debug

	def initValues(self):

		self.listToLoad=[]
		self.listName=""
		self.listDescription=""
		self.currentListConfig={}
		self.currentListConfig["id"]=""
		self.currentListConfig["name"]=""
		self.currentListConfig["description"]=""
		self.urlConfigData=[]
		
	#def initValues		

	def readGuardmode(self):
			
		readGuardmode=self.client.LliurexGuardManager.read_guardmode(True)
		msg="Read LliureX Guard Mode: "
		self._debug(msg,readGuardmode)
		msgLog=msg+str(readGuardmode)
		self.writeLog(msgLog)
		if readGuardmode['status']:
			self.guardMode=readGuardmode['data']
			return {'status':True,'code':GuardManager.READ_GUARDMODE_SUCCESSFUL,'data':readGuardmode['data']}
		else:
			return {'status':False,'code':GuardManager.READ_GUARDMODE_ERROR,'data':readGuardmode['data']}

	#def read_guardmode

	def changeGuardmode(self,mode):

		changeGuardmode=self.client.LliurexGuardManager.change_guardmode(mode)
		msg="LliureX Guard Mode changed to %s"%mode
		self._debug(msg,changeGuardmode)
		msgLog=msg+str(changeGuardmode)
		self.writeLog(msgLog)
		
		if changeGuardmode['status']:
			msg="LliureX Guard Mode changed. Dnsmasq restarted "
			forceRestartDnsmasq=False
			self.listsConfig={}
			self.listsConfigOrig={}
			self.listsConfigData=[]

			if mode !="DisableMode" :
				forceRestartDnsmasq=True
			else:
				if self.is_server:
					forceRestartDnsmasq=True
			
			if forceRestartDnsmasq:
				restartDnsmasq=self.restartDnsmasq(msg)
				if restartDnsmasq['status']:
					return {'status':True,'code':GuardManager.CHANGE_GUARDMODE_SUCCESSFUL}
				else:
					return {'status':False,'code':GuardManager.RESTARTING_DNSMASQ_ERROR,'data':restartDnsmasq['data']}
			else:
				return {'status':True,'code':GuardManager.CHANGE_GUARDMODE_SUCCESSFUL}
			
		else:
			return {'status':False,'code':GuardManager.CHANGE_GUARDMODE_ERROR,'data':change_guardmode['data']}		
				
	#def changeGuardmode 		

	def readGuardmodeHeaders(self):

		self.listsConfig={}
		self.listsConfigOrig={}
		self.listsConfigData=[]

		readGuardmodeHeaders=self.client.LliurexGuardManager.read_guardmode_headers()
		msg="LliureX Guard mode lists readed "
		self._debug(msg,readGuardmodeHeaders)
		msgLog=msg+str(readGuardmodeHeaders)
		self.writeLog(msgLog)
		if readGuardmodeHeaders['status']:
			self.listsConfig=readGuardmodeHeaders['data']
			for item in self.listsConfig:
				#tmp_list[item]['edited']=False
				self.listsConfig[item]['remove']=False
				self.listsConfig[item]["replaced_to"]=""
				self.listsConfig[item]["tmpfile"]=""

			self.listsConfigOrig=copy.deepcopy(self.listsConfig)
			self._getListsConfig()

			return {'status':True,'code':GuardManager.READ_GUARDMODE_HEADERS_SUCCESSFUL,'data':""}	

		else:
			return {'status':False,'code':GuardManager.READ_GUARDMODE_HEADERS_ERROR,'data':str(readGuardmodeHeaders['data'])}
		
	#def readGuardmodeHeaders

	def _getListsConfig(self):

		orderList=self._getOrderList()
		self.listsConfigData=[]
		
		for item in orderList:
			tmp={}
			tmp["order"]=item
			tmp["id"]=self.listsConfig[item]["id"]
			tmp["name"]=self.listsConfig[item]["name"]
			tmp["entries"]=self.listsConfig[item]["lines"]
			tmp["description"]=self.listsConfig[item]["description"]
			tmp["activated"]=self.listsConfig[item]["active"]
			tmp["remove"]=self.listsConfig[item]["remove"]
			tmp["metaInfo"]=tmp["name"]+tmp["description"]

			self.listsConfigData.append(tmp)

	#def _getListsConfig

	def loadListConfig(self,listToLoad):

		self.listToLoad=str(listToLoad)
		self.currentListConfig=self.listsConfig[self.listToLoad]
		self.listName=self.currentListConfig["name"]
		self.listDescription=self.currentListConfig["description"]

		return self._readGuardModeList()

	#def loadListConfig

	def _readGuardModeList(self):
			
		isTmpFile=False
		status=True
		tmpFile=""
		content=None
		result=[]
		lines=[]
		errorInfo=[]
		countLines=0
		listId=self.currentListConfig["id"]
		active=self.currentListConfig["active"]

		if self.currentListConfig["tmpfile"]!="":
			readTmpFile=self.readLocalFile(self.currentListConfig["tmpfile"],False)
			msg="List %s. Readed local file (%s)"%(listId,self.currentListConfig["tmpfile"])
			self._debug(msg,readTmpFile)

			if readTmpFile['status']:
				content=readTmpFile['data'][0]
				countLines=readTmpFile['data'][1]
				isTmpFile=True

			else:
				status=False
				errorInfo=readTmpFile['data']
		else:
			readGuardmodeList=self.client.LliurexGuardManager.read_guardmode_list(listId,active)
			msg="List %s. Readed file"%listId
			self._debug(msg,readGuardmodeList)

			if readGuardmodeList['status']:
				content=readGuardmodeList['data'][0]
				countLines=readGuardmodeList['data'][1]
			else:
				status=False
				errorInfo=readGuardmodeList['data']

			readGuardmodeList=None	
		if status:
			code=GuardManager.READ_LIST_INFO_SUCCESSFUL

			if countLines>self.limitLines:
				if not isTmpFile:
					tmpFile=self._createTmpFile(listId)
					f=open(tmpFile,'w')
					tmpContent="".join(content)
					f.write(tmpContent)
					f.close()
					tmpContent=None
					self.garbageFiles.append(tmpFile)
				else:
					tmpFile=readTmpFile['data'][2]	
				content=None
				readTmpFile=None
			else:
				self._getUrlConfig(content)

			result=tmpFile
			msgLog=msg + " successfully"
		else:
			code=GuardManager.READ_LIST_INFO_ERROR
			result=errorInfo
			msgLog=msg+ "with errors. Error details: "+str(errorInfo)
		
		self.writeLog(msgLog)
		return {'status':status,'code':code,'data':result}

	#def readGuardmodeList	
			
	def readLocalFile(self,file,createTmpfile):

		content=[]
		countLines=0
		tmpFile=""
		try:
			if os.path.exists(file):
				if createTmpfile:
					if os.path.getsize(file)>self.limitFileSize:
						return {'status':False,'code':GuardManager.LOAD_FILE_SIZE_OFF_LIMITS_ERROR,'data':''}	
				f=open(file,'r')
				lines=f.readlines()
				for line in lines:
					if "NAME" not in line:
						if "DESCRIPTION" not in line:
							if line !="":
								line=self.formatLine(line)
								if line!="":
									content.append(line)	
									countLines+=1
				f.close()
				lines=None
				tmpFile=file
				
				if createTmpfile:
					if countLines==0:
						return {'status':False,'code':GuardManager.EMPTY_FILE_ERROR,'data':''}
					else:	
						tmpFile=self._createTmpFile(os.path.basename(file))
						f=open(tmpFile,'w')
						f.write("".join(content))
						f.close()
						if countLines>self.limitLines:
							content=None

				self.garbageFiles.append(tmpFile)		
				
				return {'status':True,'code':GuardManager.LOAD_FILE_SUCCESSFUL,'data':[content,countLines,tmpFile]}
			else:
				return {'status':False,'code':GuardManager.LOADING_FILE_ERROR,'data':str(e)}	

		except Exception as e:
			return {'status':False,'code':GuardManager.LOADING_FILE_ERROR,'data':str(e)}

	#def readLocalFile

	def loadFile(self,fileToLoad):

		data=""
		limitLines=False
		ret=self.readLocalFile(fileToLoad,True)

		if ret["status"]:
			if ret["data"][0]!=None:
				self._getUrlConfig(ret["data"][0])
			else:
				limitLines=True
			data=[limitLines,ret["data"][2]]
		else:
			data=ret["data"]

		return {'status':ret['status'],'code':ret['code'],'data':data}
			
	#def loadFile

	def changeListsStatus(self,allLists,active,listToEdit):

		if allLists:
			for item in self.listsConfig:
				if not self.listsConfig[item]["remove"]:
					self.listsConfig[item]["active"]=active
		else:
			self.listsConfig[str(listToEdit)]["active"]=active

		self._updateListsConfigData("activated",active,listToEdit)
	
	#def changeListsStatus

	def removeLists(self,allLists,listToRemove):

		if allLists:
			for item in self.listsConfig:
				self.listsConfig[item]["remove"]=True
		else:
			self.listsConfig[str(listToRemove)]["remove"]=True

		self._updateListsConfigData("remove",True,listToRemove)
	
	#def removeLists

	def restoreList(self,listToRestore):

		self.listsConfig[str(listToRestore)]["remove"]=False

		self._updateListsConfigData("remove",False,listToRestore)

	#def restoreList

	def _updateListsConfigData(self,param,value,listToEdit):
		
		if listToEdit!=None:
			for item in self.listsConfigData:
				if item["order"]==str(listToEdit):
					if item[param]!=value:
						item[param]=value
					break
		else:
			for item in self.listsConfigData:
				if item[param]!=value:
					if param!="remove":
						if not item["remove"]:
							item[param]=value
					else:
						item[param]=value

	#def _updateListsConfigData		

	def _getUrlConfig(self,content):

		self.urlConfigData=[]
		for item in content:
			tmp={}
			tmp["url"]=item.strip()
			self.urlConfigData.append(tmp)

	#def _getUrlConfig

	def saveConf(self,listInfo,edit,fileToSave=None):

		result={}
		ret=self._createFileToSave(listInfo["id"],fileToSave)

		if ret["status"]:
			if edit:
				order=str(self.listToLoad)
				msgCode=GuardManager.LIST_EDITED_SUCCESSFUL
				if self.listsConfig[order]["id"]!=listInfo["id"]:
					self.listsConfig[order]["replaced_to"]=self.listsConfig[order]["id"]
			else:
				order=str(len(self.listsConfig)+1)
				msgCode=GuardManager.LIST_CREATED_SUCCESSFUL
				self.listsConfig[order]={}
				self.listsConfig[order]["active"]=True
				self.listsConfig[order]["remove"]=False
				self.listsConfig[order]["replaced_to"]=""

			self.listsConfig[order]["id"]=listInfo["id"]
			self.listsConfig[order]["name"]=listInfo["name"]
			self.listsConfig[order]["description"]=listInfo["description"]
			self.listsConfig[order]["lines"]=ret["lines"]
			self.listsConfig[order]["tmpfile"]=ret["tmpfile"]
			self.listsConfig[order]["edited"]=True

			self._getListsConfig()

		else:
			msgCode=ret["code"]
		
		result["status"]=ret["status"]
		result["code"]=msgCode
		result["data"]=ret["data"]

		return result

	#def saveConf		

	def _createFileToSave(self,listId,fileToSave=None):

		error=False
		result={}
		countLines=0
		urlToRemove=[]

		try:
			if fileToSave==None:
				tmpList=self._createTmpFile(listId)
				self.garbageFiles.append(tmpList)
			else:
				tmpList=fileToSave

			if fileToSave!=None:
				tmpContent=[]
				f=open(tmpList,'r')
				lines=f.readlines()
				f.close()
				f=open(tmpList,'w')
				for line in lines:
					if line!="":
						line=self.formatLine(line)
						if line!="":
							f.write(line)
							countLines+=1
		
				f.close()		
				
			else:
				formatContent=[]	
				for item in self.urlConfigData:
					if item["url"]!="":
						line=self.formatLine(item["url"])
						if line!="":
							item["url"]=line
							formatContent.append(line+"\n") 
							countLines+=1	
						else:
							urlToRemove.append(item)
				
				for item in urlToRemove:
					if item in self.urlConfigData:
						self.urlConfigData.remove(item)

				f=open(tmpList,"w")
				f.write("".join(formatContent))
				f.close()

			content=None
			formatContent=None
			urltoRemove=[]
			if countLines>0:
				result["status"]=True
			else:
				result["status"]=False
				result["code"]=GuardManager.EMPTY_LIST_ERROR
			result["tmpfile"]=tmpList
			result["lines"]=countLines
			result["data"]=""
			
		except Exception as e:
			result['status']=False
			result['code']=GuardManager.SAVING_FILE_ERROR
			result['data']=str(e)
		
		msg="List %s. Saved changes "%listId
		self._debug(msg,result)
		msgLog=msg+" "+str(result)	
		self.writeLog(msgLog)

		return result
		
	#def _createFileToSave		

	def checkData(self,data,edit,loadedFile):

		if data[1]=="":
			return {"result":False,"code":GuardManager.MISSING_LIST_NAME_ERROR,"data":""}

		else:
			checkDuplicates=True
			if edit:
				if data[0]==self.currentListConfig["id"]:
					checkDuplicates=False

			if checkDuplicates:		
				for item in self.listsConfig:
					if self.listsConfig[item]["id"]==data[0]:
						return {"result":False,"code":GuardManager.LIST_NAME_DUPLICATE,"data":""}

			if loadedFile !=None:
				if os.path.getsize(loadedFile)>self.limitFileSize:
					return {'result':False,'code':GuardManager.EDIT_FILE_SIZE_OFF_LIMITS_ERROR,'data':''}			

		return {"result":True,"code":GuardManager.ALL_CORRECT_CODE}			
			 			
	#def checkData
	
	def getListId(self,name):

		listId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		listId=listId.lower().replace(" ","_")
		listId=re.sub('[^\w\s-]', '', listId).strip()
		listId=re.sub('[-\s]+', '-', listId)

		return listId

	#def getListId

	def _getOrderList(self,info=None):

		tmp=[]
		orderList=[]

		if info==None:
			if len(self.listsConfig)>0:
				for item in self.listsConfig:
					name=self.listsConfig[item]["name"].lower()
					x=()
					x=item,name
					tmp.append(x)
		else:
			for item in info:
				name=self.listsConfig[item]["name"].lower()
				x=()
				x=item,name
				tmp.append(x)
			
		tmp.sort(key=lambda list:list[1])
		for	item in tmp:
			orderList.append(item[0])

		return orderList

	#def _getOrderList		


	def applyChanges(self):

		listToRemove=[]
		listToActive=[]
		listToDeactive=[]
		self.tmpFileList=[]
		error=False
		code=""
		data=""

		if len(self.listsConfigOrig)==0:
			changes=self.listsConfig.keys()
		else:	
			changes=diff(self.listsConfigOrig,self.listsConfig).keys()

		if len(changes)>0:
			for item in self.listsConfig:
				if item in changes:	
					if self.listsConfig[item]["remove"]:
						listToRemove.append(self.listsConfig[item]["id"])
						continue

							
					if self.listsConfig[item]["active"]:
						if self.listsConfig[item]["tmpfile"]!="":
							if self.is_client:
								send=self.sendTmpFileToServer(self.listsConfig[item]["tmpfile"])
									
						listToActive.append(self.listsConfig[item])
									
									
					if not self.listsConfig[item]["active"]:
						if self.listsConfig[item]["tmpfile"]!="":
							if self.is_client:
								send=self.sendTmpFileToServer(self.listsConfig[item]["tmpfile"])
								
						listToDeactive.append(self.listsConfig[item])

					if self.listsConfig[item]["replaced_to"]!="":
						origName=self.listsConfig[item]["replaced_to"]
						listToRemove.append(origName)
			
			if len(listToRemove)>0:
				resultRemove=self.client.LliurexGuardManager.remove_guardmode_list(listToRemove)	
				msg="Applied Changes.Removed list "
				self._debug(msg,resultRemove)
				msgLog=msg+str(resultRemove)+". List removed: "+str(listToRemove)
				self.writeLog(msgLog)
				if not resultRemove['status']:
					error=True
					code=GuardManager.REMOVING_LIST_ERROR
					data=resultRemove['data']

			if not error:
				if len(listToActive)>0:
						resultActive=self.client.LliurexGuardManager.activate_guardmode_list(listToActive)	
						msg="Applied Changes.Actived list "
						self._debug(msg,resultActive)
						msgLog=msg+str(resultActive)+". List actived: "+str(listToActive)
						self.writeLog(msgLog)

						if not resultActive['status']:
							error=True
							code=GuardManager.ACTIVATING_LIST_ERROR
							data=resultActive['data']

				if not error:
					if len(listToDeactive)>0:
						resultDeactive=self.client.LliurexGuardManager.deactivate_guardmode_list(listToDeactive)	
						msg="Applied Changes.Deactived lists "
						self._debug(msg,resultDeactive)
						msgLog=msg+str(resultDeactive)+". List deactived: "+str(listToDeactive)
						self.writeLog(msgLog)
						if not resultDeactive['status']:
							error=True
							code=GuardManager.DEACTIVATING_LIST_ERROR
							data=resultDeactive['data']

			if not error:
				msg="Lliurex Guard applied changes. Dnsmasq restart"
				restartDnsmasq=self.restartDnsmasq(msg)
				if restartDnsmasq['status']:
					return {'status':True,'code':GuardManager.CHANGES_APPLIED_SUCCESSFUL}
				else:
					return {'status':False,'code':GuardManager.RESTARTING_DNSMASQ_ERROR,'data':restartDnsmasq['data']}
			else:
				return {'status':False,'code':code,'data':data}									

		else:
			return {'status':True,'code':GuardManager.ALL_CORRECT_CODE}						

	#def applyChanges

	def restartDnsmasq(self,msg):

		restartDnsmasq=self.client.LliurexGuardManager.restart_dnsmasq()
		self.connection=False
		self.timeout=120
		self.count=0

		while not self.connection:
			time.sleep(1)
			try:
				if self.is_server or self.is_client:
					res=urllib.request.urlopen("http://%s"%self.server_ip)
				self.connection=True
			except Exception as e:
				if self.count<self.timeout:
					self.count+=1
				else:
					msgLog="Lliurex Guard checking connection with server. Time Out. Error:%s"%str(e)
					self.writeLog(msgLog)
					self.connection=True

		#self.set_server(self.server_ip)	
		self.client=n4d.client.Client(ticket=self.tk)
		self._debug(msg,restartDnsmasq)
		msgLog=msg+str(restartDnsmasq)
		self.writeLog(msgLog)
		
		return restartDnsmasq				

	#def restartDnsmasq()	

	def sendTmpFileToServer(self,tmp_file):

		send_tmpfile=self.localClient.ScpManager.send_file(self.credentials[0],self.credentials[1],"server",tmp_file,"/tmp")
		msgLog="Send tmp file %s to server"%tmp_file+ " "+str(send_tmpfile)	
		self.writeLog(msgLog)
		
		return send_tmpfile

	#def sendTmpFileToServer		

	def _createTmpFile(self,listId):
	
		tmpFile=tempfile.mkstemp("_"+listId)
		tmpFile=tmpFile[1]
		
		return tmpFile

	#def _createTmpFile	

	def remove_tmp_file(self):

		'''
		if "client" in self.flavours:
			for item in self.tmpFileList:
				if os.path.exists(item):
					os.remove(item)
		'''
		for item in self.garbageFiles:
			if os.path.exists(item):
				os.remove(item)
		
		self.garbageFiles=[]	

		self.client.LliurexGuardManager.remove_tmp_file()			

		
	#def _remove_tmp_file	

	def writeLog(self,msg):
	
		syslog.openlog("LLIUREX-GUARD")
		syslog.syslog(msg)	

	#def writeLog	

	def formatLine(self,line):

		if line!="":
			firstchar=line[0]
			
			if firstchar in [".","_","-","+","*","$"," ","&","!","¡","#","%","?","¿"]:
				line=line[1:]
			
			if "https" in line:
				line=line.replace("https://","")
			else:
				line=line.replace("http://","")

			if len(line.strip().split("/"))>1:
				line=""
		
		return line

	#def formatLine

	def updateListDns(self):

		status=True
		errorInfo=[]
		code=""
		for item in self.listsConfig:
			readGuardmodeList=self.client.LliurexGuardManager.read_guardmode_list(self.listsConfig[item]["id"],self.listsConfig[item]['active'])
			if readGuardmodeList['status']:
				content=readGuardmodeList['data'][0]
				countLines=readGuardmodeList['data'][1]
				tmpFile=self._createTmpFile(self.listsConfig[item]["id"])
				f=open(tmpFile,'w')
				tmpContent="".join(content)
				f.write(tmpContent)
				f.close()
				tmpContent=None
				self.garbageFiles.append(tmpFile)
				self.listsConfig[item]["tmpfile"]=tmpFile

			else:
				status=False
				code=GuardManager.READ_FILE_ERROR
				errorInfo=readGuardmodeList['data']
				break

		if status:
			code=GuardManager.READ_FILE_SUCCESSFUL
			result=""
		else:
			result=errorInfo

		return {'status':status,'code':code,'data':result}
		
	#def updateListDns

	def checkGlobalOptionStatus(self):

		if len(self.listsConfig)>0 and self.guardMode!="DisableMode":
			return True
		else:
			return False
			
	#def checkGlobalOptionStatus

	def checkUpdateDnsOptionStatus(self):

		if self.guardMode=="WhiteMode" and self.is_desktop:
			return True
		else:
			return False

	#def checkUpdateDnsOptionStatus	

	def checkChangeStatusListsOption(self):

		allActivated=False
		allDeactivated=False
		enableStatusFilter=True
		countActivated=0
		countDeactivated=0
		result=[]
		if len(self.listsConfig)>0:
			for item in self.listsConfig:
				if self.listsConfig[item]['active']:
					countActivated+=1
				else:
					countDeactivated+=1

			if countActivated==0:
				allDeactivated=True
				enableStatusFilter=False

			if countDeactivated==0:
				allActivated=True
				enableStatusFilter=False
		else:
			enableStatusFilter=False
			
		result=[allActivated,allDeactivated,enableStatusFilter]

		return result

	#def checkChangeStatusListsOption

	def checkRemoveListsOption(self):

		for item in self.listsConfig:
			if not self.listsConfig[item]["remove"]:
				return True
		return False

	#def checkRemoveListsOption

	def getLastChangeInFile(self,fileToCheck):

		lastChange=""
		try:
			if os.path.exists(fileToCheck):
				lastChange=os.path.getmtime(fileToCheck)
		except:
			pass

		return lastChange

	#def getLastChangeInFile

#class GuardManager
