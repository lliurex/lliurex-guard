#!/usr/bin/python3
import os
import sys
from PySide2 import QtCore, QtGui, QtQml

class UrlModel(QtCore.QAbstractListModel):

	UrlRole=QtCore.Qt.UserRole+1000
	
	def __init__(self,parent=None):
		
		super(UrlModel, self).__init__(parent)
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
			if role == UrlModel.UrlRole:
				return item["url"]

	#def data

	def roleNames(self):
		
		roles = dict()
		roles[UrlModel.UrlRole] = b"url"
	
		return roles

	#def roleNames

	def appendRow(self,u):
		
		tmpId=[]
		for item in self._entries:
			tmpId.append(item["url"])
		if u not in tmpId:
			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
			self._entries.append(dict(url=u))
			self.endInsertRows()

	#def appendRow

	def removeRow(self,index):
		self.beginRemoveRows(QtCore.QModelIndex(),index,index)
		self._entries.pop(index)
		self.endRemoveRows()
	
	#def removeRow

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class UrlModel