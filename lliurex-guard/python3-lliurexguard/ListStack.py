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

class Bridge(QObject):

	
	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.guardManager=self.core.guardManager
		self._urlModel=UrlModel.UrlModel()
		self._listName=Bridge.guardManager.listName
		self._listDescription=Bridge.guardManager.listDescription
		self._showListFormMessage=[False,"","Ok"]
		self._changesInList=False
		self._listCurrentOption=0
		self._showUrlsList=False

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

	def _getChangesInList(self):

		return self._changesInList

	#def _getChangesInList

	def _setChangesInList(self,changesInList):

		if self._changesInList!=changesInList:
			self._changesInList=changesInList
			self.on_changesInList.emit()

	#def _setChangesInList

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

	def updateUrlModel(self):

		ret=self._urlModel.clear()
		urlEntries=Bridge.guardManager.urlConfigData
		for item in urlEntries:
			if item["url"]!="":
				self._urlModel.appendRow(item["id"],item["url"])
	
	#def updateUrlModel

	def _initializeVars(self):

		self.listName=Bridge.guardManager.listName
		self.listDescription=Bridge.guardManager.listDescription
		self.showListFormMessage=[False,"","Ok"]
		self.changesInList=False
		self._urlModel.clear()

	#def _initializeVars

	@Slot()
	def goHome(self):

		if not self.changesInList:
			self.core.mainStack.currentStack=1
			self.core.mainStack.mainCurrentOption=0
			self.listCurrentOption=0
			self.core.mainStack.moveToStack=""
		else:
			#self.showChangesInListDialog=True
			self.core.mainStack.moveToStack=1

	#def goHome

	@Slot(int)
	def loadList(self,listToLoad):
		
		self.core.mainStack.closePopUp=[False,WAITING_LOADING_LIST_CODE]
		self.core.guardOptionsStack.showMainMessage=[False,"","Ok"]
		self.editList=LoadList(False,listToLoad)
		self.editList.start()
		self.editList.finished.connect(self._loadListRet)

	#def loadList

	def _loadListRet(self):

		self.currentListConfig=copy.deepcopy(Bridge.guardManager.currentListConfig)
		if self.editList.ret["status"]:
			self._initializeVars()
			if self.editList.ret["data"]=="":
				self.updateUrlModel()
				self.showUrlsList=True
			else:
				self.showUrlsList=False
			self.core.mainStack.closePopUp=[True,""]
			self.core.mainStack.currentStack=2
			self.listCurrentOption=1

	#def _loadListRet

	on_listName=Signal()
	listName=Property(str,_getListName,_setListName,notify=on_listName)

	on_listDescription=Signal()
	listDescription=Property(str,_getListDescription,_setListDescription,notify=on_listDescription)

	on_showListFormMessage=Signal()
	showListFormMessage=Property('QVariantList',_getShowListFormMessage,_setShowListFormMessage, notify=on_showListFormMessage)

	on_listCurrentOption=Signal()
	listCurrentOption=Property(int,_getListCurrentOption,_setListCurrentOption, notify=on_listCurrentOption)

	on_changesInList=Signal()
	changesInList=Property(bool,_getChangesInList,_setChangesInList,notify=on_changesInList)

	on_showUrlsList=Signal()
	showUrlsList=Property(bool,_getShowUrlsList,_setShowUrlsList,notify=on_showUrlsList)
	
	urlModel=Property(QObject,_getUrlModel,constant=True)

#class Bridge

from . import Core


