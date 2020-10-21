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
		self.main_window.set_title("Lliurex Guard")
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
		self.lock_quit=False
		self.core.optionsBox.options_pbar.hide()

		self.main_window.show()
		self.stack_window.set_transition_type(Gtk.StackTransitionType.NONE)
		self.stack_window.set_visible_child_name("bannerBox")
		self.stack_banner.set_visible_child_name("loginBox")

		if self.core.guardmanager.is_desktop:
			if not self.core.guardmanager.is_client or not self.core.guardmanager.is_server:
				self.core.loginBox.server_ip_entry.set_text("localhost")
				self.core.loginBox.server_ip_entry.hide()

		
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
		self.image_banner_box.set_name("IMAGE_BANNER")
		
	#def set_css_info	
				
			
	def connect_signals(self):
		
		self.main_window.connect("destroy",Gtk.main_quit)
		self.main_window.connect("delete_event",self.check_changes)
		self.main_window.connect("key-press-event",self.on_key_press_event)


	#def connect_signals		
		
	def load_info(self,action):
	
		self.core.optionsBox.toolbar.show()
		self.core.optionsBox.search_entry.show()	
		#self.core.optionsBox.options_pbar.hide()
		self.guardMode=""
		self.list_info={}
		self.lock_quit=True
		self.init_threads()
		self.load_info_t.start()
		GLib.timeout_add(100,self.pulsate_load_info,action)

	#def load_info
	
	def pulsate_load_info(self,action):

		if self.load_info_t.is_alive():
			return True

		else:
			self.lock_quit=False
			
			if action=="login":
				self.core.loginBox.login_spinner.stop()
			else:
				self.core.optionsBox.option_spinner.stop()	

			if self.read_guardmode['status']:
				error=False
				self.core.optionsBox.set_mode()
				if not self.read_guardmode_headers['status']:
					error=True
					msg=self.get_msg(self.read_guardmode_headers['code'])+"\n"+self.read_guardmode_headers['data']
					
				else:
					self.core.optionsBox.draw_list("init")
					if action!="login":
						if action=="apply":
							msg=self.get_msg(self.core.optionsBox.result_apply['code'])
						else:
							msg=self.get_msg(self.core.optionsBox.result_mode['code'])
					else:
						msg=""		
							
			else:
				error=True
				msg=self.get_msg(self.read_guardmode['code'])+"\n"+self.read_guardmode['data']


			if error:
				self.core.optionsBox.add_button.set_sensitive(False)
				self.core.optionsBox.apply_btn.set_sensitive(False)
				self.core.optionsBox.options_msg_label.set_name("MSG_ERROR_LABEL")
			else:
				self.core.optionsBox.main_box.set_sensitive(True)
				self.core.optionsBox.options_msg_label.set_name("MSG_CORRECT_LABEL")
				
			self.core.optionsBox.options_msg_label.set_text(msg)
				
			if action=="login":
				self.stack_banner.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.stack_banner.set_visible_child_name("optionsBox")
			else:
				self.core.optionsBox.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.core.optionsBox.stack_opt.set_visible_child_name("listBox")	

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
			msg_text=_("Changing Lliurex Guard mode. Wait a moment...")
		elif code==8:
			msg_text=_("The change of Lliurex Guard mode has been successful")	
		elif code==9:
			msg_text=_("Error changing Lliurex Guard mode:")
		elif code==10:
			msg_text=_("Error restarting dnsmasq. Lliurex Guard will be disabled:")
		elif code==11:
			msg_text=_("Loading the information from the list. Wait a moment...")
		elif code==12:
			msg_text=_("Information of the list loaded successfully")
		elif code==13:
			msg_text=_("Error loading the information from the list:")	
		elif code==14:
			msg_text=_("Loading file. Wait a moment...")
		elif code==15:
			msg_text=_("File loaded sucessfully")	
		elif code==16:
			msg_text=_("Error loading file:")	
		elif code==17:
			msg_text=_("Applying changes. Wait a moment...")
		elif code==18:
			msg_text=_("Changes applied successfully")	
		elif code==19:
			msg_text=_("Error removing lists:")
		elif code==20:
			msg_text=_("Error activating lists:")
		elif code==21:
			msg_text=("Error deactivating lists:")
		elif code==22:
			msg_text=_("Lliurex Guard mode readed sucessfully")
		elif code==23:
			msg_text=_("Error reading Lliurex Guard mode:")
		elif code==24:
			msg_text=_("List code readed successfully")
		elif code==25:
			msg_text=_("Error reading list headers:")
		elif code==26:
			msg_text=_("Saving changes. Wait a moment...")
		elif code==27:
			msg_text=_("The file loaded is empty")
		elif code==28:
			msg_text=_("No match found for the indicated search")
		elif code==29:
			msg_text=_("%s matches found for the indicated search")
		elif code==30:
			msg_text=_("It is not possible to load the selected file.\nIts size exceeds the recommended limit of 28 Mb")
		elif code==31:
			msg_text=_("It is not possible to edit the list.\nThe file size exceeds the recommended limit of 28 Mb")	
		elif code==32:
			msg_text=_("Copying selected content. Wait a moment...")
		elif code==33:
			msg_text=_("It is not possible to copy all the selected content.\nOnly the first 2500 lines have been copied")
		elif code==34:
			msg_text=_("It is not possible to update white list dns")	
		elif code==35:
			msg_text=_("The white list dns update was successful")
		elif code==36:
			msg_text=_("Updating white list dns. Wait a moment...")	
		return msg_text


	#def get_msg	


	def check_changes(self,widget,event=None):

		if not self.lock_quit:
			pending_changes=0

			if len(self.core.optionsBox.list_data)>0:
				if len(self.list_info)>0:	
					pending_changes=len(diff(self.list_info,self.core.optionsBox.list_data))
				else:
					pending_changes+=1	

			if pending_changes>0:
				dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE,
			          Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),"Lliurex Guard")
				dialog.format_secondary_text(_("There are pending changes to apply.\nDo you want to close the application and lose the changes or cancel and return to the application?"))
				response=dialog.run()
				dialog.destroy()
				if response==Gtk.ResponseType.CLOSE:
					self.core.guardmanager.remove_tmp_file()
					return False
				else:
					return True
			try:		
				self.core.guardmanager.remove_tmp_file()
			except:
				pass			
			sys.exit(0)
		else:
			return True	

	#def check_changes

	def on_key_press_event(self,window,event):
		
		ctrl=(event.state & Gdk.ModifierType.CONTROL_MASK)
		if ctrl and event.keyval == Gdk.KEY_f:
			if self.stack_window.get_visible_child_name()=="editBox":
				if self.core.editBox.stack_edit.get_visible_child_name()=="urlTw":
					self.core.editBox.url_search_entry.grab_focus()
			else:	
				if self.stack_banner.get_visible_child_name()=="optionsBox":
					self.core.optionsBox.search_entry.grab_focus()
		
	#def on_key_press_event

	def start_gui(self):
		
		GObject.threads_init()
		Gtk.main()
		
	#def start_gui


	
#class MainWindow

from . import Core
