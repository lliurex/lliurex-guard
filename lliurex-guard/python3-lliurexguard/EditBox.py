#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gio, GObject,GLib,Gdk


from . import settings
import gettext
_ = gettext.gettext

import os
import copy
import json
import codecs
import io
import glob
import threading
import subprocess
import multiprocessing
import sys
import time
sys.setrecursionlimit(3500)

import datetime



class EditBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
	
	#def __init__	
		
	def init_form(self):

		try:
			self.editBox.remove(self.editBox.main_box)
		except:
			pass

	#def init_form		

	def render_form(self,read_tw,file=None):	

		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-guard.css"
		self.main_box=builder.get_object("list_edit_box")
		self.header_label=builder.get_object("header_label")
		self.header_separator=builder.get_object("header_separator")
		self.content_box=builder.get_object("content_box")
		list_name_label=builder.get_object("list_name_label")
		self.list_name_entry=builder.get_object("list_name_entry")
		list_description_label=builder.get_object("list_description_label")
		self.list_description_entry=builder.get_object("list_description_entry")
		url_label=builder.get_object("url_label")
		self.url_search_entry=builder.get_object("url_search_entry")

		self.url_tw_box=builder.get_object("url_tw_box")
		self.url_tw=builder.get_object("url_textview")
		self.buffer=self.url_tw.get_buffer()
		self.tag_found = self.buffer.create_tag("found",
            background="yellow")

		self.url_editor_box=builder.get_object("url_editor_box")
		url_editor_label=builder.get_object("url_editor_label")
		self.open_editor_btn=builder.get_object("open_editor_btn")

		self.edit_waiting_box=builder.get_object("edit_waiting_box")
		self.edit_spinner=builder.get_object("edit_spinner")
		self.edit_spinner_label=builder.get_object("edit_spinner_label")

		self.stack_edit= Gtk.Stack()
		self.stack_edit.set_transition_duration(750)
		self.stack_edit.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_edit.set_margin_top(0)
		self.stack_edit.set_margin_bottom(0)

		self.stack_edit.add_titled(self.url_tw_box,"urlTw","Url Tw")
		self.stack_edit.add_titled(self.url_editor_box,"urlEditor","Url Editor")
		self.stack_edit.add_titled(self.edit_waiting_box,"editWaiting","Edit Waiting")
		self.stack_edit.show_all()
		self.content_box.pack_start(self.stack_edit,True,True,5)

		self.label_list=[list_name_label,list_description_label,url_label,url_editor_label]
		self.edit_msg_label=builder.get_object("edit_msg_label")
		self.edit_pbar=builder.get_object("edit_pbar")
		self.save_btn=builder.get_object("save_btn")
		self.cancel_btn=builder.get_object("cancel_btn")
		self.edit=False
		self.header_label.set_text(_("New list"))
		self.origId=None
		self.loaded_file=file
		self.read_tw=read_tw
		if self.read_tw:
			self.core.editBox.url_search_entry.show()
		else:
			self.core.editBox.url_search_entry.hide()	
		self.edit_msg_label.set_text("")
		self.edit_pbar.hide()
		self.count=1
		self.process_block=125
		self.waiting_search=False
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		self.connect_signals()
		self.init_threads()
		#self.clipboard=Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		#self.init_data_form()
				
	#def render_form_

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

		for item in self.label_list:
			item.set_name("OPTION_LABEL")

		self.list_name_entry.set_name("CUSTOM-ENTRY")	
		self.list_description_entry.set_name("CUSTOM-ENTRY")
		self.url_search_entry.set_name("CUSTOM-ENTRY")	

		self.header_separator.set_name("SEPARATOR")
		self.header_label.set_name("HEADER-LABEL")	


	#def set_css_info

	def connect_signals(self):

		self.save_btn.connect("clicked",self.core.editBox.gather_values)
		self.cancel_btn.connect("clicked",self.core.editBox.cancel_clicked)
		self.open_editor_btn.connect("clicked",self.open_editor_clicked)
		self.url_search_entry.connect("changed",self.detect_search)
		self.url_tw.connect("paste-clipboard",self.get_clipboard)
		self.url_tw.connect("button-press-event",self.urltw_mouse_clicked)
		self.url_tw.connect("key-press-event",self.urltw_key_clicked)
	
	
	#def connect_signals	

	def init_threads(self):

		self.checking_data_t=threading.Thread(target=self.checking_data)
		self.saving_data_t=threading.Thread(target=self.saving_data)
		self.open_editor_t=multiprocessing.Process(target=self.open_editor)
		self.get_clipboard_content_t=threading.Thread(target=self.get_clipboard_content)
		self.checking_data_t.daemon=True
		self.saving_data_t.daemon=True
		self.open_editor_t.daemon=True
		self.get_clipboard_content_t.daemon=True

		GObject.threads_init()

	#def init_threads	

	def init_data_form(self):
	
		self.init_threads()

	#def init_data_form	


	def write_tw(self,clipboard,content=None):

		self.process_block=125
		
		if content!=None:
			info=content
			
		else:
			info=self.core.optionsBox.read_list['data'][0]
			
		if len(info)<self.process_block:
			self.process_block=len(info)	
		
		if len(info)>0:
			#self.core.optionsBox.options_pbar.pulse()
				
			for i in range(0,self.process_block):
				iter=self.buffer.get_end_iter()
				if i==len(info):
					self.buffer.insert(iter,info[i].split("\n")[0])
				else:
					self.buffer.insert(iter,info[i])	
			for i in range(0,self.process_block):
				info.pop(0)	
			
			return True
		else:
			if content!=None:
				pass
			else:
				self.core.editBox.load_values(self.core.optionsBox.order)
			
			self.core.mainWindow.lock_quit=False
			
			if not clipboard:
				self.core.optionsBox.option_spinner.stop()
				self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
				self.core.mainWindow.stack_window.set_visible_child_name("editBox")		
				self.stack_edit.set_visible_child_name("urlTW")
			else:
				self.edit_spinner.stop()
				self.main_box.set_sensitive(True)
				self.url_tw.set_property('editable',True)
				self.stack_edit.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.stack_edit.set_visible_child_name("urlTw")		
				if self.clipboard_content['code']==33:
					self.edit_msg_label.set_text(self.core.mainWindow.get_msg(self.clipboard_content['code']))
					self.edit_msg_label.set_name("MSG_ERROR_LABEL")
			
			return False	
	
	#def write_tw	

	def load_values(self,order):
	
		self.header_label.set_text(_("Edit list"))
		list_to_edit=copy.deepcopy(self.core.optionsBox.list_data[order])

		self.list_name_entry.set_text(list_to_edit["name"])
		self.list_description_entry.set_text(list_to_edit["description"])
		self.edit=True
		self.origId=self.core.optionsBox.list_data[order]["id"]
		self.order=order
		#data=None
		
	#def load_values	


	def gather_values(self,widget):

		self.edit_msg_label.set_text("")
		self.data_tocheck={}
		self.data_tocheck["id"]=self.core.guardmanager.get_listId(self.list_name_entry.get_text())
		self.data_tocheck["name"]=self.list_name_entry.get_text()
		self.data_tocheck["description"]=self.list_description_entry.get_text()
	
		self.edit_spinner.start()
		self.edit_spinner_label.set_text(self.core.mainWindow.get_msg(26))			
		self.edit_spinner_label.set_name("WAITING_LABEL")
		self.stack_edit.set_transition_duration(550)
		self.stack_edit.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack_edit.set_visible_child_name("editWaiting")
		
		self.main_box.set_sensitive(False)
		self.init_threads()
		self.checking_data_t.start()
		GLib.timeout_add(100,self.pulsate_checking_data)
		
	#def gather_values	

	def pulsate_checking_data(self):
		
		if self.checking_data_t.is_alive():
			#self.core.mainWindow.waiting_pbar.pulse()
			return True
			
		else:
			
			if not self.check["result"]:

				self.main_box.set_sensitive(True)
				#self.edit_pbar.hide()
				self.edit_spinner.stop()
				self.stack_edit.set_transition_duration(550)
				self.stack_edit.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				if self.read_tw:
					self.stack_edit.set_visible_child_name("urlTw")
				else:
					self.stack_edit.set_visible_child_name("urlEditor")	
				msg_text=self.core.mainWindow.get_msg(self.check["code"])
				self.edit_msg_label.set_name("MSG_ERROR_LABEL")
				self.edit_msg_label.set_text(msg_text)
				return False
			else:	
				self.save_values()
		
		
		
	#def pulsate_checking_data	
		
	def checking_data(self):
		
		self.check=self.core.guardmanager.check_data(self.core.optionsBox.list_data,self.data_tocheck,self.edit,self.loaded_file,self.origId)
	
	#def checking_data
		
	def save_values(self):		
		
		content=""
		list_info={}
		list_info["id"]=self.data_tocheck["id"]
		list_info["name"]=self.data_tocheck["name"]
		list_info["description"]=self.data_tocheck["description"]
		if self.read_tw:
			content=self.buffer.get_text(self.buffer.get_start_iter(),self.buffer.get_end_iter(),True)
			content_lines="".join(content).split("\n")
			while "" in content_lines:
				content_lines.remove("")
				
			list_info["lines"]=len(content_lines)
			content_lines=None
		
		self.args=[list_info,content,self.loaded_file]
		self.core.mainWindow.lock_quit=True
		self.init_threads()
		self.saving_data_t.start()
		GLib.timeout_add(100,self.pulsate_saving_data)

	#def save_values
	
	def pulsate_saving_data(self):

		'''
		Result code:
			-3: created successfully
			-4: edited successfully
			-5: error saving changes
		'''

		if self.saving_data_t.is_alive():
			self.edit_pbar.pulse()
			return True
			
		else:
			self.edit_spinner.stop()
			self.core.mainWindow.lock_quit=False
			self.main_box.set_sensitive(True)
			self.edit_pbar.hide()
			if self.saving['status']:
				tmp_list=self.args[0]
				replaced_to=""
				if self.edit:
					msg_code=4
					order=self.order
					if self.origId!=tmp_list["id"]:
						replaced_to=self.origId
				else:
					msg_code=3
					order=str(len(self.core.optionsBox.list_data)+1)
					self.core.optionsBox.list_data[order]={}
					self.core.optionsBox.list_data[order]["active"]=True
					self.core.optionsBox.list_data[order]["remove"]=False

				self.core.optionsBox.list_data[order]["id"]=tmp_list["id"]
				self.core.optionsBox.list_data[order]["name"]=tmp_list["name"]
				self.core.optionsBox.list_data[order]["description"]=tmp_list["description"]
				if self.read_tw:
					self.core.optionsBox.list_data[order]["lines"]=tmp_list["lines"]
				else:
					self.core.optionsBox.list_data[order]["lines"]=self.saving["lines"]	
				self.core.optionsBox.list_data[order]["replaced_to"]=replaced_to
				self.core.optionsBox.list_data[order]["tmpfile"]=self.saving["tmpfile"]
				self.core.optionsBox.list_data[order]["edited"]=True

				self.core.optionsBox.draw_list("edit")
				self.core.optionsBox.options_msg_label.set_text(self.core.mainWindow.get_msg(msg_code))
				self.core.optionsBox.options_msg_label.set_name("MSG_CORRECT_LABEL")
				
			else:
				self.core.optionsBox.options_msg_label.set_text(self.core.mainWindow.get_msg(self.saving['code'])+'\n'+self.saving['data'])
				self.core.optionsBox.options_msg_label.set_name("MSG_ERROR_LABEL")

			self.core.optionsBox.main_box.set_sensitive(True)
			self.core.optionsBox.search_entry.set_text("")
			self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
			self.core.mainWindow.stack_window.set_visible_child_name("bannerBox")
			self.core.mainWindow.stack_banner.set_visible_child_name("optionsBox")
			self.core.optionsBox.stack_opt.set_visible_child_name("listBox")
			self.core.editBox.remove(self.core.editBox.main_box)
			
			return False

	#def pulsate_saving_data
	
	def saving_data(self):

		self.saving=self.core.guardmanager.save_conf(self.args)
	
	#def saving_data	

	def open_editor_clicked(self,widget):

		
		self.init_threads()
		self.main_box.set_sensitive(False)
		self.core.mainWindow.lock_quit=True
		self.open_editor_t.start()
		self.edit_msg_label.set_text(self.core.mainWindow.get_msg(6))
		self.edit_msg_label.set_name("WAITING_LABEL")
		GLib.timeout_add(10,self.pulsate_waiting_editor_close)
		
		
		
	#def open_editor_clicked	

	def pulsate_waiting_editor_close(self):

		if self.open_editor_t.is_alive():
			return True

		else:
			self.core.mainWindow.lock_quit=False
			self.main_box.set_sensitive(True)
			self.edit_msg_label.set_text("")

			return False

	#def pulsate_waiting_editor_close		

	def open_editor(self):
	
		cmd="kwrite %s"%self.loaded_file
		os.system(cmd)
	
	#def open_editor

	def cancel_clicked(self,widget):

		self.core.optionsBox.main_box.set_sensitive(True)
		self.core.editBox.remove(self.core.editBox.main_box)
		self.core.optionsBox.options_msg_label.set_text("")
		self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.core.mainWindow.stack_window.set_visible_child_name("bannerBox")
		self.core.mainWindow.stack_banner.set_visible_child_name("optionsBox")
		self.core.optionsBox.stack_opt.set_visible_child_name("listBox")

	#def cancel_clicked	
	
	
	def detect_search(self,widget,event=None):

		self.waiting=0
		if not self.waiting_search:
			self.edit_msg_label.set_name("WAITING_LABEL")
			self.edit_msg_label.set_text(_("Searching. Wait a moment..."))
			self.waiting_search=True
			self.cancel_btn.set_sensitive(False)
			self.save_btn.set_sensitive(False)
			GLib.timeout_add_seconds(1,self.pulsate_waiting_search)

	#def detect_changes
	
	def pulsate_waiting_search(self):

		 if self.waiting<1:
		 	self.waiting+=1
		 	return True

		 else:
		 	self.waiting_search=False
		 	self.cancel_btn.set_sensitive(True)
		 	self.save_btn.set_sensitive(True)
		 	self.edit_msg_label.set_text("")
		 	self.url_search_entry_changed()
		 	return False

	#def pulsate_waiting_search	


	def url_search_entry_changed(self):

	
		start=self.buffer.get_start_iter()
		end = self.buffer.get_end_iter()
		self.buffer.remove_tag(self.tag_found,start,end)
		self.count=0

		#cursor_mark = self.buffer.get_insert()
		#start = self.buffer.get_iter_at_mark(cursor_mark)

		if self.url_search_entry.get_text()!="":
			if start.get_offset() == self.buffer.get_char_count():
				start = self.buffer.get_start_iter()

			self.search_and_mark(self.url_search_entry.get_text(), start)
		
			
	#def _url_search_entry_changed
	
	def search_and_mark(self,text,start):

		try:
			
			end = self.buffer.get_end_iter()
			match = start.forward_search(text, Gtk.TextSearchFlags.CASE_INSENSITIVE, end)
			if match is not None:
				self.count+=1
				match_start, match_end = match
				self.buffer.apply_tag(self.tag_found, match_start, match_end)
				self.search_and_mark(text, match_end)
			else:
				if self.count==0:
					self.edit_msg_label.set_name("MSG_ERROR_LABEL")
					self.edit_msg_label.set_text(self.core.mainWindow.get_msg(28))
				else:
					#self.get_clipboard()
					self.edit_msg_label.set_name("MSG_CORRECT_LABEL")
					self.edit_msg_label.set_text(self.core.mainWindow.get_msg(29)%self.count)	
			
		except:

			pass		


	#def search_and_mark	
		

	def get_clipboard(self,wigdet=None):

		self.url_tw.set_property('editable',False)
		self.main_box.set_sensitive(False)
		self.core.mainWindow.lock_quit=True
		
		self.edit_spinner.start()
		self.edit_spinner_label.set_text(self.core.mainWindow.get_msg(32))			
		self.edit_spinner_label.set_name("WAITING_LABEL")
		
		self.stack_edit.set_transition_duration(550)
		self.stack_edit.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack_edit.set_visible_child_name("editWaiting")	
		
		self.init_threads()
		self.get_clipboard_content_t.start()
		GLib.timeout_add(100,self.pulsate_get_clipboard)

	#def get_clipboard	


	def pulsate_get_clipboard(self):


		if self.get_clipboard_content_t.is_alive():
			return True
					
		else:
			text_to_copy=self.clipboard_content['data']
			GLib.timeout_add(100,self.write_tw,True,text_to_copy)
			return False

	#def pulsate_get_clipboard			

		
	def get_clipboard_content(self):

		self.clipboard_content=self.core.guardmanager.get_clipboard_content()
		
	#def get_clipboard_content		

	def urltw_mouse_clicked(self,widget,event=None):

		if event.button==3:
			
			self.url_tw.set_property('editable',True)
		else:
			self.url_tw.set_property('editable',False)	

	#def urltw_mouse_clicked		
						
	def urltw_key_clicked(self,widget,event=None):

		self.url_tw.set_property('editable',True)	

	#def urltw_key_clicked				

#class EditBox

from . import Core
