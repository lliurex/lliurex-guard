from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex,QProcess
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from pathlib import Path
from . import UrlModel

WAITING_LOADING_LIST_CODE=11
WAITING_OPEN_FILE_CODE=6
WAITING_SAVE_CHANGES=26
DUPLICATES_ENTRIES_CODE=-32
DUPLICATE_URL_CODE=-33
DUPLICATES_INCORRECT_CODE=-36
INCORRECT_ENTRIES_CODE=-37
INCORRECT_URL_CODE=-38


class AddList(QThread):

	listAdded=Signal(dict)

	def __init__(self,manager,fileToLoad):

		super().__init__()
		self.manager=manager
		self.fileToLoad=fileToLoad

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		retFile={'status':True,'data':{},'errorInfo':""}
		ret=self.manager.initValues()
		if self.fileToLoad!="":
			retFile=self.manager.loadFile(self.fileToLoad)
		
		self.listAdded.emit(retFile)
	
	#def run

#class AddList

class LoadList(QThread):

	listLoaded=Signal(dict)

	def __init__(self,manager,listToLoad):

		super().__init__()
		self.manager=manager
		self.listToLoad=listToLoad

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		ret=self.manager.initValues()
		retLoad=self.manager.loadListConfig(self.listToLoad)
		self.listLoaded.emit(retLoad)

	#def run

#class LoadList

class OpenListFile(QThread):

	fileClosed=Signal()
	def __init__(self,manager,fileToLoad):

		super().__init__()
		self.manager=manager
		self.fileToLoad=Path(fileToLoad).resolve()

	#def __init__

	def run(self,):

		if self.fileToLoad.exists():
			process=QProcess()
			process.start("kate",["-b",self.fileToLoad.as_posix()])
			process.waitForFinished(-1)

		self.fileClosed.emit()

	#def run

#class OpenListFile

class CheckListChanges(QThread):

	changesListChecked=Signal(dict)

	def __init__(self,manager,dataToCheck,edit,fileToCheck):

		super().__init__()
		self.manager=manager
		self.dataToCheck=dataToCheck
		self.edit=edit
		self.fileToCheck=fileToCheck

	#def __init__

	def run(self,*args):

		ret=self.manager.checkData(self.dataToCheck,self.edit,self.fileToCheck)
		self.changesListChecked.emit(ret)

	#def run

#class CheckListChanges

class SaveChanges(QThread):

	changesSaved=Signal(dict)

	def __init__(self,manager,dataToSave,edit,fileToSave):

		super().__init__()
		self.manager=manager
		self.dataToSave=dataToSave
		self.edit=edit
		self.fileToSave=fileToSave

	#def __init__

	def run(self,*args):

		ret=self.manager.saveConf(self.dataToSave,self.edit,self.fileToSave)

		self.changesSaved.emit(ret)

	#def run

#class SaveChanges

