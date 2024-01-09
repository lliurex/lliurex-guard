from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import ListsModel

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.guardManager=self.core.guardManager
		self._listsModel=ListsModel.ListsModel()
		self._showMainMessage=[False,"","Ok"]
		self._enableGlobalOptions=True
		self._guardMode="DisableMode"


	#def _init__
	
	def loadConfig(self):

		self.enableGlobalOptions=True
		self.guardMode=Bridge.guardManager.guardMode
		self._updateListsModel()

	#def loadConfig

	def _getListsModel(self):

		return self._listsModel

	#def _getListsModel

	def _getShowMainMessage(self):

		return self._showMainMessage

	#def _getShowMainMessage

	def _setShowMainMessage(self,showMainMessage):

		if self._showMainMessage!=showMainMessage:
			self._showMainMessage=showMainMessage
			self.on_showMainMessage.emit()

	#def _setShowMainMessage

	def _getEnableGlobalOptions(self):

		return self._enableGlobalOptions

	#def _getEnableGlobalOptions

	def _setEnableGlobalOptions(self,enableGlobalOptions):

		if self._enableGlobalOptions!=enableGlobalOptions:
			self._enableGlobalOptions=enableGlobalOptions
			self.on_enableGlobalOptions.emit()

	#def _setEnableGlobalOptions

	def _getGuardMode(self):

		return self._guardMode

	#def _getGuardMode

	def _setGuardMode(self,guardMode):

		if self._guardMode!=guardMode:
			self._guardMode=guardMode
			self.on_guardMode.emit()

	#def _setGuardMode

	def _updateListsModel(self):

		ret=self._listsModel.clear()
		listsEntries=Bridge.guardManager.listsConfigData
		for item in listsEntries:
			if item["id"]!="":
				self._listsModel.appendRow(item["order"],item["id"],item["name"],item["entries"],item["description"],item["activated"],item["delete"],item["metaInfo"])
	
	#def _updateListsModel

	@Slot('QVariantList')
	def changeListStatus(self,data):

		print(data)

	#def changeListStatus

	@Slot('QVariantList')
	def removeList(self,data):

		print(data)

	#def removeList

	@Slot(str)
	def changeGuardMode(self,mode):

		print(mode)

	#def changeGuardMode

	on_showMainMessage=Signal()
	showMainMessage=Property('QVariantList',_getShowMainMessage,_setShowMainMessage, notify=on_showMainMessage)
	
	on_enableGlobalOptions=Signal()
	enableGlobalOptions=Property(bool,_getEnableGlobalOptions,_setEnableGlobalOptions,notify=on_enableGlobalOptions)

	on_guardMode=Signal()
	guardMode=Property(str,_getGuardMode,_setGuardMode,notify=on_guardMode)
	
	listsModel=Property(QObject,_getListsModel,constant=True)

#class Bridge

from . import Core


