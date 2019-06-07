#!/usr/bin/env python3

import sys
import os


from . import guardmanager
from . import MainWindow
from . import LoginBox
from . import OptionsBox
from . import EditBox
from . import settings


class Core:
	
	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	#def get_core
	
	def __init__(self,args=None):

	
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.ui_path= settings.RSRC_DIR + "/lliurex-guard.ui"
		
		self.guardmanager=guardmanager.GuardManager()
		self.loginBox=LoginBox.LoginBox()
		self.optionsBox=OptionsBox.OptionsBox()
		self.editBox=EditBox.EditBox()
		self.mainWindow=MainWindow.MainWindow()

		self.mainWindow=MainWindow.MainWindow()

		self.mainWindow.load_gui()
		self.mainWindow.start_gui()
			
		
		
	#def init
	
	
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint
