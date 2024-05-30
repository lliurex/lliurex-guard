#!/usr/bin/env python3

import sys
import os


from . import GuardManager
from . import ListStack
from . import GuardOptionsStack
from . import MainStack


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

	
		self.guardManager=GuardManager.GuardManager()
		self.listStack=ListStack.Bridge()
		self.guardOptionsStack=GuardOptionsStack.Bridge()
		self.mainStack=MainStack.Bridge()
		
		self.mainStack.initBridge()			
		
		
	#def init
	
	
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint

#class Core
