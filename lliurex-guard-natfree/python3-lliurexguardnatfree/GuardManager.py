#!/usr/bin/env python3

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
from pathlib import Path
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

	KIRIGAMI_MSG_OK=0
	KIRIGAMI_MSG_ERROR=1
	KIRIGAMI_MSG_WARNING=2
	KIRIGAMI_MSG_INFO=3

	def __init__(self):

		super(GuardManager, self).__init__()

		self.dbg=1
		self.userValidated=True
		self.limitLines=5
		self.limitFileSize=28000000
		self.garbageFiles=[]
		self.credentials=[]
		self.guardMode="DisableMode"
		self.listsConfig={}
		self.listsConfigOrig={}
		self.listsConfigData=[]
		self.urlConfigData=[]
		self.detectFlavour()
		self.initValues()
	
	#def __init__	
			
	def detectFlavour(self):
		
		self.is_server=""

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]

		for item in flavours:
			if 'adi' in item or "lab" in item:
				self.is_server=True
				break
	
	#def detect_flavour
	
	def createN4dClient(self,ticket):

		ticket=ticket.replace('##U+0020##',' ')
		tk=n4d.client.Ticket(ticket)
		self.client=n4d.client.Client(ticket=tk,timeout=120)

		msgLog=f'Session user: {os.environ["USER"]}'
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
		self.currentListConfig={
			"id":"",
			"name":"",
			"description":""
		}
		self.urlConfigData=[]
		
	#def initValues

	def readGuardmode(self):

		response = self.client.LliurexGuardManagerNatFree.read_guardmode()
		
		msg = "Read LliureX Guard Mode: "
		self._debug(msg, response)
		self.writeLog(f"{msg}{response}")
		
		if isinstance(response, dict) and response.get('status'):
			self.guardMode = response.get('data')
			return {
				'status': True,
				'code': GuardManager.READ_GUARDMODE_SUCCESSFUL,
				'data': self.guardMode,
				'type': GuardManager.KIRIGAMI_MSG_OK
			}
		else:
			errorData = response.get('data') if isinstance(response, dict) else self.guardMode
			return {
				'status': False,
				'code': GuardManager.READ_GUARDMODE_ERROR,
				'data': errorData,
				'type': GuardManager.KIRIGAMI_MSG_ERROR
			}
	
	#def readGuardmode
	
	def changeGuardmode(self,mode):

		response=self.client.LliurexGuardManagerNatFree.change_guardmode(mode)
		
		msg=f"LliureX Guard Mode changed to {mode}"
		self._debug(msg,response)
		msgLog=f"{msg}{response}"
		self.writeLog(msgLog)

		if isinstance(response, dict) and response.get('status'):
			self.listsConfig={}
			self.listsConfigOrig={}
			self.listsConfigData=[]
			return {
				'status':True,
				'code':GuardManager.CHANGE_GUARDMODE_SUCCESSFUL,
				'type':GuardManager.KIRIGAMI_MSG_OK
			}
		else:
			errorData=response.get('data') if isinstance(response, dict) else response
			return {
				'status':False,
				'code':GuardManager.CHANGE_GUARDMODE_ERROR,
				'data':response.get('data'),
				'type':GuardManager.KIRIGAMI_MSG_ERROR
			}		
				
	#def changeGuardmode 		

	def readGuardmodeHeaders(self):

		self.listsConfig={}
		self.listsConfigOrig={}
		self.listsConfigData=[]

		response=self.client.LliurexGuardManagerNatFree.read_guardmode_headers()
		
		msg="LliureX Guard mode lists readed "
		self._debug(msg,response)
		msgLog=f"{msg}{response}"
		self.writeLog(msgLog)
		
		if isinstance(response, dict) and response.get('status'):
			self.listsConfig=response.get('data')

			if isinstance(self.listsConfig, dict):
				for item in self.listsConfig:
					if isinstance(self.listsConfig[item], dict):
						self.listsConfig[item]['remove'] = False
						self.listsConfig[item]["replaced_to"] = ""
						self.listsConfig[item]["tmpfile"] = ""			
	
			self.listsConfigOrig=copy.deepcopy(self.listsConfig)
			self._getListsConfig()

			return {
				'status':True,
				'code':GuardManager.READ_GUARDMODE_HEADERS_SUCCESSFUL,
				'data':"",
				'type':GuardManager.KIRIGAMI_MSG_OK
			}	

		else:
			errorData=response.get('data') if isinstance(response, dict) else response
			return {
				'status':False,
				'code':GuardManager.READ_GUARDMODE_HEADERS_ERROR,
				'data':errorData,
				'type':GuardManager.KIRIGAMI_MSG_ERROR
			}
		
	#def readGuardmodeHeaders

	def _getListsConfig(self):

		orderList = self._getOrderList()
		self.listsConfigData = []

		if not isinstance(orderList, (list, tuple)) or not isinstance(self.listsConfig, dict):
			return

		for item in orderList:
			configItem = self.listsConfig.get(item)
			if not isinstance(configItem, dict):
				continue

			tmp = {
				"order":item,
				"id": configItem.get("id", ""),
				"name": configItem.get("name", ""),
				"entries": configItem.get("lines", 0),
				"description": configItem.get("description", ""),
				"activated": configItem.get("active", False),
				"remove":configItem.get("remove", False),
				"metaInfo":f'{configItem.get("name", "")}{configItem.get("description", "")}'
			}

			self.listsConfigData.append(tmp)

	#def _getListsConfig

	def loadListConfig(self,listToLoad):

		self.listToLoad=str(listToLoad)
		self.currentListConfig=self.listsConfig.get(self.listToLoad)
		self.listName=self.currentListConfig.get("name")
		self.listDescription=self.currentListConfig.get("description")

		return self._readGuardModeList()

	#def loadListConfig

	def _readGuardModeList(self):

		isTmpFile = False
		status = True
		tmpFile = ""
		content = None
		result = ""
		errorInfo = ""
		countLines = 0

		listId = self.currentListConfig.get("id", "")
		active = self.currentListConfig.get("active", False)
		currentTmpfile = self.currentListConfig.get("tmpfile", "")

		if currentTmpfile != "":
			readTmpFile = self.readLocalFile(currentTmpfile, False)
			msg = f"List {listId}. Readed local file ({currentTmpfile})"
			self._debug(msg, readTmpFile)

			if isinstance(readTmpFile, dict) and readTmpFile.get('status'):
				content = readTmpFile.get('data').get("content")
				countLines = readTmpFile.get('data').get("countLines")
				isTmpFile = True
			else:
				status = False
				errorInfo = readTmpFile.get("errorInfo") if isinstance(readTmpFile, dict) else readTmpFile
		else:
			readGuardmodeList = self.client.LliurexGuardManagerNatFree.read_guardmode_list(listId, active)
			msg = f"List {listId}. Readed file"
			self._debug(msg, readGuardmodeList)

			if isinstance(readGuardmodeList, dict) and readGuardmodeList.get('status'):
				content = readGuardmodeList['data'][0]
				countLines = readGuardmodeList['data'][1]
			else:
				status = False
				errorInfo = readGuardmodeList.get('data') if isinstance(readGuardmodeList, dict) else readGuardmodeList

		if status:
			msgCode = GuardManager.READ_LIST_INFO_SUCCESSFUL
			msgType = GuardManager.KIRIGAMI_MSG_OK

			if countLines > self.limitLines:
				if not isTmpFile:
					tmpFile = self._createTmpFile(listId)
					with open(tmpFile, 'w', encoding='utf-8') as f:
						tmpContent = "".join(content)
						f.write(tmpContent)
						self.garbageFiles.append(tmpFile)
				else:
					tmpFile = readTmpFile.get('data').get("tmpFile") if isinstance(readTmpFile, dict) else ""
				contet = None
				readTmpFile=None
			else:
				self._getUrlConfig(content)
			
			msgLog = f"{msg} successfully"
			msgData={"tmpFile":tmpFile}
		else:
			msgCode = GuardManager.READ_LIST_INFO_ERROR
			msgType = GuardManager.KIRIGAMI_MSG_ERROR
			msgData = {}
			msgLog = f"{msg} with errors. Error details: {errorInfo}"

		self.writeLog(msgLog)
		return {
			'status': status, 
			'code': msgCode, 
			'data': msgData,
			'type': msgType,
			"errorInfo":errorInfo
			}

	# def _readGuardModeList

	def readLocalFile(self, filePath, createTmpfile):

		content = []
		countLines = 0

		p = Path(filePath)

		try:
			if p.exists():
				if createTmpfile:
					if p.stat().st_size > self.limitFileSize:
						return {
							'status': False,
							'code': GuardManager.LOAD_FILE_SIZE_OFF_LIMITS_ERROR,
							'data': {},
							'type':GuardManager.KIRIGAMI_MSG_ERROR
						}

				lines = p.read_text(encoding='utf-8').splitlines(keepends=True)

				for line in lines:
					if "NAME" not in line and "DESCRIPTION" not in line:
						if line.strip() != "":
							line = self.formatLine(line)
							if line != "":
								content.append(f"{line}\n")	
								countLines += 1

				lines = None
				tmpFile = str(p)

				if createTmpfile:
					if countLines == 0:
						return {
							'status': False, 
							'code': GuardManager.EMPTY_FILE_ERROR,
							'data': {},
							'type': GuardManager.KIRIGAMI_MSG_ERROR,
							"errorInfo":"Empty File"
						}
					else:	
						tmpPath = Path(self._createTmpFile(p.name))
						tmpPath.write_text("".join(content), encoding='utf-8')
						tmpFile = str(tmpPath)

						if countLines > self.limitLines:
							content = None

				self.garbageFiles.append(tmpFile)		
				
				return {
					'status': True,
					'code': GuardManager.LOAD_FILE_SUCCESSFUL,
					'data': {
						'content':content, 
						'countLines':countLines,
						'tmpFile':tmpFile
					},
					'type': GuardManager.KIRIGAMI_MSG_OK
					}
			else:
				return {
					'status': False,
					'code': GuardManager.LOADING_FILE_ERROR,
					'data': {},
					'type': GuardManager.KIRIGAMI_MSG_ERROR,
					'errorInfo':'File does not exist'

				}

		except Exception as e:
			return {
				'status': False,
				'code': GuardManager.LOADING_FILE_ERROR,
				'data': {},
				'type': GuardManager.KIRIGAMI_MSG_ERROR,
				'errorInfo':str(e)
			}

	#def readLocalFile

	def loadFile(self, fileToLoad):

		print("Cargando archivo")
		limitLines = False
		ret = self.readLocalFile(fileToLoad, True)

		if ret.get("status"):
			content= ret.get("data").get("content")
			tmpFile = ret.get("data").get("tmpFile")

			if content is not None:
				self._getUrlConfig(content)
			else:
				limitLines = True

			data = {
				'limitLines': limitLines,
				'tmpFile': tmpFile,
			}
		else:
			data = {
				'limitLines': False,
				'tmpFile': tmpFile,
			}

		return {
			'status': ret.get('status'), 
			'code': ret.get('code'), 
			'data': data,
			"errorInfo":ret.get("errorInfo", "")
		}
			
	#def loadFile

	def changeListsStatus(self, allLists, active, listToEdit):

		if allLists:
			for item in self.listsConfig:
				if isinstance(self.listsConfig[item], dict) and not self.listsConfig[item].get("remove", False):
					self.listsConfig[item]["active"] = active

		else:
			key = str(listToEdit)
			if key in self.listsConfig and isinstance(self.listsConfig[key], dict):
				self.listsConfig[key]["active"] = active
			else:
				self._debug(f"Warning: Attempted to change status of non-existing list ID: {key}")
				return 

		self._updateListsConfigData("activated", active, listToEdit)
	
	#def changeListsStatus

	def removeLists(self, allLists, listToRemove):

		if allLists:
			for item in self.listsConfig:
				if isinstance(self.listsConfig[item], dict):
					self.listsConfig[item]["remove"] = True
		else:
			key = str(listToRemove)
			if key in self.listsConfig and isinstance(self.listsConfig[key], dict):
				self.listsConfig[key]["remove"] = True
			else:
				self._debug(f"Warning: Attempted to remove non-existing list ID: {key}")
				return

		self._updateListsConfigData("remove", True, listToRemove)

	#def removeLists

	def restoreList(self, allLists, listToRestore):

		if allLists:
			for item in self.listsConfig:
				if isinstance(self.listsConfig[item], dict):
					self.listsConfig[item]["remove"] = False
		else:
			key = str(listToRestore)
			if key in self.listsConfig and isinstance(self.listsConfig[key], dict):
				self.listsConfig[key]["remove"] = False
			else:
				self._debug(f"Warning: Attempted to restore non-existing list ID: {key}")
				return

		self._updateListsConfigData("remove", False, listToRestore)

	#def restoreList

	def _updateListsConfigData(self, param, value, listToEdit):

		if listToEdit is not None:
			target_order = str(listToEdit)
			for item in self.listsConfigData:
				if item.get("order") == target_order:
					if item.get(param) != value:
						item[param] = value
						break
		else:
			for item in self.listsConfigData:
				if param in item and item[param] != value:
					if param == "remove" or not item.get("remove", False):
						item[param] = value

	#def _updateListsConfigData

	def _getUrlConfig(self, content):

		self.urlConfigData = []

		if not content:
			return

		for count, item in enumerate(content, start=1):
			if isinstance(item, str):
				cleanedUrl = item.strip()
				if cleanedUrl == "":
					continue

				tmp = {
					"urlId": count,
					"url": cleanedUrl
				}

				self.urlConfigData.append(tmp)

	#def _getUrlConfig

	def saveConf(self, listInfo, edit, fileToSave=None):

		result = {}

		list_id = listInfo.get("id", "")
		ret = self._createFileToSave(list_id, fileToSave)

		if ret.get("status"):
			if edit:
				order = str(getattr(self, 'listToLoad', ''))
				if order not in self.listsConfig:
					return {
						'status': False,
						'code': GuardManager.READ_GUARDMODE_ERROR,
						'data': f'Order key {order} not found in configuration',
						'type': GuardManager.KIRIGAMI_MSG_ERROR
					}
				msgCode = GuardManager.LIST_EDITED_SUCCESSFUL
				if self.listsConfig[order].get("id") != list_id:
					self.listsConfig[order]["replaced_to"] = self.listsConfig[order].get("id", "")
			else:
				try:
					existing_keys = [int(k) for k in self.listsConfig.keys() if k.isdigit()]
					next_order = max(existing_keys) + 1 if existing_keys else 1
				except Exception:
					next_order = len(self.listsConfig) + 1

				order = str(next_order)
				msgCode = GuardManager.LIST_CREATED_SUCCESSFUL

				self.listsConfig[order] = {
					"active": True,
					"remove": False,
					"replaced_to": ""
				}

			msgType = GuardManager.KIRIGAMI_MSG_OK
			self.listsConfig[order]["id"] = list_id
			self.listsConfig[order]["name"] = listInfo.get("name", "")
			self.listsConfig[order]["description"] = listInfo.get("description", "")
			self.listsConfig[order]["lines"] = ret.get("lines", 0)
			self.listsConfig[order]["tmpfile"] = ret.get("tmpfile", "")
			self.listsConfig[order]["edited"] = True

			self._getListsConfig()
		else:
			msgCode = ret.get("code")
			msgType = GuardManager.KIRIGAMI_MSG_ERROR

		result["status"] = ret.get("status", False)
		result["code"] = msgCode
		result["data"] = ret.get("data", "")
		result["type"]=msgType

		return result

	#def saveConf

	def _createFileToSave(self, listId, fileToSave=None):

		result = {}
		countLines = 0

		try:
			if fileToSave is None:
				tmpPath = Path(self._createTmpFile(listId))
				self.garbageFiles.append(str(tmpPath))
			else:
				tmpPath = Path(fileToSave)

			if fileToSave is not None:
				if tmpPath.exists():
					lines = tmpPath.read_text(encoding='utf-8').splitlines()
					formatContent = []

					for line in lines:
						if line.strip() != "":
							cleanedLine = self.formatLine(line)
							if cleanedLine != "":
								formatContent.append(cleanedLine + "\n")
								countLines += 1

					print(formatContent)
					tmpPath.write_text("".join(formatContent), encoding='utf-8')
				else:
					raise FileNotFoundError(f"File to save not found: {fileToSave}")
			else:
				formatContent = []
				validUrls = []

				for item in self.urlConfigData:
					urlStr = item.get("url", "")
					if urlStr != "":
						cleanedLine = self.formatLine(urlStr)
						if cleanedLine != "":
							item["url"] = cleanedLine
							formatContent.append(cleanedLine + "\n")
							countLines += 1
							validUrls.append(item)

				self.urlConfigData = validUrls

				tmpPath.write_text("".join(formatContent), encoding='utf-8')

			if countLines > 0:
				result["status"] = True
				result["code"] = GuardManager.LOAD_FILE_SUCCESSFUL
			else:
				result["status"] = False
				result["code"] = GuardManager.EMPTY_LIST_ERROR

			result["tmpfile"] = str(tmpPath)
			result["lines"] = countLines
			result["data"] = ""

		except Exception as e:
			result['status'] = False
			result['code'] = GuardManager.SAVING_FILE_ERROR
			result['data'] = str(e)

		msg = f"List {listId}. Saved changes"
		self._debug(msg, result)
		self.writeLog(f"{msg} {result}")

		return result
		
	#def _createFileToSave

	def checkData(self, data, edit, loadedFile):

		if str(data[1]).strip() == "":
			return {"status": False, "code": GuardManager.MISSING_LIST_NAME_ERROR, "data": "","type": GuardManager.KIRIGAMI_MSG_ERROR}

		checkDuplicates = True
		if edit:
			if data[0] == self.currentListConfig.get("id"):
				checkDuplicates = False

		if checkDuplicates:		
			for item in self.listsConfig:
				if isinstance(self.listsConfig[item], dict) and self.listsConfig[item].get("id") == data[0]:
					return {"status": False, "code": GuardManager.LIST_NAME_DUPLICATE, "data": "","type": GuardManager.KIRIGAMI_MSG_ERROR}

		if loadedFile is not None:
			p = Path(loadedFile)
			if p.exists():
				if p.stat().st_size > self.limitFileSize:
					return {'status': False, 'code': GuardManager.EDIT_FILE_SIZE_OFF_LIMITS_ERROR, 'data': '',"type":GuardManager.KIRIGAMI_MSG_ERROR}

				if p.stat().st_size == 0:
					return {'status': False, 'code': GuardManager.EMPTY_FILE_ERROR, 'data': '',"type": GuardManager.KIRIGAMI_MSG_ERROR}

				with p.open('r', encoding='utf-8') as fd:
					first_char = fd.read(1)
					if not first_char.strip():
						return {'status': False, 'code': GuardManager.EMPTY_FILE_ERROR, 'data': '',"type": GuardManager.KIRIGAMI_MSG_ERROR}
			else:
				return {'status': False, 'code': GuardManager.LOADING_FILE_ERROR, 'data': 'File does not exist',"type": GuardManager.KIRIGAMI_MSG_ERROR}
		else:
			if data[2] == 0:
				return {'status': False, 'code': GuardManager.EMPTY_LIST_ERROR, 'data': '',"type": GuardManager.KIRIGAMI_MSG_ERROR}			

		return {"status": True, "code": GuardManager.ALL_CORRECT_CODE, "data": "", "type": GuardManager.KIRIGAMI_MSG_OK}			
			 			
	#def checkData
	
	def getListId(self, name):

		if not isinstance(name, str):
			return ""

		listId = ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		listId = listId.lower()
		listId = re.sub(r'[^\w\s-]', '', listId)
		listId = listId.replace(" ", "_")
		listId = re.sub(r'_{2,}', '_', listId)
		listId = re.sub(r'-{2,}', '-', listId)
		
		return listId.strip('_ -')

	#def getListId

	def _getOrderList(self, info=None):

		sourceKeys = info if info is not None else self.listsConfig.keys()

		if not sourceKeys or not isinstance(self.listsConfig, dict):
			return []

		validItems = []

		for item in sourceKeys:
			configItem = self.listsConfig.get(item)
			if isinstance(configItem, dict):
				name = configItem.get("name", "").lower()
				validItems.append((item, name))

		validItems.sort(key=lambda x: x[1])

		return [item[0] for item in validItems]

	#def _getOrderList

	def applyChanges(self):

		listToRemove = []
		listToActive = []
		listToDeactive = []
		self.tmpFileList = []
		error = False
		code = GuardManager.CHANGES_APPLIED_SUCCESSFUL
		data = ""
		msgType= GuardManager.KIRIGAMI_MSG_OK

		if len(self.listsConfigOrig) == 0:
			changes = self.listsConfig.keys()
		else:
			changes = diff(self.listsConfigOrig, self.listsConfig).keys()

		if len(changes) > 0:
			for item in self.listsConfig:
				if item in changes and isinstance(self.listsConfig[item], dict):	
					if self.listsConfig[item].get("remove", False):
						listToRemove.append(self.listsConfig[item].get("id"))
						continue

					if self.listsConfig[item].get("active", False):
						listToActive.append(self.listsConfig[item])
					else:
						listToDeactive.append(self.listsConfig[item])

					replaced_to = self.listsConfig[item].get("replaced_to", "")
					if replaced_to != "":
						listToRemove.append(replaced_to)

			if len(listToRemove) > 0:
				resultRemove = self.client.LliurexGuardManagerNatFree.remove_guardmode_list(listToRemove)
				self._debug("Applied Changes. Removed list ", resultRemove)
				self.writeLog(f"Applied Changes. Removed list {resultRemove}. List removed: {listToRemove}")

				if not resultRemove.get('status', False):
					error = True
					code = GuardManager.REMOVING_LIST_ERROR
					data = resultRemove.get('data', '')
					type= GuardManager.KIRIGAMI_MSG_ERROR

			if not error and len(listToActive) > 0:
				resultActive = self.client.LliurexGuardManagerNatFree.activate_guardmode_list(listToActive)
				self._debug("Applied Changes. Actived list ", resultActive)
				self.writeLog(f"Applied Changes. Actived list {resultActive}. List actived: {listToActive}")

				if not resultActive.get('status', False):
					error = True
					code = GuardManager.ACTIVATING_LIST_ERROR
					data = resultActive.get('data', '')
					msgType = GuardManager.KIRIGAMI_MSG_ERROR

			if not error and len(listToDeactive) > 0:
				resultDeactive = self.client.LliurexGuardManagerNatFree.deactivate_guardmode_list(listToDeactive)
				self._debug("Applied Changes. Deactived lists ", resultDeactive)
				self.writeLog(f"Applied Changes. Deactived lists {resultDeactive}. List deactived: {listToDeactive}")

				if not resultDeactive.get('status', False):
					error = True
					code = GuardManager.DEACTIVATING_LIST_ERROR
					data = resultDeactive.get('data', '')
					msgType = KIRIGAMI_MSG_ERROR


			return {'status': not error, 'code': code, 'data': data, 'type': msgType}									

		else:
			return {'status': True, 'code': GuardManager.ALL_CORRECT_CODE, 'data': '', 'type': msgType}

	#def applyChanges

	def _createTmpFile(self, listId):

		fd, tmpPathStr = tempfile.mkstemp(suffix=f"_{listId}")

		os.close(fd)

		return tmpPathStr

	#def _createTmpFile
	
	def removeTmpFile(self):

		for item in self.garbageFiles:
			if not item:
				continue

			p = Path(item)
			try:
				if p.is_file():
					p.unlink()
			except Exception as e:
				self._debug(f"Warning: Could not remove temporary file {item}: {e}")
		
	#def removeTmpFile
	
	def writeLog(self,msg):
	
		syslog.openlog("LLIUREX-GUARD-NATFREE")
		syslog.syslog(msg)	

	#def writeLog	

	def formatLine(self, line):

		if not isinstance(line, str):
			return ""

		line = line.strip()
		if not line:
			return ""

		forbiddenStarts = {".", "_", "-", "+", "*", "$", " ", "&", "!", "¡", "#", "%", "?", "¿"}
		if line[0] in forbiddenStarts:
			line = line[1:].strip()
			if not line:
				return ""

		if line.startswith("https://"):
			line = line[8:]
		elif line.startswith("http://"):
			line = line[7:]

		if "/" in line:
			return ""

		sanitizeItems = ["--", ".-", "-.", "0.", ".0", "0-", "-0"]
		for item in sanitizeItems:
			if item in line:
				return ""

		return line

	#def formatLine

	def checkGlobalOptionStatus(self):

		return bool(self.listsConfig) and getattr(self, 'guardMode', '') != "DisableMode"

	#def checkGlobalOptionStatus

	def checkChangeStatusListsOption(self):

		allActivated = False
		allDeactivated = False
		enableStatusFilter = True

		totalLists = len(self.listsConfig)
		
		if totalLists == 0:
			return {
				"allActivated":False, 
				"allDesactivated":False, 
				"enableStatusFilter":False
			}

		countActivated = sum(1 for item in self.listsConfig.values() if isinstance(item, dict) and item.get('active'))
		countDeactivated = totalLists - countActivated
		countRemoved = sum(1 for item in self.listsConfig.values() if isinstance(item, dict) and item.get('remove'))

		if countActivated == 0:
			allDeactivated = True
			enableStatusFilter = False

		if countDeactivated == 0:
			allActivated = True
			enableStatusFilter = False

		if countRemoved == totalLists:
			allActivated = False
			allDeactivated = False
			enableStatusFilter = False

		return {
			"allActivated":allActivated, 
			"allDeactivated": allDeactivated, 
			"enableStatusFilter":enableStatusFilter
		}

	#def checkChangeStatusListsOption

	def checkRemoveListsOption(self):

		return any(
			isinstance(item, dict) and not item.get("remove", False) 
			for item in self.listsConfig.values()
		)

	#def checkRemoveListsOption

	def checkRestoreListsOption(self):

		return any(
			isinstance(item, dict) and item.get("remove", False) 
			for item in self.listsConfig.values()
		)

	#def checkRestoreListOption

	def getLastChangeInFile(self, fileToCheck):

		if not fileToCheck:
			return None

		try:
			p = Path(fileToCheck)
			if p.is_file():
				return p.stat().st_mtime
		except OSError as e:
			self._debug(f"Warning: Could not get modification time for {fileToCheck}: {e}")

		return None

	#def getLastChangeInFile

	def checkUrlDuplicates(self, urlToCheck, listOfUrl):

		return any(
			isinstance(item, dict) and item.get("url") == urlToCheck 
			for item in listOfUrl
		)

	#def checkUrlDuplicates

	def getLastUrlId(self):

		tmpId=[]
		for item in self.urlConfigData:
			tmpId.append(item["urlId"])

		tmpId=sorted(tmpId,reverse=True)

		if len(tmpId)>0:
			return tmpId[0]
		else:
			return 0

	#def getLastUrlId

	def getLastUrlId(self):

		if not self.urlConfigData or not isinstance(self.urlConfigData, list):
			return 0

		return max(
			(item.get("urlId", 0) for item in self.urlConfigData if isinstance(item, dict)), 
			default=0
		)

	#def getLastUrlId

#class GuardManager