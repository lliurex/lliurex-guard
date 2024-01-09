from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os 
import sys
import threading
import time
import copy

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


class GatherInfo(QThread):

	def __init__(self,*args):
		
		QThread.__init__(self)

	#def _init__

	def run(self,*args):
		
		time.sleep(1)
		self.readGuardmode=Bridge.guardManager.readGuardmode()
		if self.readGuardmode['status']:
			if self.readGuardmode['data']!="DisableMode":
				self.readGuardmodeHeaders=Bridge.guardManager.readGuardmodeHeaders()
			else:
				self.readGuardmodeHeaders={'status':True}

	#def run

#class GatherInfo

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.guardManager=self.core.guardManager
		self._currentStack=0
		self._mainCurrentOption=0
		self._closePopUp=[True,""]
		self.moveToStack=""
		self._closeGui=True
		self._showLoadErrorMessage=[False,"",""]

	#def _init__

	def initBridge(self):

		self.currentStack=0
		self.closeGui=False
		try:
			Bridge.guardManager.createN4dClient(sys.argv[1],sys.argv[2])

			if Bridge.guardManager.userValidated:
				self.gatherInfo=GatherInfo()
				self.gatherInfo.start()
				self.gatherInfo.finished.connect(self._loadConfig)
			else:
				self.closeGui=True
				self.showLoadErrorMessage=[True,Bridge.guardManager,USER_NOT_VALID_ERROR]
		except:
			self.closeGui=True
			msg="Error caused by sys.arg. Number of arguments received: %s"%len(sys.argv)
			Bridge.guardManager._debug("LOADING",msg)
			Bridge.guardManager.write_log(msg)
			self.showLoadErrorMessage=[True,Bridge.guardManager,LOAD_LLIUREXGUARD_ERROR]
	
	#def initBridge
	
	def _loadConfig(self):

		self.closeGui=True
		if self.gatherInfo.readGuardmode['status']:
			if self.gatherInfo.readGuardmodeHeaders['status']:
				self.core.guardOptionsStack.loadConfig()
				self._systemLocale=Bridge.guardManager.systemLocale
				self.currentStack=1
			else:
				self.showLoadErrorMessage=[True,self.gatherInfo.readGuardmodeHeaders['code'],self.gatherInfo.readGuardmodeHeaders['data']]
		else:
			self.showLoadErrorMessage=[True,self.gatherInfo.readGuardmode['code'].self.gatherInfo.readGuarMode['data']]
	
	#def _loadConfig

	def _getSystemLocale(self):

		return self._systemLocale

	#def _getSystemLocale

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack	

	def _setCurrentStack(self,currentStack):
		
		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurentStack

	def _getMainCurrentOption(self):

		return self._mainCurrentOption

	#def _getMainCurrentOption	

	def _setMainCurrentOption(self,mainCurrentOption):
		
		if self._mainCurrentOption!=mainCurrentOption:
			self._mainCurrentOption=mainCurrentOption
			self.on_mainCurrentOption.emit()

	#def _setMainCurrentOption

	def _getClosePopUp(self):

		return self._closePopUp

	#def _getClosePopUp

	def _setClosePopUp(self,closePopUp):

		if self._closePopUp!=closePopUp:
			self._closePopUp=closePopUp
			self.on_closePopUp.emit()

	#def _setClosePopUp

	def _getShowLoadErrorMessage(self):

		return self._showLoadErrorMessage

	#def _getShowLoadErrorMessage

	def _setShowLoadErrorMessage(self,showLoadErrorMessage):

		if self._showLoadErrorMessage!=showLoadErrorMessage:
			self._showLoadErrorMessage=showLoadErrorMessage
			self.on_showLoadErrorMessage.emit()

	#def _setShowLoadErrorMessage

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui
			self.on_closeGui.emit()

	#def _setCloseGui

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
		
		if 'valencia' in self._systemLocale:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Guard+en+Lliurex.'
		else:
			self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex-Guard-en-Lliurex'
		
		self.openHelpT=threading.Thread(target=self._openHelp)
		self.openHelpT.daemon=True
		self.openHelpT.start()

	#def openHelp

	def _openHelp(self):

		os.system(self.helpCmd)

	#def _openHelp

	@Slot()
	def closeLliureXGuard(self):

		self.closeGui=True

	#def closeLliurexGuard
	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)

	on_mainCurrentOption=Signal()
	mainCurrentOption=Property(int,_getMainCurrentOption,_setMainCurrentOption, notify=on_mainCurrentOption)

	on_showLoadErrorMessage=Signal()
	showLoadErrorMessage=Property('QVariantList',_getShowLoadErrorMessage,_setShowLoadErrorMessage, notify=on_showLoadErrorMessage)

	on_closePopUp=Signal()
	closePopUp=Property('QVariantList',_getClosePopUp,_setClosePopUp, notify=on_closePopUp)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	systemLocale=Property(str,_getSystemLocale,constant=True)

#class Bridge

from . import Core


