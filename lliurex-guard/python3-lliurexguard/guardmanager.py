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
	EDIT_FILE_OFF_LIMITS_ERROR=-31
	LINES_TO_COPY_OFF_LIMITS_ERROR=-33
	READ_FILE_ERROR=-34
	EMPTY_LIST_ERROR=-35
	USER_NOT_VALID_ERROR=-36
	LOAD_LLIUREXGUARD_ERROR=-37

	ALL_CORRECT_CODE=0
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

		msg_log='Session user: %s Lliurex-Guard user: %s'%(os.environ["USER"],self.credentials[0])
		self.write_log(msg_log)


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
		self.currentListConfig["name"]=self.listName
		self.currentListConfig["description"]=self.listDescription
		self.urlConfigData=[]
		
	#def initValues		

	def readGuardmode(self):
			
		readGuardmode=self.client.LliurexGuardManager.read_guardmode(True)
		msg="Read LliureX Guard Mode: "
		self._debug(msg,readGuardmode)
		msgLog=msg+str(readGuardmode)
		self.write_log(msgLog)
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
		self.write_log(msgLog)
		
		if changeGuardmode['status']:
			msg="LliureX Guard Mode changed. Dnsmasq restarted "
			forceRestartDnsmasq=False
			self.listsConfig={}
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
		self.listsConfigData=[]

		readGuardmodeHeaders=self.client.LliurexGuardManager.read_guardmode_headers()
		msg="LliureX Guard mode lists readed "
		self._debug(msg,readGuardmodeHeaders)
		msgLog=msg+str(readGuardmodeHeaders)
		self.write_log(msgLog)
		if readGuardmodeHeaders['status']:
			self.listsConfig=readGuardmodeHeaders['data']
			for item in self.listsConfig:
				#tmp_list[item]['edited']=False
				self.listsConfig[item]['remove']=False
				self.listsConfig[item]["replaced_to"]=""
				self.listsConfig[item]["tmpfile"]=""

			self._getListsConfig()

			return {'status':True,'code':GuardManager.READ_GUARDMODE_HEADERS_SUCCESSFUL,'data':""}	

		else:
			return {'status':False,'code':GuardManager.READ_GUARDMODE_HEADERS_ERROR,'data':str(readGuardmodeHeaders['data'])}
		
	#def readGuardmodeHeaders

	def _getListsConfig(self):

		orderList=self._getOrderList()
		
		for item in orderList:
			tmp={}
			tmp["order"]=item
			tmp["id"]=self.listsConfig[item]["id"]
			tmp["name"]=self.listsConfig[item]["name"]
			tmp["entries"]=self.listsConfig[item]["lines"]
			tmp["description"]=self.listsConfig[item]["description"]
			tmp["activated"]=self.listsConfig[item]["active"]
			tmp["delete"]=False
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
		result=""
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
				result=tmpFile
			else:
				self._getUrlConfig(content)
				content=None	
			msg_log=msg + " successfully"
		else:
			code=GuardManager.READ_LIST_INFO_ERROR
			result=errorInfo
			msg_log=msg+ "with errors. Error details: "+str(errorInfo)
		
		self.write_log(msg_log)
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
								line=self._format_line(line)
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

	def _getUrlConfig(self,content):

		count=1
		for item in content:
			tmp={}
			tmp["id"]=count
			tmp["url"]=item.strip()
			self.urlConfigData.append(tmp)
			count+=1

	#def _getUrlConfig		

	def save_conf(self,args):

		error=False
		result={}
		info=args[0]
		content=args[1]
		count_lines=0

		try:
			if args[2]==None:
				tmp_list=self._createTmpFile(info["id"])
				self.garbageFiles.append(tmp_list)
			else:
				tmp_list=args[2]

			if content=="":
				tmp_content=[]
				f=open(tmp_list,'r')
				lines=f.readlines()
				f.close()
				f=open(tmp_list,'w')
				for line in lines:
					if line!="":
						line=self._format_line(line)
						if line!="":
							f.write(line)
							count_lines+=1
		
				f.close()		
				
			else:
				format_content=[]	
				content=content.split("\n")	
				for line in content:
					if line !="":
						line=self._format_line(line)
						if line!="":
							format_content.append(line+"\n")
							count_lines+=1	
				f=open(tmp_list,"w")
				f.write("".join(format_content))
				f.close()
			content=None
			format_content=None
			if count_lines>0:
				result["status"]=True
			else:
				result["status"]=False
				result["code"]=GuardManager.EMPTY_LIST_ERROR
			result["tmpfile"]=tmp_list
			result["lines"]=count_lines
			result["data"]=""
			
		except Exception as e:
			result['status']=False
			result['code']=GuardManager.SAVING_FILE_ERROR
			result['data']=str(e)
		
		msg="List %s. Saved changes "%info["id"]
		self._debug(msg,result)
		msg_log=msg+" "+str(result)	
		self.write_log(msg_log)

		return result
			

			
	#def save_conf		

	def check_data(self,list_data,data,edit,loaded_file,orig_id=None):

		if data["name"]=="":
			return {"result":False,"code":GuardManager.MISSING_LIST_NAME_ERROR,"data":""}

		else:
			check_duplicates=True
			if edit:
				if data["id"]==orig_id:
					check_duplicates=False

			if check_duplicates:		
				for item in list_data:
					if list_data[item]["id"]==data["id"]:
						return {"result":False,"code":GuardManager.LIST_NAME_DUPLICATE,"data":""}

			if loaded_file !=None:
				if os.path.getsize(loaded_file)>self.limitFileSize:
					return {'result':False,'code':GuardManager.EDIT_FILE_SIZE_OFF_LIMITS_ERROR,'data':''}			

		return {"result":True,"code":GuardManager.ALL_CORRECT_CODE}			
			 			
	#def check_data
	
	def get_listId(self,name):

		listId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		listId=listId.lower().replace(" ","_")
		listId=re.sub('[^\w\s-]', '', listId).strip()
		listId=re.sub('[-\s]+', '-', listId)

		return listId

	#def get_siteId

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


	def apply_changes(self,list_data,orig_data):

		list_to_remove=[]
		list_to_active=[]
		list_to_deactive=[]
		self.tmpfile_list=[]
		error=False
		code=""
		data=""

		if len(orig_data)==0:
			changes=list_data.keys()
		else:	
			changes=diff(orig_data,list_data).keys()

		if len(changes)>0:
			for item in list_data:
				if item in changes:	
					if list_data[item]["remove"]:
						list_to_remove.append(list_data[item]["id"])
						continue

							
					if list_data[item]["active"]:
						if list_data[item]["tmpfile"]!="":
							#self.tmpfile_list.append(list_data[item]["tmpfile"])
							if self.is_client:
								send=self.send_tmpfile_toserver(list_data[item]["tmpfile"])
									
						list_to_active.append(list_data[item])
									
									
					if not list_data[item]["active"]:
						if list_data[item]["tmpfile"]!="":
							#self.tmpfile_list.append(list_data[item]["tmpfile"])
							if self.is_client:
								send=self.send_tmpfile_toserver(list_data[item]["tmpfile"])
								
						list_to_deactive.append(list_data[item])

					if list_data[item]["replaced_to"]!="":
						orig_name=list_data[item]["replaced_to"]
						list_to_remove.append(orig_name)
			
			if len(list_to_remove)>0:
				result_remove=self.client.LliurexGuardManager.remove_guardmode_list(list_to_remove)	
				msg="Applied Changes.Removed list "
				self._debug(msg,result_remove)
				msg_log=msg+str(result_remove)+". List removed: "+str(list_to_remove)
				self.write_log(msg_log)
				if not result_remove['status']:
					error=True
					code=GuardManager.REMOVING_LIST_ERROR
					data=result_remove['data']

			if not error:
				if len(list_to_active)>0:
						result_active=self.client.LliurexGuardManager.activate_guardmode_list(list_to_active)	
						msg="Applied Changes.Actived list "
						self._debug(msg,result_active)
						msg_log=msg+str(result_active)+". List actived: "+str(list_to_active)
						self.write_log(msg_log)

						if not result_active['status']:
							error=True
							code=GuardManager.ACTIVATING_LIST_ERROR
							data=result_active['data']

				if not error:
					if len(list_to_deactive)>0:
						result_deactive=self.client.LliurexGuardManager.deactivate_guardmode_list(list_to_deactive)	
						msg="Applied Changes.Deactived lists "
						self._debug(msg,result_deactive)
						msg_log=msg+str(result_deactive)+". List deactived: "+str(list_to_deactive)
						self.write_log(msg_log)
						if not result_deactive['status']:
							error=True
							code=GuardManager.DEACTIVATING_LIST_ERROR
							data=result_deactive['data']

			if not error:
				#self.remove_tmp_file(tmpfile_list)
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

	#def apply_changes

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
					msg_log="Lliurex Guard checking connection with server. Time Out. Error:%s"%str(e)
					self.write_log(msg_log)
					self.connection=True

			
		#self.set_server(self.server_ip)	
		self.client=n4d.client.Client(ticket=self.tk)
		self._debug(msg,restartDnsmasq)
		msg_log=msg+str(restartDnsmasq)
		self.write_log(msg_log)
		
		return restartDnsmasq				

	#def restartDnsmasq()	

	def send_tmpfile_toserver(self,tmp_file):

		send_tmpfile=self.localClient.ScpManager.send_file(self.credentials[0],self.credentials[1],"server",tmp_file,"/tmp")
		msg_log="Send tmp file %s to server"%tmp_file+ " "+str(send_tmpfile)	
		self.write_log(msg_log)
		
		return send_tmpfile

	#def send_tmpfile_toserver		

	def _createTmpFile(self,listId):
	
		tmpFile=tempfile.mkstemp("_"+listId)
		tmpFile=tmpFile[1]
		
		return tmpFile

	#def _createTmpFile	

	def remove_tmp_file(self):

		'''
		if "client" in self.flavours:
			for item in self.tmpfile_list:
				if os.path.exists(item):
					os.remove(item)
		'''
		for item in self.garbageFiles:
			if os.path.exists(item):
				os.remove(item)
		
		self.garbageFiles=[]	

		self.client.LliurexGuardManager.remove_tmp_file()			

		
	#def _remove_tmp_file	

	def write_log(self,msg):
	
		syslog.openlog("LLIUREX-GUARD")
		syslog.syslog(msg)	

	#def write_log	

	def _format_line(self,line):

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

	#def _format_line

	def get_clipboard_content(self):

		text_to_copy=[]
		code=""
		
		try:
			p = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
			data=p.communicate()[0]
		except Exception as e:
			print (str(e))
			data=""
	
		if type(data) is bytes:
			result=data.decode()
		else:
			result=data
		
		if result!="":	
			text=result.split("\n")
			   		
			if len(text)<=self.limitLines:
				for item in text:
					text_to_copy.append(item+"\n")
				
			else:
				count=0
				code=GuardManager.LINES_TO_COPY_OFF_LIMITS_ERROR
			
				for item in text:
					if count<2500:
						text_to_copy.append(item+"\n")
						count+=1
					else:
						break

		return {'status':True,'code':code,'data':text_to_copy} 	

	#def get_clipboard_content				

	def update_list_dns(self,list_data):

		status=True
		error_info=[]
		code=""
		for item in list_data:
			read_guardmode_list=self.client.LliurexGuardManager.read_guardmode_list(list_data[item]["id"],list_data[item]['active'])
			if read_guardmode_list['status']:
				content=read_guardmode_list['data'][0]
				count_lines=read_guardmode_list['data'][1]
				tmp_file=self._createTmpFile(list_data[item]["id"])
				f=open(tmp_file,'w')
				tmp_content="".join(content)
				f.write(tmp_content)
				f.close()
				tmp_content=None
				self.garbageFiles.append(tmp_file)
				list_data[item]["tmpfile"]=tmp_file

			else:
				status=False
				code=GuardManager.READ_FILE_ERROR
				error_info=read_guardmode_list['data']
				break

		if status:
			code=GuardManager.READ_FILE_SUCCESSFUL
			result=list_data
		else:
			result=error_info

		return {'status':status,'code':code,'data':result}
		
	#def update_list_dns

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

#class GuardManager
