from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import ListsModel

WAITING_CHANGE_GUARDMODE_CODE=7

class ChangeMode(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.mode=args[0]
		self.retChange={}
		self.retMode={}
		self.retHeaders={}

	#def __init__

	def run(self,*args):

		self.retChange=Bridge.guardManager.changeGuardmode(self.mode)
		if self.retChange["status"]:
			self.retMode=Bridge.guardManager.readGuardmode()
			if self.retMode['status']:
				if self.retMode['data']!="DisableMode":
					self.retHeaders=Bridge.guardManager.readGuardmodeHeaders()
				else:
					self.retHeaders={"status":True}
	#def run

#class ChangeMode

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.guardManager=self.core.guardManager
		self._listsModel=ListsModel.ListsModel()
		self._showMainMessage=[False,"","Ok",""]
		self._enableGlobalOptions=True
		self._guardMode="DisableMode"
		self._showChangeModeDialog=[False,""]
		self._showUpdateDnsOption=False
	
	#def _init__
	
	def loadConfig(self):

		self.guardMode=Bridge.guardManager.guardMode
		self._updateListsModel()
		self.enableGlobalOptions=Bridge.guardManager.checkGlobalOptionStatus()
		self.showUpdateDnsOption=Bridge.guardManager.checkUpdateDnsOptionStatus()

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

	def _getShowUpdateDnsOption(self):

		return self._showUpdateDnsOption

	#def _getShowUpdateDnsOption

	def _setShowUpdateDnsOption(self,showUpdateDnsOption):

		if self._showUpdateDnsOption!=showUpdateDnsOption:
			self._showUpdateDnsOption=showUpdateDnsOption
			self.on_showUpdateDnsOption.emit()

	#def _setShowUpdateDnsOption

	def _getGuardMode(self):

		return self._guardMode

	#def _getGuardMode

	def _setGuardMode(self,guardMode):

		if self._guardMode!=guardMode:
			self._guardMode=guardMode
			self.on_guardMode.emit()

	#def _setGuardMode

	def _getShowChangeModeDialog(self):

		return self._showChangeModeDialog

	#def _getShowChangeModeDialog

	def _setShowChangeModeDialog(self,showChangeModeDialog):

		if self._showChangeModeDialog!=showChangeModeDialog:
			self._showChangeModeDialog=showChangeModeDialog
			self.on_showChangeModeDialog.emit()

	#def _setShowChangeModeDialog

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

	@Slot()
	def updateWhiteListDNS(self):

		print("Update DNS")

	#def updateWhiteListDNS

	@Slot(str)
	def changeGuardMode(self,mode):

		self.modeToChange=mode
		self._showMainMessage=[False,"","Ok"]
		self.showChangeModeDialog=[True,self.modeToChange]
	
	#def changeGuardMode

	@Slot(str)
	def manageChangeModeDialog(self,response):

		self.showChangeModeDialog=[False,""]
		if response=="Accept":
			self.core.mainStack.closeGui=False
			self.core.mainStack.closePopUp=[False,WAITING_CHANGE_GUARDMODE_CODE]
			self.changeModeT=ChangeMode(self.modeToChange)
			self.changeModeT.start()
			self.changeModeT.finished.connect(self._changeModeRet)

	#def manageChangeModeDialog

	def _changeModeRet(self):

		if self.changeModeT.retChange['status']:
			if self.changeModeT.retMode['status']:
				self.guardMode=Bridge.guardManager.guardMode
				if self.changeModeT.retHeaders['status']:
					self._updateListsModel()
					self.showMainMessage=[True,self.changeModeT.retChange['code'],"Ok"]
				else:
					self.showMainMessage=[True,self.changeModeT.retHeaders['code'],"Error",self.changeModeT.retHeaders['data']]		
			else:
				self.showMainMessage=[True,self.changeModeT.retMode['code'],"Error",self.changeModeT.ret['data']]
		else:
			self.showMainMessage=[True,self.changeModeT.retChange['code'],"Error",self.changeModeT.ret['data']]

		self.enableGlobalOptions=Bridge.guardManager.checkGlobalOptionStatus()
		self.showUpdateDnsOption=Bridge.guardManager.checkUpdateDnsOptionStatus()
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _changeModeRet

	@Slot()
	def addCustomList(self):

		self.core.mainStack.currentStack=2

	#def addCustomList

	on_showMainMessage=Signal()
	showMainMessage=Property('QVariantList',_getShowMainMessage,_setShowMainMessage, notify=on_showMainMessage)
	
	on_enableGlobalOptions=Signal()
	enableGlobalOptions=Property(bool,_getEnableGlobalOptions,_setEnableGlobalOptions,notify=on_enableGlobalOptions)

	on_showUpdateDnsOption=Signal()
	showUpdateDnsOption=Property(bool,_getShowUpdateDnsOption,_setShowUpdateDnsOption,notify=on_showUpdateDnsOption)

	on_guardMode=Signal()
	guardMode=Property(str,_getGuardMode,_setGuardMode,notify=on_guardMode)
	
	on_showChangeModeDialog=Signal()
	showChangeModeDialog=Property('QVariantList',_getShowChangeModeDialog,_setShowChangeModeDialog,notify=on_showChangeModeDialog)

	listsModel=Property(QObject,_getListsModel,constant=True)

#class Bridge

from . import Core


