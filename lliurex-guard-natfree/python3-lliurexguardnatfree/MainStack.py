from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
from PySide2.QtGui import QDesktopServices
import os 
import sys
import time

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	infoGathered=Signal(dict)

	def __init__(self,manager):

		super().__init__()
		self.manager=manager

	#def _init__

	def run(self,*args):
		
		time.sleep(0.2)
		ret=self.manager.readGuardmode()
		retHeaders={"status":False,"data":""}
		if ret.get('status'):
			if ret.get('data')!="DisableMode":
				retHeaders=self.manager.readGuardmodeHeaders()
			else:
				retHeaders={'status':True}

		dataToEmit={
			"guardMode":ret,
			"headers":retHeaders
		}

		self.infoGathered.emit(dataToEmit)

	#def run

#class GatherInfo

class Bridge(QObject):

	currentStackChanged=Signal()
	mainCurrentOptionChanged=Signal()
	showLoadErrorMessageChanged=Signal()
	showPopUpChanged=Signal()
	closeGuiChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.guardManager=self.core.guardManager
		self._currentStack=0
		self._mainCurrentOption=0
		self._showPopUp={"show":False,"msgCode":""}
		self.moveToStack=""
		self._closeGui=True
		self._showLoadErrorMessage={"show":False,"msgCode":"","data":"","type":""}
		self.guardManager.createN4dClient(sys.argv[1])

	#def _init__

	@Property(int,notify=currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack	

	@currentStack.setter
	def currentStack(self, currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.currentStackChanged.emit()

	#def currentStack

	@Property(int, notify=mainCurrentOptionChanged)
	def mainCurrentOption(self):

		return self._mainCurrentOption

	#def mainCurrentOption	

	@mainCurrentOption.setter
	def mainCurrentOption(self,mainCurrentOption):
		
		if self._mainCurrentOption!=mainCurrentOption:
			self._mainCurrentOption=mainCurrentOption
			self.mainCurrentOptionChanged.emit()

	#def mainCurrentOption

	@Property('QVariant',notify=showLoadErrorMessageChanged)
	def showLoadErrorMessage(self):

		return self._showLoadErrorMessage

	#def showLoadErrorMessage

	@showLoadErrorMessage.setter
	def showLoadErrorMessage(self,showLoadErrorMessage):

		if self._showLoadErrorMessage!=showLoadErrorMessage:
			self._showLoadErrorMessage=showLoadErrorMessage
			self.showLoadErrorMessageChanged.emit()

	#def showLoadErrorMessage

	@Property('QVariant',notify=showPopUpChanged)
	def showPopUp(self):

		return self._showPopUp

	#def showPopUp

	@showPopUp.setter
	def showPopUp(self,showPopUp):

		if self._showPopUp!=showPopUp:
			self._showPopUp=showPopUp
			self.showPopUpChanged.emit()

	#def showPopUp

	@Property(bool,notify=closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui
			self.closeGuiChanged.emit()

	#def closeGui

	def initBridge(self):

		self.currentStack=0
		self.closeGui=False
		self.gatherInfoT=GatherInfo(self.guardManager)
		self.gatherInfoT.start()
		self.gatherInfoT.infoGathered.connect(self._loadConfig)
		self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)

	#def initBridge
	
	@Slot(dict)
	def _loadConfig(self,ret):

		guardMode=ret.get("guarMode")

		if not guardMode.get("status"):
			self.showLoadErrorMessage={"show":True,"msgCode":guardMode.get("code"),"data":guardMode.get("data"),"type":guardMode.get("type")}
			self.closeGui
			return
		
		headers=ret.get("headers")
		if not headers,get("status"):
			self.showLoadErrorMessage={"show":True,"msgCode":headers.get("code"),"data":headers.get("data"),"type":headers.get("type")}
			self.closeGui
			return

		self.core.guardOptionsStack.loadConfig()
		self.currentStack=1
	
		self.closeGui=True

	#def _loadConfig


	@Slot(int)
	def moveToMainOptions(self,stack):

		if self.mainCurrentOption!=stack:
			if stack==0:
				self.mainCurrentOption=stack
			else:
				self._loadHolidayStack()

	#def moveToMainOptions	

	def manageGoToStack(self):

		if self.moveToStack!="":
			self.currentStack=self.moveToStack
			self.mainCurrentOption=0
			self.moveToStack=""

	#def _manageGoToStack

	@Slot()
	def openHelp(self):
		
		self.helpCmd='https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Guard+en+Lliurex'
		QDesktopServices.openUrl(helpUrl)
	
	#def openHelp

	@Slot()
	def closeLliureXGuard(self):

		if self.core.guardOptionsStack.arePendingChanges:
			if self.currentStack!=2:
				self.closeGui=False
				self.core.guardOptionsStack.showPendingChangesDialog=True
		else:
			try:
				self.guardManager.removeTmpFile()
			except:
				pass

	#def closeLliurexGuard
		
#class Bridge

from . import Core


