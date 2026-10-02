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

	listStatusChanged=Signal()

	def __init__(self,manager,allLists,active,listToEdit):

		super.__init__()
		self.manager=manager
		self.allLists=allLists
		self.active=active
		self.listToEdit=listToEdit

	#def __init__

	def run(self,*args):
		
		time.sleep(0.5)
		ret=self.manager.changeListsStatus(self.allLists,self.active,self.listToEdit)

		self.listStatusChanged.emit()
	#def run

#class ChangeListsStatus

class RemoveLists(QThread):

	listRemoved=Signal()
	def __init__(self,manager,allLists,listToRemove):

		super.__init__()
		self.manager=manager
		self.allLists=allLists
		self.listToRemove=listToRemove

	#def __init__

	def run(self,*args):
		
		time.sleep(0.5)
		ret=self.manager.removeLists(self.allLists,self.listToRemove)
		self.listRemoved.emit()

	#def run

#class RemoveLists

class RestoreList(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.allLists=args[0]
		self.listToRestore=args[1]

	#def __init__

	def run(self,*args):

		time.sleep(0.5)
		ret=self.guardManager.restoreList(self.allLists,self.listToRestore)

	#def run

#class RestoreLists

class ChangeMode(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.mode=args[0]
		self.retChange={}
		self.retMode={}
		self.retHeaders={}

	#def __init__

	def run(self,*args):

		self.retChange=self.guardManager.changeGuardmode(self.mode)
		if self.retChange["status"]:
			self.retMode=self.guardManager.readGuardmode()
			if self.retMode['status']:
				if self.retMode['data']!="DisableMode":
					self.retHeaders=self.guardManager.readGuardmodeHeaders()
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

		self.retChange=self.guardManager.applyChanges()
		if self.retChange["status"]:
			self.retHeaders=self.guardManager.readGuardmodeHeaders()
		else:
			if self.retChange["code"]==-10:
				ret=self.guardManager.readGuardmode()
	#def run

#class ApplyChanges

class Bridge(QObject):

	showMainMessageChanged=Signal()
	enableGlobalOptionsChanged=Signal()
	enableListsStatusOptionsChanged=Signal()
	guardModeChanged=Signal()
	showChangeModeDialogChanged=Signal()
	arePendingChangesChanged=Signal()
	showPendingChangesDialogChanged=Signal()
	showRemoveListsDialogChanged=Signal()
	enableRemoveListsOptionChanged=Signal()
	enableRestoreListsOptionChanged=Signal()
	showRestoreListsDialogChanged=Signal()
	filterStatusValueChanged=Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		self.guardManager=self.core.guardManager
		self._listsModel=ListsModel.ListsModel()
		self._showMainMessage={"show":False,"msgCode":"","type":"","data"}
		self._enableGlobalOptions=True
		self._guardMode="DisableMode"
		self._showChangeModeDialog={"show":False,"modeToChange":""}
		self._enableListsStatusOptions={"allActivated":True,"allDeactivated":True,"enableStatusFilter":True}
		self._arePendingChanges=False
		self._showPendingChangesDialog=False
		self._showRemoveListsDialog={"show":False,"removeAll":False}
		self._enableRemoveListsOption=True
		self._enableRestoreListsOption=True
		self._showRestoreListsDialog=False
		self._showUpdateDnsDialog=False
		self._filterStatusValue="all"

	#def _init__

	@Property('QVariant',notify=showMainMessageChanged)
	def showMainMessage(self):

		return self._showMainMessage

	#def showMainMessage

	@showMainMessage.setter
	def showMainMessage(self,showMainMessage):

		if self._showMainMessage!=showMainMessage:
			self._showMainMessage=showMainMessage
			self.showMainMessageChanged.emit()

	#def showMainMessage

	@Property(bool,notify=enableGlobalOptionsChanged)
	def enableGlobalOptions(self):

		return self._enableGlobalOptions

	#def enableGlobalOptions

	@enableGlobalOptions.setter
	def enableGlobalOptions(self,enableGlobalOptions):

		if self._enableGlobalOptions!=enableGlobalOptions:
			self._enableGlobalOptions=enableGlobalOptions
			self.enableGlobalOptionsChanged.emit()

	#def enableGlobalOptions

	@Property('QVariant', notify=enableListsStatusOptionsChanged)
	def enableListsStatusOptions(self):

		return self._enableListsStatusOptions

	#def enableListsStatusOptions

	@enableGlobalOptions.setter
	def enableListsStatusOptions(self,enableListsStatusOptions):

		if self._enableListsStatusOptions!=enableListsStatusOptions:
			self._enableListsStatusOptions=enableListsStatusOptions
			self.enableListsStatusOptionsChanged.emit()

	#def enableListsStatusOptions	

	@Property(str,notify=guardModeChanged)
	def guardMode(self):

		return self._guardMode

	#def guardMode

	@guardMode.setter
	def guardMode(self,guardMode):

		if self._guardMode!=guardMode:
			self._guardMode=guardMode
			self.guardModeChanged.emit()

	#def guardMode

	@Property('QVariant',notify=showChangeModeDialogChanged)
	def showChangeModeDialog(self):

		return self._showChangeModeDialog

	#def showChangeModeDialog

	@showChangeModeDialog.setter
	def showChangeModeDialog(self,showChangeModeDialog):

		if self._showChangeModeDialog!=showChangeModeDialog:
			self._showChangeModeDialog=showChangeModeDialog
			self.showChangeModeDialogChanged.emit()

	#def showChangeModeDialog

	@Property(bool,notify=arePendingChangesChanged)
	def arePendingChanges(self):

		return self._arePendingChanges

	#def arePendingChanges

	@arePendingChanges.setter
	def arePendingChanges(self,arePendingChanges):

		if self._arePendingChanges!=arePendingChanges:
			self._arePendingChanges=arePendingChanges
			self.arePendingChangesChanged.emit()

	#def arePendingChanges

	@Property(bool,notify=showPendingChangesDialogChanged)
	def showPendingChangesDialog(self):

		return self._showPendingChangesDialog

	#def showPendingChangesDialog

	@showPendingChangesDialog.setter
	def showPendingChangesDialog(self,showPendingChangesDialog):

		if self._showPendingChangesDialog!=showPendingChangesDialog:
			self._showPendingChangesDialog=showPendingChangesDialog
			self.showPendingChangesDialogChanged.emit()

	#def showPendingChangesDialog	

	@Property('QVariant',notify=showRemoveListsDialogChanged)
	def showRemoveListsDialog(self):

		return self._showRemoveListsDialog

	#def showRemoveListsDialog

	@showRemoveListsDialog.setter
	def showRemoveListsDialog(self,showRemoveListsDialog):

		if self._showRemoveListsDialog!=showRemoveListsDialog:
			self._showRemoveListsDialog=showRemoveListsDialog
			self.showRemoveListsDialogChanged.emit()

	#def showRemoveListsDialog

	@Property(bool,notify=enableRemoveListsOptionChanged)
	def enableRemoveListsOption(self):

		return self._enableRemoveListsOption

	#def enableRemoveListsOption

	@enableRemoveListsOption.setter
	def enableRemoveListsOption(self,enableRemoveListsOption):

		if self._enableRemoveListsOption!=enableRemoveListsOption:
			self._enableRemoveListsOption=enableRemoveListsOption
			self.enableRemoveListsOptionChanged.emit()

	#def enableRemoveListsOption

	@Property(bool,notify=enableRestoreListsOptionChanged)
	def enableRestoreListsOption(self):

		return self._enableRestoreListsOption

	#def enableRestoreListsOption

	@enableRestoreListsOption.setter
	def enableRestoreListsOption(self,enableRestoreListsOption):

		if self._enableRestoreListsOption!=enableRestoreListsOption:
			self._enableRestoreListsOption=enableRestoreListsOption
			self.enableRestoreListsOptionChanged.emit()

	#def enableRestoreListsOption	
	
	@Property(bool,notify=showRestoreListsDialogChanged)
	def showRestoreListsDialog(self):

		return self._showRestoreListsDialog

	#def showRestoreListsDialgo

	@showRestoreListsDialog.setter
	def showRestoreListsDialog(self,showRestoreListsDialog):

		if self._showRestoreListsDialog!=showRestoreListsDialog:
			self._showRestoreListsDialog=showRestoreListsDialog
			self.showRestoreListsDialogChanged.emit()

	#def showRestoreListsDialog	
	
	@Property(str,notify=filterStatusValueChanged)
	def filterStatusValue(self):

		return self._filterStatusValue

	#def filterStatusValue

	@filterStatusValue.setter
	def filterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.filterStatusValueChanged.emit()

	#def filterStatusValue

	def _getListsModel(self):

		return self._listsModel

	#def _getListsModel

	def loadConfig(self):

		self.guardMode=self.guardManager.guardMode
		self._updateListsModel()
		self.manageGlobalOptions()

	#def loadConfig

	def manageGlobalOptions(self):

		self.enableGlobalOptions=self.guardManager.checkGlobalOptionStatus()
		self.enableListsStatusOptions=self.guardManager.checkChangeStatusListsOption()
		self.enableRemoveListsOption=self.guardManager.checkRemoveListsOption()
		self.enableRestoreListsOption=self.guardManager.checkRestoreListsOption()

	#def manageGlobalOptions

	def _updateListsModel(self,forceClear=False):

		ret=self._listsModel.clear()
		if not forceClear:
			listsEntries=self.guardManager.listsConfigData
			for item in listsEntries:
				if item["id"]!="":
					self._listsModel.appendRow(item["order"],item["id"],item["name"],item["entries"],item["description"],item["activated"],item["remove"],item["metaInfo"])
		
	#def _updateListsModel

	def _updateListsModelInfo(self,param):

		updatedInfo=self.guardManager.listsConfigData
		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				index=self._listsModel.index(i)
				self._listsModel.setData(index,param,updatedInfo[i][param])

	#def _updateListsModelInfo

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	@Slot('QJSValue')
	def changeListStatus(self,data):

		if hasattr(data,'toVariant'):
			data=data.toVariant()

		self.core.mainStack.closeGui=False
		self.showMainMessage={"show":False,"msgCode":"","type":"","data"}
		self.changeAllLists=data.get("allLists")
		active=data.get("active")
		if self.changeAllLists:
			listToEdit=None
		else:
			listToEdit=data.get("listId")

		self.core.mainStack.showPopUp={"show":True,"msgCode":WAITING_APPLY_LISTS_CHANGES_CODE}
		self.changeStatusT=ChangeListStatus(self.manager,self.changeAllLists,active,listToEdit)
		self.changeStatusT.start()
		self.changeStatusT.listStatusChanged.connect(self._changeStatusRet)
		self.changeStatusT.finished.connect(self.changeStatusT.deleteLater)		

	#def changeListStatus

	@Slot()
	def _changeStatusRet(self):

		self._updateListsModelInfo('activated')
		self.enableListsStatusOptions=self.guardManager.checkChangeStatusListsOption()
		self.filterStatusValue="all"
		if self.guardManager.listsConfig!=self.guardManager.listsConfigOrig:
			self.arePendingChanges=True
		else:
			self.arePendingChanges=False
		
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}
		self.core.mainStack.closeGui=True

	#def _changeStatusRet

	@Slot('QJSValue')
	def removeLists(self,data):

		if hasattr(data,'toVariant'):
			data=data.toVariant()


		self.showMainMessage={"show":False,"msgCode":"","type":"","data"}
		self.removeAllLists=data.get("allLists")

		if self.removeAllLists:
			self.listToRemove=None
		else:
			self.listToRemove=data.get("listId")

		self.showRemoveListsDialog={"show":True,"removeAll":self.removeAllLists}

	#def removeLists

	@Slot(str)
	def manageRemoveListsDialog(self,response):

		self.showRemoveListsDialog={"show":False,"removeAll":False}
		if response=="Apply":
			self.core.mainStack.closeGui=False
			self.core.mainStack.showPopUp={"show":True,"msgCode":WAITING_REMOVE_LISTS_CODE}
			self.removeListsT=RemoveLists(self.manager,self.removeAllLists,self.listToRemove)
			self.removeListsT.start()
			self.removeListsT.listRemoved.connect(self._removeListsRet)
			self.removeListsT.finished.connect(self.removeListT.deleteLater)	

	#def manageRemoveListsDialog

	@Slot()
	def _removeListsRet(self):

		self._updateListsModelInfo('remove')

		self.manageGlobalOptions()
		self.filterStatusValue="all"
		
		if self.guardManager.listsConfig!=self.guardManager.listsConfigOrig:
			self.arePendingChanges=True
		else:
			self.arePendingChanges=False
		
		self.core.mainStack.showPopUp={"show":False,"msgCode":""}
		self.core.mainStack.closeGui=True

	#def _removeListRet

	@Slot('QVariantList')
	def restoreLists(self,data):

		self.showMainMessage=[False,"","Ok",""]
		self.restoreAllLists=data[0]

		if self.restoreAllLists:
			self.listToRestore=None
			self.showRestoreListsDialog=True
		else:
			self.listToRestore=data[1]
			self.manageRestoreListsDialog('Apply')

		
	@Slot(str)
	def manageRestoreListsDialog(self,response):

		self.showRestoreListsDialog=[False,False]
		if response=="Apply":
			self.core.mainStack.closeGui=False
			self.core.mainStack.showPopUp=[False,WAITING_RESTORE_LIST_CODE]
			self.restoreListT=RestoreList(self.restoreAllLists,self.listToRestore)
			self.restoreListT.start()
			self.restoreListT.finished.connect(self._restoreListRet)
	
	#def manageRestoreListsDialog

	def _restoreListRet(self):

		self._updateListsModelInfo('remove')
		self.manageGlobalOptions()
		self.filterStatusValue="all"
		
		if self.guardManager.listsConfig!=self.guardManager.listsConfigOrig:
			self.arePendingChanges=True
		else:
			self.arePendingChanges=False

		self.core.mainStack.showPopUp=[True,""]
		self.core.mainStack.closeGui=True

	#def _restoreListRet

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
			self.core.mainStack.showPopUp=[False,WAITING_CHANGE_GUARDMODE_CODE]
			self.changeModeT=ChangeMode(self.modeToChange)
			self.changeModeT.start()
			self.changeModeT.finished.connect(self._changeModeRet)

	#def manageChangeModeDialog

	def _changeModeRet(self):

		if self.changeModeT.retChange['status']:
			if self.changeModeT.retMode['status']:
				self.guardMode=self.guardManager.guardMode
				if self.changeModeT.retHeaders['status']:
					self._updateListsModel()
					self.showMainMessage=[True,self.changeModeT.retChange['code'],"Ok"]
				else:
					self.showMainMessage=[True,self.changeModeT.retHeaders['code'],"Error",self.changeModeT.retHeaders['data']]		
			else:
				self.showMainMessage=[True,self.changeModeT.retMode['code'],"Error",self.changeModeT.retMode['data']]
		else:
			self.showMainMessage=[True,self.changeModeT.retChange['code'],"Error",self.changeModeT.retChange['data']]

		self.manageGlobalOptions()
		self.filterStatusValue="all"
		self.core.mainStack.showPopUp=[True,""]
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
			try:
				self.guardManager.removeTmpFile()
			except:
				pass
				
			self.core.mainStack.closeGui=True

	#def managePendingChangesDialog

	@Slot()
	def applyChanges(self):

		self.showMainMessage=[False,"","Ok",""]
		self.core.mainStack.closeGui=False
		self.core.mainStack.showPopUp=[False,WAITING_APPLY_CHANGES_CODE]
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
			try:
				self.guardManager.removeTmpFile()
			except:
				pass
			self.core.mainStack.closeGui=True

		else:
			if self.applyChangesT.retChange["code"]==-10:
				self.core.mainStack.closeGui=True
				self.arePendingChanges=False
				self.guardMode=self.guardManager.guardMode
				self._updateListsModel(True)
				self.manageGlobalOptions()
			self.showMainMessage=[True,self.applyChangesT.retChange["code"],"Error",self.applyChangesT.retChange["data"]]

		self.core.mainStack.showPopUp=[True,""]		

	#def _applyChangesRet

	listsModel=Property(QObject,_getListsModel,constant=True)

#class Bridge

from . import Core


