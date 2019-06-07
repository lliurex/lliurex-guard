#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib



import signal
import os
import subprocess
import json
import sys
import time
import threading
from jsondiff import diff

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from . import settings
import gettext
_ = gettext.gettext

class MainWindow:
	
	def __init__(self,):

		self.core=Core.Core.get_core()

	#def init

	
	def load_gui(self):
		
		gettext.textdomain(settings.TEXT_DOMAIN)
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-guard.css"
				
		self.stack_window= Gtk.Stack()
		self.stack_window.set_transition_duration(750)
		self.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_window.set_margin_top(0)
		self.stack_window.set_margin_bottom(0)
		
		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("LliureX Guard")
		self.main_window.resize(802,745)
		self.main_box=builder.get_object("main_box")
		
		self.banner_box=builder.get_object("banner_box")
		self.image_banner_box=builder.get_object("image_banner_box")
	
		self.stack_window.add_titled(self.banner_box,"bannerBox", "Banner Box")
		self.stack_window.add_titled(self.core.editBox, "editBox", "Edit Box")
		self.stack_window.show_all()
		self.main_box.pack_start(self.stack_window,True,True,0)


		self.stack_banner= Gtk.Stack()
		self.stack_banner.set_transition_duration(750)
		self.stack_banner.set_halign(Gtk.Align.FILL)
		self.stack_banner.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

		
		self.stack_banner.add_titled(self.core.loginBox,"loginBox", "Login Box")
		self.stack_banner.add_titled(self.core.optionsBox,"optionsBox", "Options Box")
		self.stack_banner.show_all()
		self.banner_box.pack_start(self.stack_banner,True,True,5)
		
		self.set_css_info()
		self.init_threads()
		self.connect_signals()
			
		self.main_window.show()
		self.stack_window.set_transition_type(Gtk.StackTransitionType.NONE)
		self.stack_window.set_visible_child_name("bannerBox")
		self.stack_banner.set_visible_child_name("loginBox")

		
	#def load_gui


	def init_threads(self):

		self.load_info_t=threading.Thread(target=self.load_list_info)
		self.load_info_t.daemon=True

		GObject.threads_init()

	#def init_threads	

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()
		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.main_window.set_name("WINDOW")
		#self.image_banner_box.set_name("IMAGE_BANNER")
		
	#def set_css_info	
				
			
	def connect_signals(self):
		
		self.main_window.connect("destroy",Gtk.main_quit)
		self.main_window.connect("delete_event",self.check_changes)

	#def connect_signals		
		
	def load_info(self,action=None):
	
		self.core.optionsBox.toolbar.show()
		self.core.optionsBox.search_entry.show()	
		self.core.optionsBox.options_pbar.hide()
		self.guardMode=""
		self.list_info={}
		self.init_threads()
		self.load_info_t.start()
		GLib.timeout_add(100,self.pulsate_load_info,action)

	#def load_info
	
	def pulsate_load_info(self,action=None):

		if self.load_info_t.is_alive():
			if action!=None:
				self.core.optionsBox.options_pbar.pulse()
			return True

		else:
			if action!=None:
				self.core.optionsBox.options_pbar.hide()

			if self.read_guardmode['status']:
				if not self.read_guardmode_headers['status']:
					self.core.optionsBox.add_button.set_sensitive(False)
					self.core.optionsBox.apply_btn.set_sensitive(False)
				else:
					self.core.optionsBox.set_mode()
					self.core.optionsBox.draw_list("init")
					if action==None:
						self.stack_banner.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
						self.stack_banner.set_visible_child_name("optionsBox")
					else:
						if action=="apply":
							self.core.optionsBox.options_msg_label.set_text(self.get_msg(self.core.optionsBox.result_apply['code']))
						else:
							self.core.optionsBox.options_msg_label.set_text(self.get_msg(self.core.optionsBox.result_mode['code']))
	
						self.core.optionsBox.main_box.set_sensitive(True)
						self.core.optionsBox.options_msg_label.set_name("MSG_CORRECT_LABEL")		
			else:
				self.core.optionsBox.options_msg_label.set_text(self.get_msg(read_guardmode['code']))
				self.core.optionsBox.options_msg_label.set_label("MSG_ERROR_LABEL")
				self.core.optionsBox.add_button.set_sensitive(False)
				self.core.optionsBox.apply_btn.set_sensitive(False)

			return False	

	#def pulsate_load_info	

	def load_list_info(self):

		self.read_guardmode=self.core.guardmanager.read_guardmode()
		if self.read_guardmode['status']:
			self.guardMode=self.read_guardmode['data']
			if self.guardMode!="DisableMode":
				self.read_guardmode_headers=self.core.guardmanager.read_guardmode_headers()
				if self.read_guardmode_headers['status']:
					self.list_info=self.read_guardmode_headers['data']
			else:
				self.read_guardmode_headers={'status':True}
	
	#def load_list_info

	def get_msg(self,code):

		if code==0:
			msg_text=""
		elif code==1:
			msg_text=_("You must indicate a name for the list")
		elif code==2:
			msg_text=_("The name of the list is duplicate")
		elif code==3:
			msg_text=_("List created successfully")
		elif code==4:
			msg_text=_("List edited successfully")
		elif code==5:
			msg_text=_("Error saving the changes of the list:")
		elif code==6:
			msg_text=_("Waiting while viewing / editing the list")
		elif code==7:
			msg_text=_("Changing LliureX Guard mode. Wait a moment...")
		elif code==8:
			msg_text=_("The change of LliureX Guard mode has been successful")	
		elif code==9:
			msg_text=_("Error changing LliureX Guard mode:")
		elif code==10:
			msg_text=_("Error restarting dnsmasq")
		elif code==11:
			msg_text=_("Loading the information from the list. Wait a moment...")
		elif code==12:
			msg_text=_("Information of the list loaded successfully")
		elif code==13:
			msg_text=_("Error loading the information from the list")	
		elif code==14:
			msg_text=_("Loading file. Wait a moment...")
		elif code==15:
			msg_text=_("File loaded sucessfully")	
		elif code==16:
			msg_text=_("Error loading file")	
		elif code==17:
			msg_text=_("Applying changes. Wait a moment...")
		elif code==18:
			msg_text=_("Changes applied successfully")	
		elif code==19:
			msg_text=_("Error removing lists")
		elif code==20:
			msg_text=_("Error activating lists")
		elif code==21:
			msg_text=("Error deactivating lists")
		elif code==22:
			msg_text=_("LLiureX Guard mode readed sucessfully")
		elif code==23:
			msg_text=_("Error reading Lliurex Guard mode")
		elif code==24:
			msg_text=_("List code readed successfully")
		elif code==25:
			msg_text=_("Error reading list headers")
		elif code==26:
			msg_text=_("Saving changes. Wait a moment...")
		return msg_text

	#def get_msg	


	def check_changes(self,widget,event=None):

		pending_changes=0

		if len(self.core.optionsBox.list_data)>0:
			if len(self.list_info)>0:	
				pending_changes=len(diff(self.list_info,self.core.optionsBox.list_data))
			else:
				pending_changes+=1	

		if pending_changes>0:
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,
		          Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),"LliureX Guard")
			dialog.format_secondary_text(_("There are pending changes to apply. Do you want to exit or cancel?"))
			response=dialog.run()
			dialog.destroy()
			if response==Gtk.ResponseType.CLOSE:
				return False
			else:
				return True

		sys.exit(0)

	#def check_changes

	def start_gui(self):
		
		GObject.threads_init()
		Gtk.main()
		
	#def start_gui


	
#class MainWindow

from . import Core
