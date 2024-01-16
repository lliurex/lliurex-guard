from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import UrlModel

WAITING_LOADING_LIST_CODE=11
WAITING_OPEN_FILE_CODE=6
WAITING_SAVE_CHANGES=26


class LoadList(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.newList=args[0]
		self.listInfo=args[1]
		self.ret={}

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		ret=Bridge.guardManager.initValues()
		if not self.newList:
			self.ret=Bridge.guardManager.loadListConfig(self.listInfo)

	#def run

#class LoadList

class OpenListFile(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.fileToLoad=args[0]

	#def __init__

	def run(self,*args):

		cmd="kwrite %s"%self.fileToLoad
		os.system(cmd)

	#def run

#class OpenListFile

class CheckListChanges(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.dataToCheck=args[0]
		self.edit=args[1]
		self.fileToCheck=args[2]
		self.ret={}

	#def __init__

	def run(self,*args):

		self.ret=Bridge.guardManager.checkData(self.dataToCheck,self.edit,self.fileToCheck)

	#def run

#class CheckListChanges

class SaveChanges(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.dataToSave=args[0]
		self.edit=args[1]
		self.fileToCheck=args[2]
		self.ret={}

	#def __init__

	def run(self,*args):

		self.ret=Bridge.guardManager.saveConf(self.dataToSave,self.edit,self.fileToCheck)

	#def run

#class SaveChanges


class Bridge(QObject):

	
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.guardManager=self.core.guardManager
		self._urlModel=UrlModel.UrlModel()
		self._listName=Bridge.guardManager.listName
		self._listDescription=Bridge.guardManager.listDescription
		self._showListFormMessage=[False,"","Ok"]
		self._arePendingChangesInList=False
		self.changesInHeaders=False
		self.changesInContent=False
		self._listCurrentOption=0
		self._showUrlsList=False
		self._enableForm=True
		self._showChangesInListDialog=False

	#def _init__

	def _getListName(self):

		return self._listName

	#def _getListName

	def _setListName(self,listName):

		if self._listName!=listName:
			self._listName=listName
			self.on_listName.emit()

	#def _setListName

	def _getListDescription(self):

		return self._listDescription

	#def _getListDescription

	def _setListDescription(self,listDescription):

		if self._listDescription!=listDescription:
			self._listDescription=listDescription
			self.on_listDescription.emit()

	#def _setListDescription

	def _getListCurrentOption(self):

		return self._listCurrentOption

	#def _getListCurrentOption

	def _setListCurrentOption(self,listCurrentOption):

		if self._listCurrentOption!=listCurrentOption:
			self._listCurrentOption=listCurrentOption
			self.on_listCurrentOption.emit()

	#def _setListCurrentOption

	def _getUrlModel(self):

		return self._urlModel

	#def _getUrlModel

	def _getArePendingChangesInList(self):

		return self._arePendingChangesInList

	#def _getArePendingChangesInList

	def _setArePendingChangesInList(self,arePendingChangesInList):

		if self._arePendingChangesInList!=arePendingChangesInList:
			self._arePendingChangesInList=arePendingChangesInList
			self.on_arePendingChangesInList.emit()

	#def _setArePendingChangesInList

	def _getShowListFormMessage(self):

		return self._showListFormMessage

	#def _getShowListFormMessage

	def _setShowListFormMessage(self,showListFormMessage):

		if self._showListFormMessage!=showListFormMessage:
			self._showListFormMessage=showListFormMessage
			self.on_showListFormMessage.emit()

	#def _setShowListFormMessage

	def _getShowUrlsList(self):

		return self._showUrlsList

	#def _getShowUrlsList

	def _setShowUrlsList(self,showUrlsList):

		if self._showUrlsList!=showUrlsList:
			self._showUrlsList=showUrlsList
			self.on_showUrlsList.emit()

	#def _setShowUrlsList

	def _getEnableForm(self):

		return self._enableForm

	#def _getEnableForm

	def _setEnableForm(self,enableForm):

		if self._enableForm!=enableForm:
			self._enableForm=enableForm
			self.on_enableForm.emit()

	#def _setEnableForm

	def _getShowChangesInListDialog(self):

		return self._showChangesInListDialog

	#def _getShowChangesInListDialog

	def _setShowChangesInListDialog(self,showChangesInListDialog):

		if self._showChangesInListDialog!=showChangesInListDialog:
			self._showChangesInListDialog=showChangesInListDialog
			self.on_showChangesInListDialog.emit()

	#def _setShowChangesInListDialog

	def updateUrlModel(self):

		ret=self._urlModel.clear()
		urlEntries=self.contentOfList
		for item in urlEntries:
			if item["url"]!="":
				self._urlModel.appendRow(item["url"])
	
	#def updateUrlModel

	def _initializeVars(self):

		self.listName=Bridge.guardManager.listName
		self.listDescription=Bridge.guardManager.listDescription
		self.showListFormMessage=[False,"","Ok"]
		self.arePendingChangesInList=False
		self.changesInHeaders=False
		self.changesInContent=False
		self.fileToLoad=None
		self.lastChangeFromFile=""
		self.contentOfList=copy.deepcopy(Bridge.guardManager.urlConfigData)
		self._urlModel.clear()

	#def _initializeVars

	@Slot()
	def goHome(self):

		if not self.arePendingChangesInList:
			self.listCurrentOption=0
			self.core.mainStack.moveToStack=1
			self.core.mainStack.manageGoToStack()
		else:
			self.showChangesInListDialog=True
			self.core.mainStack.moveToStack=""

	#def goHome

	@Slot(int)
	def loadList(self,listToLoad):
		
		self.core.mainStack.closePopUp=[False,WAITING_LOADING_LIST_CODE]
		self.core.guardOptionsStack.showMainMessage=[False,"","Ok"]
		self.editList=LoadList(False,listToLoad)
		self.edit=True
		self.editList.start()
		self.editList.finished.connect(self._loadListRet)

	#def loadList

	def _loadListRet(self):

		self.currentListConfig=copy.deepcopy(Bridge.guardManager.currentListConfig)
		self.contentOfList=copy.deepcopy(Bridge.guardManager.urlConfigData)
		if self.editList.ret["status"]:
			self._initializeVars()
			if self.editList.ret["data"]=="":
				self.updateUrlModel()
				self.showUrlsList=True
			else:
				self.fileToLoad=self.editList.ret["data"]
				self.lastChangeFromFile=Bridge.guardManager.getLastChangeInFile(self.fileToLoad)
				self.showUrlsList=False
			self.core.mainStack.closePopUp=[True,""]
			self.core.mainStack.currentStack=2
			self.listCurrentOption=1

	#def _loadListRet

	@Slot()
	def openListFile(self):

		self.showListFormMessage=[False,"","Ok"]
		self.showListFormMessage=[True,WAITING_OPEN_FILE_CODE,"Information"]
		self.core.mainStack.closeGui=False
		self.enableForm=False
		self.openFileT=OpenListFile(self.fileToLoad)
		self.openFileT.start()
		self.openFileT.finished.connect(self._openFileRet)

	#def openListFile

	def _openFileRet(self):

		self.core.mainStack.closeGui=True
		self.showListFormMessage=[False,"","Ok"]
		self.enableForm=True
		lastChangeFromFile=Bridge.guardManager.getLastChangeInFile(self.fileToLoad)

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
			self.currentListConfig["id"]=Bridge.guardManager.getListId(listName)
			self.currentListConfig["name"]=self.listName

		if self.currentListConfig!=Bridge.guardManager.currentListConfig:
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

		if self.currentListConfig!=Bridge.guardManager.currentListConfig:
			self.changesInHeaders=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInContent:
				self.changesInHeaders=False
				self.arePendingChangesInList=False

	#def updateListDescription

	@Slot(str)
	def addNewUrl(self,urlToAdd):

		self.showListFormMessage=[False,"","Ok"]
		tmpNewUrl=urlToAdd.split(" ")
		
		for item in tmpNewUrl:
			if item!="":
				self._urlModel.appendRow(item)
				tmp={}
				tmp["url"]=item
				self.contentOfList.append(tmp)

		if self.contentOfList!= Bridge.guardManager.urlConfigData:
			self.changesInContent=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInHeaders:
				self.arePendingChangesInList=False
				self.changesInContent=False 
 
	#def AddNewUrl

	@Slot(int)
	def removeUrl(self,urlToRemove):

		self.showListFormMessage=[False,"","Ok"]
		tmpUrl=self._urlModel._entries[urlToRemove]["url"]
		self._urlModel.removeRow(urlToRemove)

		for i in range(len(self.contentOfList)-1,-1,-1):
			if tmpUrl==self.contentOfList[i]["url"]:
				self.contentOfList.pop(i)

		if self.contentOfList!=Bridge.guardManager.urlConfigData:
			self.changesInContent=True
			self.arePendingChangesInList=True
		else:
			if not self.changesInHeaders:
				self.arePendingChangesInList=False
				self.changesInContent=False 

	#def removeUrl

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

		self.core.mainStack.closeGui=False
		self.showListFormMessage=[False,"","Ok"]
		self.core.mainStack.closePopUp=[False,WAITING_SAVE_CHANGES]
		dataToCheck=[self.currentListConfig["id"],self.currentListConfig["name"]]
		self.checkListChangesT=CheckListChanges(dataToCheck,self.edit,self.fileToLoad)
		self.checkListChangesT.start()
		self.checkListChangesT.finished.connect(self._checkListChangesRet)

	#def saveListChanges

	def _checkListChangesRet(self):

		if self.checkListChangesT.ret["result"]:
			Bridge.guardManager.urlConfigData=self.contentOfList
			self.saveChangesT=SaveChanges(self.currentListConfig,self.edit,self.fileToLoad)
			self.saveChangesT.start()
			self.saveChangesT.finished.connect(self._saveChangesRet)
		else:
			self.core.mainStack.closePopUp=[True,""]
			self.showListFormMessage=[True,self.checkListChangesT.ret["code"],"Error"]

	#def _checkListChangesRet

	def _saveChangesRet(self):

		if self.saveChangesT.ret["status"]:
			self.core.guardOptionsStack._updateListsModel()
			self.core.guardOptionsStack.showMainMessage=[True,self.saveChangesT.ret["code"],"Ok",""]
			self.core.guardOptionsStack.arePendingChanges=True
		else:
			self.core.guardOptionsStack.showMainMessage=[True,self.saveChangesT.ret["code"],"Error",self.saveChangesT.ret["data"]]

		self.core.mainStack.closePopUp=[True,""]
		self.arePendingChangesInList=False
		self.core.mainStack.closeGui=True
		self.core.mainStack.moveToStack=1
		self.core.mainStack.manageGoToStack()
		self.listCurrentOption=0

	#def _saveChangesRet
		
	on_listName=Signal()
	listName=Property(str,_getListName,_setListName,notify=on_listName)

	on_listDescription=Signal()
	listDescription=Property(str,_getListDescription,_setListDescription,notify=on_listDescription)

	on_showListFormMessage=Signal()
	showListFormMessage=Property('QVariantList',_getShowListFormMessage,_setShowListFormMessage, notify=on_showListFormMessage)

	on_listCurrentOption=Signal()
	listCurrentOption=Property(int,_getListCurrentOption,_setListCurrentOption, notify=on_listCurrentOption)

	on_arePendingChangesInList=Signal()
	arePendingChangesInList=Property(bool,_getArePendingChangesInList,_setArePendingChangesInList,notify=on_arePendingChangesInList)

	on_enableForm=Signal()
	enableForm=Property(bool,_getEnableForm,_setEnableForm,notify=on_enableForm)

	on_showChangesInListDialog=Signal()
	showChangesInListDialog=Property(bool,_getShowChangesInListDialog,_setShowChangesInListDialog,notify=on_showChangesInListDialog)

	on_showUrlsList=Signal()
	showUrlsList=Property(bool,_getShowUrlsList,_setShowUrlsList,notify=on_showUrlsList)
	
	urlModel=Property(QObject,_getUrlModel,constant=True)

#class Bridge

from . import Core