class Bridge(QObject):

	listNameChanged=Signal()
	listDescriptionChanged=Signal()
	showListFormMessageChanged=Signal()
	listCurrentOptionChanged=Signal()
	arePendingChangesInListChanged=Signal()
	enableFormChanged=Signal()
	showChangesInListDialogChanged=Signal()
	showUrlsListChanged=Signal()
	enableUrlEditionChanged=Signal()
	
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		self.guardManager=self.core.guardManager
		self._urlModel=UrlModel.UrlModel()
		self._listName=self.guardManager.listName
		self._listDescription=self.guardManager.listDescription
		self._showListFormMessage={"show":False,"msgCode":"","type":""}
		self._arePendingChangesInList=False
		self.changesInHeaders=False
		self.changesInContent=False
		self._listCurrentOption=0
		self._showUrlsList=False
		self._enableForm=False
		self._showChangesInListDialog=False
		self._enableUrlEdition=False
		self.lastUrlId=0

	#def _init__

	@Property(str,notify=listNameChanged)
	def listName(self):

		return self._listName

	#def listName

	@listName.setter
	def listName(self,listName):

		if self._listName!=listName:
			self._listName=listName
			self.listNameChanged.emit()

	#def listName
	
	@Property(str,notify=listDescriptionChanged)
	def listDescription(self):

		return self._listDescription

	#def listDescription

	@listDescription.setter
	def listDescription(self,listDescription):

		if self._listDescription!=listDescription:
			self._listDescription=listDescription
			self.listDescriptionChanged.emit()

	#def listDescription
	
	@Property('QVariant',notify=showListFormMessageChanged)
	def showListFormMessage(self):

		return self._showListFormMessage

	#def showListFormMessage

	@showListFormMessage.setter
	def showListFormMessage(self,showListFormMessage):

		if self._showListFormMessage!=showListFormMessage:
			self._showListFormMessage=showListFormMessage
			self.showListFormMessageChanged.emit()

	#def showListFormMessage

	@Property(int,notify=listCurrentOptionChanged)
	def listCurrentOption(self):

		return self._listCurrentOption

	#def listCurrentOption

	@listCurrentOption.setter
	def listCurrentOption(self,listCurrentOption):

		if self._listCurrentOption!=listCurrentOption:
			self._listCurrentOption=listCurrentOption
			self.listCurrentOptionChanged.emit()

	#def listCurrentOption

	@Property(bool,notify=arePendingChangesInListChanged)
	def arePendingChangesInList(self):

		return self._arePendingChangesInList

	#def arePendingChangesInList

	@arePendingChangesInList.setter
	def arePendingChangesInList(self,arePendingChangesInList):

		if self._arePendingChangesInList!=arePendingChangesInList:
			self._arePendingChangesInList=arePendingChangesInList
			self.arePendingChangesInListChanged.emit()

	#def arePendingChangesInList

	@Property(bool,notify=enableFormChanged)
	def enableForm(self):

		return self._enableForm

	#def enableForm

	@enableForm.setter
	def enableForm(self,enableForm):

		if self._enableForm!=enableForm:
			self._enableForm=enableForm
			self.enableFormChanged.emit()

	#def _setEnableForm

	@Property(bool,notify=showChangesInListDialogChanged)
	def showChangesInListDialog(self):

		return self._showChangesInListDialog

	#def showChangesInListDialog

	@showChangesInListDialog.setter
	def showChangesInListDialog(self,showChangesInListDialog):

		if self._showChangesInListDialog!=showChangesInListDialog:
			self._showChangesInListDialog=showChangesInListDialog
			self.showChangesInListDialogChanged.emit()

	#def showChangesInListDialog	

	@Property(bool,notify=showUrlsListChanged)
	def showUrlsList(self):

		return self._showUrlsList

	#def showUrlsList

	@showUrlsList.setter
	def showUrlsList(self,showUrlsList):

		if self._showUrlsList!=showUrlsList:
			self._showUrlsList=showUrlsList
			self.showUrlsListChanged.emit()

	#def showUrlsList

	@Property(bool,notify=enableUrlEditionChanged)
	def enableUrlEdition(self):

		return self._enableUrlEdition

	#def enableUrlEdition

	@enableUrlEdition.setter
	def enableUrlEdition(self,enableUrlEdition):

		if self._enableUrlEdition!=enableUrlEdition:
			self._enableUrlEdition=enableUrlEdition
			self.enableUrlEditionChanged.emit()

	#def enableUrlEdition

	def _getUrlModel(self):

		return self._urlModel

	#def _getUrlModel

	def updateUrlModel(self):

		ret=self._urlModel.clear()
		urlEntries=self.contentOfList
		self.lastUrlId=self.guardManager.getLastUrlId()+1
		for item in urlEntries:
			if item["url"]!="":
				self._urlModel.appendRow(item["urlId"],item["url"])
	
	#def updateUrlModel

	def _initializeVars(self):

		self.listName=self.guardManager.listName
		self.listDescription=self.guardManager.listDescription
		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		self.arePendingChangesInList=False
		self.changesInHeaders=False
		self.changesInContent=False
		self.fileToLoad=None
		self.enableForm=False
		self.lastChangeFromFile=""
		self.listCurrentOption=0
		self.showChangesInListDialog=False
		self.lastUrlId=0
		self.contentOfList=copy.deepcopy(self.guardManager.urlConfigData)
		self._urlModel.clear()

	#def _initializeVars

	@Slot()
	def goHome(self):

		if not self.arePendingChangesInList:
			self.listCurrentOption=0
			self.core.mainStack.moveToStack=1
			self.core.mainStack.closeGui=True
			self.core.mainStack.manageGoToStack()
		else:
			self.showChangesInListDialog=True
			self.core.mainStack.moveToStack=""

	#def goHome

	@Slot(str)
	def addNewList(self,fileToLoad=""):

		self.core.mainStack.closeGui=False
		self.core.mainStack.showPopUp={"show":True,"msgCode":WAITING_LOADING_LIST_CODE}
		self.core.guardOptionsStack.showMainMessage={"show":False,"msgCode":"","type":"","data":""}
		self.edit=False
		self.newListT=AddList(self.guardManager,fileToLoad)
		self.newListT.start()
		self.newListT.listAdded.connect(self._newListRet)
		self.newListT.finished.connect(self.newListT.deleteLater)

	#def addNewList

	@Slot(dict)
	def _newListRet(self,ret):

		self.core.mainStack.showPopUp={"show":False,"msgCode":""}

		if not ret.get('status'):
			self.core.mainStack.closeGui=True
			self.core.guardOptionsStack.showMainMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type"),"data":ret.get("errorInfo")}
			return
		
		self.currentListConfig=copy.deepcopy(self.guardManager.currentListConfig)
		self.contentOfList=copy.deepcopy(self.guardManager.urlConfigData)
		self._initializeVars()
		if not ret.get("data").get("limitLines"):
			self.showUrlsList=True
			self.updateUrlModel()
		else:
			self.fileToLoad=ret.get("data").get("tmpFile")
			self.lastChangeFromFile=self.guardManager.getLastChangeInFile(self.fileToLoad)
			self.showUrlsList=False

		self.core.mainStack.currentStack=2
		self.listCurrentOption=1
		self.enableForm=True

	#def _newListRet

	@Slot(int)
	def loadList(self,listToLoad):
		
		self.core.mainStack.closeGui=False
		self.core.mainStack.showPopUp={"show":True,"msgCode":WAITING_LOADING_LIST_CODE}
		self.core.guardOptionsStack.showMainMessage={"show":False,"msgCode":"","type":"","data":""}
		self.edit=True
		self.editListT=LoadList(self.guardManager,listToLoad)
		self.editListT.start()
		self.editListT.listLoaded.connect(self._loadListRet)
		self.editListT.finished.connect(self.editListT.deleteLater)

	#def loadList

	@Slot(dict)
	def _loadListRet(self,ret):

		self.core.mainStack.showPopUp={"show":False,"msgCode":""}
		if not ret.get("status"):
			self.core.guardOptionsStack.showMainMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type"),"data":ret.get("errorInfo")}

		self.currentListConfig=copy.deepcopy(self.guardManager.currentListConfig)
		self.contentOfList=copy.deepcopy(self.guardManager.urlConfigData)
		self._initializeVars()
		tmpFile=ret.get("data").get("tmpFile")
		if tmpFile=="":
			self.updateUrlModel()
			self.showUrlsList=True
		else:
			self.fileToLoad=tmpFile
			self.lastChangeFromFile=self.guardManager.getLastChangeInFile(self.fileToLoad)
			self.showUrlsList=False
		
		self.core.mainStack.currentStack=2
		self.listCurrentOption=1
		self.enableForm=True

	#def _loadListRet

	@Slot()
	def openListFile(self):

		self.showListFormMessage={"show":True,"msgCode":WAITING_OPEN_FILE_CODE,"type":self.guardManager.KIRIGAMI_MSG_INFO}
		self.core.mainStack.closeGui=False
		self.enableForm=False
		self.openFileT=OpenListFile(self.guardManager,self.fileToLoad)
		self.openFileT.start()
		self.openFileT.fileClosed.connect(self._openFileRet)
		self.openFileT.finished.connect(self.openFileT.deleteLater)

	#def openListFile

	@Slot()
	def _openFileRet(self):

		self.core.mainStack.closeGui=True
		self.showListFormMessage={"show":False,"msgCode":"","msgType":""}
		self.enableForm=True
		lastChangeFromFile=self.guardManager.getLastChangeInFile(self.fileToLoad)

		if lastChangeFromFile!=self.lastChangeFromFile:
			self.changesInContent=True
			self.arePendingChangesInList=True
			self.lastChangeFromFile=lastChangeFromFile
		else:
			if not self.changesInHeaders:
				self.changesInContent=False
				self.arePendingChangesInList=False

	#def _openFileRet

	@Slot(str)
	def updateListName(self,listName):

		if listName!=self.listName:
			self.listName=listName
			self.currentListConfig["id"]=self.guardManager.getListId(listName)
			self.currentListConfig["name"]=self.listName

		if self.currentListConfig!=self.guardManager.currentListConfig:
			self.changesInHeaders=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInContent:
				self.changesInHeaders=False
				self.arePendingChangesInList=False

	#def updateListName

	@Slot(str)
	def updateListDescription(self,listDescription):

		if listDescription!=self.listDescription:
			self.listDescription=listDescription
			self.currentListConfig["description"]=self.listDescription

		if self.currentListConfig!=self.guardManager.currentListConfig:
			self.changesInHeaders=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInContent:
				self.changesInHeaders=False
				self.arePendingChangesInList=False

	#def updateListDescription

	@Slot(str)
	def addNewUrl(self,urlToAdd):

		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		tmpNewUrl=urlToAdd.split(" ")
		countDuplicate=0
		countError=0
		msgCode=""
		self.lastUrlId=self.lastUrlId+1

		for item in tmpNewUrl:
			item=self.guardManager.formatLine(item)
			if item!="":
				self.lastUrlId+=1
				if not self.guardManager.checkUrlDuplicates(item,self.contentOfList):
					urlId=self.lastUrlId
					self._urlModel.appendRow(urlId,item)
					tmp={}
					tmp["urlId"]=urlId
					tmp["url"]=item
					self.contentOfList.append(tmp)
				else:
					countDuplicate+=1
			else:
				countError+=1

		if self.contentOfList!= self.guardManager.urlConfigData:
			self.changesInContent=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInHeaders:
				self.arePendingChangesInList=False
				self.changesInContent=False

		if countError >0 and countDuplicate>0:
			msgCode=DUPLICATES_INCORRECT_CODE
		elif countDuplicate>0:
			msgCode=DUPLICATES_ENTRIES_CODE
		elif countError>0:
			msgCode=INCORRECT_ENTRIES_CODE
		
		if msgCode:
			self.showListFormMessage={"show":True,"msgCode":msgCode,"type":self.guardManager.KIRIGAMI_MSG_WARNING}	
 
	#def AddNewUrl
	@Slot('QJSValue')
	def manageEditUrlBtn(self,oldValue):

		if hasattr(oldValue,'toVariant'):
			oldValue=oldValue.toVariant()

		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		self.enableUrlEdition=True
		self.urlToEditIndex=oldValue.get("urlIndex")
		self.urlToEditValue=oldValue.get("urlValue")

	#def manageEditUrlBtn

	@Slot(str)
	def editUrl(self,newValue):

		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		self.enableUrlEdition=False

		tmpNewUrl=newValue.split(" ")[0]
		tmpNewUrl=self.guardManager.formatLine(tmpNewUrl)
		if tmpNewUrl=="":
			self.showListFormMessage={"show":True,"msgCode":INCORRECT_URL_CODE,"type":self.guardManager.KIRIGAMI_MSG_WARNING}
			return

		if self.guardManager.checkUrlDuplicates(tmpNewUrl,self.contentOfList):
			self.showListFormMessage={"show":True,"msgCode":DUPLICATE_URL_CODE,"type":self.guardManager.KIRIGAMI_MSG_WARNING} 
			return

		index=self._urlModel.index(self.urlToEditIndex)
		self._urlModel.setData(index,"url",tmpNewUrl)
		
		for item in self.contentOfList:
			if item["url"]==self.urlToEditValue:
				item["url"]=tmpNewUrl
				break;
		
		if self.contentOfList!=self.guardManager.urlConfigData:
			self.changesInContent=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInHeaders:
				self.arePendingChangesInList=False
				self.changesInContent=False 

	#def editUrl

	@Slot()
	def cancelUrlEdition(self):

		self.enableUrlEdition=False
	
	#def cancelUrlEdition

	@Slot(int)
	def removeUrl(self,urlToRemove):

		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		tmpId=self._urlModel._entries[urlToRemove]["urlId"]
		self._urlModel.removeRow(urlToRemove)

		for i in range(len(self.contentOfList)-1,-1,-1):
			if tmpId==self.contentOfList[i]["urlId"]:
				self.contentOfList.pop(i)

		if self.contentOfList!=self.guardManager.urlConfigData:
			self.changesInContent=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInHeaders:
				self.arePendingChangesInList=False
				self.changesInContent=False 

	#def removeUrl

	@Slot(str)
	def manageEmptyListDialog(self,response):
		
		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		
		if response=="Apply":
			self._urlModel.clear()
			self.contentOfList=[]

			if self.contentOfList!=self.guardManager.urlConfigData:
				self.changesInContent=True
				self.arePendingChangesInList=True
			else:
				if not self.changesInHeaders:
					self.arePendingChangesInList=False
					self.changesInContent=False 	

	#def manageEmptyListDialog

	@Slot(str)
	def manageChangesInListDialog(self,response):

		self.showChangesInListDialog=False

		if response=="Apply":
			self.saveListChanges()
		elif response=="Discard":
			self.arePendingChangesInList=False
			self.core.mainStack.closeGui=True
			self.core.mainStack.moveToStack=1
			self.core.mainStack.manageGoToStack()

	#def manageChangesInListDialog

	@Slot() 
	def saveListChanges(self):

		self.showListFormMessage={"show":False,"msgCode":"","type":""}
		self.core.mainStack.showPopUp={"show":True,"msgCode":WAITING_SAVE_CHANGES}
		dataToCheck={
			"listId":self.currentListConfig["id"],
			"name": self.currentListConfig["name"],
			"content":len(self.contentOfList)
		}
		self.checkListChangesT=CheckListChanges(self.guardManager,dataToCheck,self.edit,self.fileToLoad)
		self.checkListChangesT.start()
		self.checkListChangesT.changesListChecked.connect(self._checkListChangesRet)
		self.checkListChangesT.finished.connect(self.checkListChangesT.deleteLater)

	#def saveListChanges

	@Slot(dict)
	def _checkListChangesRet(self,ret):

		if not ret.get("status"):
			self.core.mainStack.showPopUp={"show":False,"msgCode":""}
			self.showListFormMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type")}	
			return

		self.guardManager.urlConfigData=self.contentOfList
		self.saveChangesT=SaveChanges(self.guardManager,self.currentListConfig,self.edit,self.fileToLoad)
		self.saveChangesT.start()
		self.saveChangesT.changesSaved.connect(self._saveChangesRet)
		self.saveChangesT.finished.connect(self.saveChangesT.deleteLater)

	#def _checkListChangesRet

	@Slot(dict)
	def _saveChangesRet(self,ret):

		if ret.get("status"):
			self.core.guardOptionsStack._updateListsModel()
			self.core.guardOptionsStack.arePendingChanges=True
	
		self.core.guardOptionsStack.showMainMessage={"show":True,"msgCode":ret.get("code"),"type":ret.get("type"),"data":ret.get("data")}
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}
		self.arePendingChangesInList=False
		self.core.mainStack.closeGui=True
		self.core.mainStack.moveToStack=1
		self.core.mainStack.manageGoToStack()
		self.listCurrentOption=0
		self.core.guardOptionsStack.manageGlobalOptions()

	#def _saveChangesRet

	@Slot()
	def cancelListChanges(self):

		self._cancelListChanges()

	#def cancelListChanges

	def _cancelListChanges(self):

		self.arePendingChangesInList=False
		self.core.mainStack.closeGui=True
		self.core.mainStack.moveToStack=1
		self.core.mainStack.manageGoToStack()

	#def _cancelBellChanges
		
	urlModel=Property(QObject,_getUrlModel,constant=True)

#class Bridge

from . import Core


