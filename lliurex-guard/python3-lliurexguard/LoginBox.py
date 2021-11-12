#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import sys
import os
import gettext
import threading
from . import settings


gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class LoginBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-guard.css"

		self.login_box=builder.get_object("login_box")
		self.login_msg_box=builder.get_object("login_msg_box")
		self.login_error_img=builder.get_object("login_error_img")
		self.login_msg_label=builder.get_object("login_msg_label")
		self.login_spinner=builder.get_object("login_spinner")

		self.pack_start(self.login_box,True,True,0)
		self.set_css_info()
		self.init_threads()
		self.load()
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
	#def set_css_info	

	def init_threads(self):
		
		GObject.threads_init()

	#def init_threads	

	def load(self):

		self.login_msg_label.set_halign(Gtk.Align.CENTER)
		self.login_msg_label.set_text(_("Correct user\nLoading information. Wait a moment..."))
		self.login_msg_box.set_name("HIDE_BOX")
		self.login_error_img.hide()
		self.login_spinner.start()
				
		t=threading.Thread(target=self.core.guardmanager.create_n4dClient(sys.argv[1],sys.argv[2]))
		t.daemon=True
		t.start()
		GLib.timeout_add(500,self.load_listener,t)

	#def load

	def load_listener(self,thread):

		if thread.is_alive():
			return True

		if self.core.guardmanager.user_validated:
			self.core.mainWindow.load_info("login")
		else:
			self.login_spinner.stop()
			self.login_msg_box.set_name("ERROR_BOX")
			self.login_error_img.show()
			self.login_msg_label.set_name("FEEDBACK_LABEL")
			self.login_msg_label.set_halign(Gtk.Align.START)
			self.login_msg_label.set_text(_("Invalid user"))		
	
		return False

	#def load_listener 	

#class LoginBox

from . import Core