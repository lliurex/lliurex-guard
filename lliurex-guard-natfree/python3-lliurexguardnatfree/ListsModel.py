#!/usr/bin/python3
import os
import sys
from PySide2 import QtCore, QtGui, QtQml

class ListsModel(QtCore.QAbstractListModel):

	OrderRole=QtCore.Qt.UserRole+1000
	IdRole= QtCore.Qt.UserRole + 1001
	NameRole=QtCore.Qt.UserRole+1002
	EntriesRole=QtCore.Qt.UserRole+1003
	DescriptionRole=QtCore.Qt.UserRole+1004
	ActivatedRole=QtCore.Qt.UserRole+1005
	RemoveRole=QtCore.Qt.UserRole+1006
	MetaInfoRole=QtCore.Qt.UserRole+1007
	
	def __init__(self,parent=None):
		
		super(ListsModel, self).__init__(parent)
		self._entries =[]
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == ListsModel.OrderRole:
				return item["order"]
			elif role == ListsModel.IdRole:
				return item["id"]
			elif role==ListsModel.NameRole:
				return item["name"]
			elif role == ListsModel.EntriesRole:
				return item["entries"]
			elif role == ListsModel.DescriptionRole:
				return item["description"]
			elif role == ListsModel.ActivatedRole:
				return item["activated"]
			elif role == ListsModel.RemoveRole:
				return item["remove"]
			elif role == ListsModel.MetaInfoRole:
				return item["metaInfo"]
			

	#def data

	def roleNames(self):
		
		roles = dict()
		roles[ListsModel.OrderRole]=b"order"
		roles[ListsModel.IdRole] = b"id"
		roles[ListsModel.NameRole] = b"name"
		roles[ListsModel.EntriesRole] = b"entries"
		roles[ListsModel.DescriptionRole] = b"description"
		roles[ListsModel.ActivatedRole] = b"activated"
		roles[ListsModel.RemoveRole] = b"remove"
		roles[ListsModel.MetaInfoRole]=b"metaInfo"
		return roles

	#def roleNames

	def appendRow(self,od,i,na,en,des,ac,re,mt):
		
		tmpId=[]
		for item in self._entries:
			tmpId.append(item["id"])
		tmpN=na.strip()
		if i not in tmpId and na !="" and len(tmpN)>0:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
			self._entries.append(dict(order=od,id=i,name=na,entries=en,description=des,activated=ac,remove=re,metaInfo=mt))
			self.endInsertRows()

	#def appendRow

	def removeRow(self,index):
		self.beginRemoveRows(QtCore.QModelIndex(),index,index)
		self._entries.pop(index)
		self.endRemoveRows()
	
	#def removeRow

	def setData(self, index, param, value, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			if param in ["activated","remove"]:
				if self._entries[row][param]!=value:
					self._entries[row][param]=value
					self.dataChanged.emit(index,index)
					return True
				else:
					return False
			else:
				return False
	
	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class ListsModel
