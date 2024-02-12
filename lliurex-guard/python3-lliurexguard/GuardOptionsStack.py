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
WAITING_APPLY_LISTS_CHANGES_CODE=18
WAITING_REMOVE_LISTS_CODE=19
WAITING_RESTORE_LIST_CODE=20
WAITING_APPLY_CHANGES_CODE=17
WAITING_UPDATE_DNS=27

class ChangeListStatus(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.allLists=args[0]
		self.active=args[1]
		self.listToEdit=args[2]

	#def __init__

	def run(self,*args):
		time.sleep(0.5)
		ret=Bridge.guardManager.changeListsStatus(self.allLists,self.active,self.listToEdit)

	#def run

#class ChangeListsStatus

class RemoveLists(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.allLists=args[0]
		self.listToRemove=args[1]

	#def __init__

	def run(self,*args):
		
		time.sleep(0.5)
		ret=Bridge.guardManager.removeLists(self.allLists,self.listToRemove)

	#def run

#class RemoveLists

class RestoreList(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.listToRestore=args[0]

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		ret=Bridge.guardManager.restoreList(self.listToRestore)

	#def run

#class RestoreLists

class UpdateDns(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.ret={}

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		self.ret=Bridge.guardManager.updateListDns()

	#def run

#class UpdateDns

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

class ApplyChanges(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.retChange={}
		self.retHeaders={}

	#def __init__

	def run(self,*args):

		self.retChange=Bridge.guardManager.applyChanges()
		if self.retChange["status"]:
			self.retHeaders=Bridge.guardManager.readGuardmodeHeaders()
		else:
			if self.retChange["code"]==-10:
				ret=Bridge.guardManager.readGuardmode()
	#def run

#class ApplyChanges

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
		self._enableListsStatusOptions=[True,True,True]
		self._arePendingChanges=False
		self._showPendingChangesDialog=False
		self._showRemoveListsDialog=[False,False]
		self._enableRemoveListsOption=True
		self._showUpdateDnsDialog=False
		self._filterStatusValue="all"

	#def _init__
	
	def loadConfig(self):

		self.guardMode=Bridge.guardManager.guardMode
		self._updateListsModel()
		self.enableGlobalOptions=Bridge.guardManager.checkGlobalOptionStatus()
		self.enableListsStatusOptions=Bridge.guardManager.checkChangeStatusListsOption()
		self.showUpdateDnsOption=Bridge.guardManager.checkUpdateDnsOptionStatus()
		print(self.enableListsStatusOptions)
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

	def _getEnableListsStatusOptions(self):

		return self._enableListsStatusOptions

	#def _getEnableListsStatusOptions

	def _setEnableListsStatusOptions(self,enableListsStatusOptions):

		if self._enableListsStatusOptions!=enableListsStatusOptions:
			self._enableListsStatusOptions=enableListsStatusOptions
			self.on_enableListsStatusOptions.emit()

	#def _setEnableListsStatusOptions

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

	def _getArePendingChanges(self):

		return self._arePendingChanges

	#def _getArePendingChanges

	def _setArePendingChanges(self,arePendingChanges):

		if self._arePendingChanges!=arePendingChanges:
			self._arePendingChanges=arePendingChanges
			self.on_arePendingChanges.emit()

	#def _setArePendingChanges

	def _getShowPendingChangesDialog(self):

		return self._showPendingChangesDialog

	#def _getShowPendingChangesDialog

	def _setShowPendingChangesDialog(self,showPendingChangesDialog):

		if self._showPendingChangesDialog!=showPendingChangesDialog:
			self._showPendingChangesDialog=showPendingChangesDialog
			self.on_showPendingChangesDialog.emit()

	#def _setShowPendingChangesDialog

	def _getShowRemoveListsDialog(self):

		return self._showRemoveListsDialog

	#def _getShowRemoveListsDialog

	def _setShowRemoveListsDialog(self,showRemoveListsDialog):

		if self._showRemoveListsDialog!=showRemoveListsDialog:
			self._showRemoveListsDialog=showRemoveListsDialog
			self.on_showRemoveListsDialog.emit()

	#def _setShowRemoveListsDialog

	def _getEnableRemoveListsOption(self):

		return self._enableRemoveListsOption

	#def _getEnableRemoveListsOption

	def _setEnableRemoveListsOption(self,enableRemoveListsOption):

		if self._enableRemoveListsOption!=enableRemoveListsOption:
			self._enableRemoveListsOption=enableRemoveListsOption
			self.on_enableRemoveListsOption.emit()

	#def _setEnableRemoveListsOption

	def _getShowUpdateDnsDialog(self):

		return self._showUpdateDnsDialog

	#def _getShowUpdateDnsDialog

	def _setShowUpdateDnsDialog(self,showUpdateDnsDialog):

		if self._showUpdateDnsDialog!=showUpdateDnsDialog:
			self._showUpdateDnsDialog=showUpdateDnsDialog
			self.on_showUpdateDnsDialog.emit()

	#def _setShowUpdateDnsDialog

	def _getFilterStatusValue(self):

		return self._filterStatusValue

	#def _getFilterStatusValue

	def _setFilterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.on_filterStatusValue.emit()

	#def _setFilterStatusValue

	def _updateListsModel(self,forceClear=False):

		ret=self._listsModel.clear()
		if not forceClear:
			listsEntries=Bridge.guardManager.listsConfigData
			for item in listsEntries:
				if item["id"]!="":
					self._listsModel.appendRow(item["order"],item["id"],item["name"],item["entries"],item["description"],item["activated"],item["remove"],item["metaInfo"])
		
	#def _updateListsModel

	def _updateListsModelInfo(self,param):

		updatedInfo=Bridge.guardManager.listsConfigData
		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				index=self._listsModel.index(i)
				self._listsModel.setData(index,param,updatedInfo[i][param])

	#def _updateListsModelInfo

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	@Slot('QVariantList')
	def changeListStatus(self,data):

		self.core.mainStack.closeGui=False
		self.showMainMessage=[False,"","Ok",""]
		self.changeAllLists=data[0]
		active=data[1]
		if self.changeAllLists:
			listToEdit=None
		else:
			listToEdit=data[2]

		self.core.mainStack.closePopUp=[False,WAITING_APPLY_LISTS_CHANGES_CODE]
		self.changeStatusT=ChangeListStatus(self.changeAllLists,active,listToEdit)
		self.changeStatusT.start()
		self.changeStatusT.finished.connect(self._changeStatusRet)		

	#def changeListStatus

	def _changeStatusRet(self):

		self._updateListsModelInfo('activated')
		self.enableListsStatusOptions=Bridge.guardManager.checkChangeStatusListsOption()
		self.filterStatusValue="all"
		if Bridge.guardManager.listsConfig!=Bridge.guardManager.listsConfigOrig:
			self.arePendingChanges=True
		else:
			self.arePendingChanges=False
		
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _changeStatusRet

	@Slot('QVariantList')
	def removeLists(self,data):

		self.showMainMessage=[False,"","Ok",""]
		self.removeAllLists=data[0]

		if self.removeAllLists:
			self.listToRemove=None
		else:
			self.listToRemove=data[1]

		self.showRemoveListsDialog=[True,self.removeAllLists]

	#def removeLists

	@Slot(str)
	def manageRemoveListsDialog(self,response):

		self.showRemoveListsDialog=[False,False]
		if response=="Apply":
			self.core.mainStack.closeGui=False
			self.core.mainStack.closePopUp=[False,WAITING_REMOVE_LISTS_CODE]
			self.removeListsT=RemoveLists(self.removeAllLists,self.listToRemove)
			self.removeListsT.start()
			self.removeListsT.finished.connect(self._removeListsRet)	

	#def manageRemoveListsDialog

	def _removeListsRet(self):

		self._updateListsModelInfo('remove')
		self.enableGlobalOptions=Bridge.guardManager.checkGlobalOptionStatus()
		self.enableRemoveListsOption=Bridge.guardManager.checkRemoveListsOption()
		self.enableListsStatusOptions=Bridge.guardManager.checkChangeStatusListsOption()
		self.filterStatusValue="all"
		
		if Bridge.guardManager.listsConfig!=Bridge.guardManager.listsConfigOrig:
			self.arePendingChanges=True
		else:
			self.arePendingChanges=False
		
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _removeListRet

	@Slot(str)

	def restoreList(self,listToRestore):

		self.showMainMessage=[False,"","Ok",""]
		self.core.mainStack.closePopUp=[False,WAITING_RESTORE_LIST_CODE]
		self.restoreListT=RestoreList(listToRestore)
		self.restoreListT.start()
		self.restoreListT.finished.connect(self._restoreListRet)

	#def restoreList

	def _restoreListRet(self):

		self._updateListsModelInfo('remove')
		self.enableRemoveListsOption=Bridge.guardManager.checkRemoveListsOption()
		self.enableListsStatusOptions=Bridge.guardManager.checkChangeStatusListsOption()
		self.filterStatusValue="all"
		
		if Bridge.guardManager.listsConfig!=Bridge.guardManager.listsConfigOrig:
			self.arePendingChanges=True
		else:
			self.arePendingChanges=False

		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _restoreListRet

	@Slot()
	def updateWhiteListDNS(self):

		self.showMainMessage=[False,"","Ok",""]
		self.showUpdateDnsDialog=True

	#def updateWhiteListDNS

	@Slot(str)
	def manageUpdateDnsDialog(self,response):

		self.showUpdateDnsDialog=False

		if response=="Accept":
			self.core.mainStack.closeGui=False
			self.core.mainStack.closePopUp=[False,WAITING_UPDATE_DNS]
			self.updateDnsT=UpdateDns()
			self.updateDnsT.start()
			self.updateDnsT.finished.connect(self._updateDnsRet)

	#def manageUpdateDnsDialog

	def _updateDnsRet(self):

		if self.updateDnsT.ret['status']:
			self.showMainMessage=[True,self.updateDnsT.ret['code'],"Ok",""]
		else:
			self.showMainMessage=[True,self.updateDnsT.ret["code"],"Error",self.updateDnsT.ret["data"]]

		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _updateDnsRet


	@Slot(str)
	def changeGuardMode(self,mode):

		self.modeToChange=mode
		self._showMainMessage=[False,"","Ok",""]
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
				self.showMainMessage=[True,self.changeModeT.retMode['code'],"Error",self.changeModeT.retMode['data']]
		else:
			self.showMainMessage=[True,self.changeModeT.retChange['code'],"Error",self.changeModeT.retChange['data']]

		self.enableGlobalOptions=Bridge.guardManager.checkGlobalOptionStatus()
		self.enableListsStatusOptions=Bridge.guardManager.checkChangeStatusListsOption()
		self.filterStatusValue="all"
		self.showUpdateDnsOption=Bridge.guardManager.checkUpdateDnsOptionStatus()
		self.core.mainStack.closePopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _changeModeRet

	@Slot()
	def addCustomList(self):

		self.core.mainStack.currentStack=2

	#def addCustomList

	@Slot(str)
	def managePendingChangesDialog(self,response):

		self.showPendingChangesDialog=False

		if response=="Apply":
			self.applyChanges()
		elif response=="Discard":
			self.arePendingChanges=False
			self.core.mainStack.closeGui=True

	#def managePendingChangesDialog

	@Slot()
	def applyChanges(self):

		self.showMainMessage=[False,"","Ok",""]
		self.core.mainStack.closeGui=False
		self.core.mainStack.closePopUp=[False,WAITING_APPLY_CHANGES_CODE]
		self.applyChangesT=ApplyChanges()
		self.applyChangesT.start()
		self.applyChangesT.finished.connect(self._applyChangesRet)

	#def applyChanges

	def _applyChangesRet(self):

		if self.applyChangesT.retChange["status"]:
			if self.applyChangesT.retHeaders["status"]:
				self.loadConfig()
				self.showMainMessage=[True,self.applyChangesT.retChange["code"],"Ok",""]
			else:
				self.showMainMessage=[True,self.applyChangesT.retHeaders["code"],"Error",self.applyChangesT.retHeaders["data"]]

			self.arePendingChanges=False
			self.core.mainStack.closeGui=True

		else:
			if self.applyChangesT.retChange["code"]==-10:
				self.core.mainStack.closeGui=True
				self.arePendingChanges=False
				self.guardMode=Bridge.guardManager.guardMode
				self._updateListsModel(True)
				self.enableGlobalOptions=Bridge.guardManager.checkGlobalOptionStatus()
				self.enableListsStatusOptions=Bridge.guardManager.checkChangeStatusListsOption()

			self.showMainMessage=[True,self.applyChangesT.retChange["code"],"Error",self.applyChangesT.retChange["data"]]

		self.core.mainStack.closePopUp=[True,""]		

	#def _applyChangesRet
	 
	on_showMainMessage=Signal()
	showMainMessage=Property('QVariantList',_getShowMainMessage,_setShowMainMessage, notify=on_showMainMessage)
	
	on_enableGlobalOptions=Signal()
	enableGlobalOptions=Property(bool,_getEnableGlobalOptions,_setEnableGlobalOptions,notify=on_enableGlobalOptions)

	on_enableListsStatusOptions=Signal()
	enableListsStatusOptions=Property('QVariantList',_getEnableListsStatusOptions,_setEnableListsStatusOptions,notify=on_enableListsStatusOptions)

	on_showUpdateDnsOption=Signal()
	showUpdateDnsOption=Property(bool,_getShowUpdateDnsOption,_setShowUpdateDnsOption,notify=on_showUpdateDnsOption)

	on_guardMode=Signal()
	guardMode=Property(str,_getGuardMode,_setGuardMode,notify=on_guardMode)
	
	on_showChangeModeDialog=Signal()
	showChangeModeDialog=Property('QVariantList',_getShowChangeModeDialog,_setShowChangeModeDialog,notify=on_showChangeModeDialog)

	on_arePendingChanges=Signal()
	arePendingChanges=Property(bool,_getArePendingChanges,_setArePendingChanges,notify=on_arePendingChanges)

	on_showPendingChangesDialog=Signal()
	showPendingChangesDialog=Property(bool,_getShowPendingChangesDialog,_setShowPendingChangesDialog,notify=on_showPendingChangesDialog)

	on_showRemoveListsDialog=Signal()
	showRemoveListsDialog=Property('QVariantList',_getShowRemoveListsDialog,_setShowRemoveListsDialog,notify=on_showRemoveListsDialog)

	on_enableRemoveListsOption=Signal()
	enableRemoveListsOption=Property(bool,_getEnableRemoveListsOption,_setEnableRemoveListsOption,notify=on_enableRemoveListsOption)

	on_showUpdateDnsDialog=Signal()
	showUpdateDnsDialog=Property(bool,_getShowUpdateDnsDialog,_setShowUpdateDnsDialog,notify=on_showUpdateDnsDialog)

	on_filterStatusValue=Signal()
	filterStatusValue=Property(str,_getFilterStatusValue,_setFilterStatusValue,notify=on_filterStatusValue)

	listsModel=Property(QObject,_getListsModel,constant=True)

#class Bridge

from . import Core


