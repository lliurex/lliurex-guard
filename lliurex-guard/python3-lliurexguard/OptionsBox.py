#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib

import sys
import os
import copy

from . import settings
import gettext
import threading
import datetime
import time

gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class OptionsBox(Gtk.VBox):
	
	WAITING_CHANGE_GUARDMODE_CODE=7
	WAITING_LOADING_LIST_CODE=11
	WAITING_LOADING_FILE_CODE=14
	WAITING_APPLY_CHANGES_CODE=17

	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-guard.css"
		self.manage_list_image=self.core.rsrc_dir+"manage_list.svg"
		self.blacklist_image=self.core.rsrc_dir+"blacklist_mode.svg"
		self.whitelist_image=self.core.rsrc_dir+"whitelist_mode.svg"

		self.main_box=builder.get_object("options_box")
		self.toolbar=builder.get_object("toolbar")
		self.option_separator=builder.get_object("option_separator")
		self.add_button=builder.get_object("add_button")
		self.global_management_button=builder.get_object("global_management_button")
		self.help_button=builder.get_object("help_button")
		self.search_entry=builder.get_object("search_entry")

		self.add_list_popover=builder.get_object("add_list_popover")
		self.add_custom_eb=builder.get_object("add_custom_eb")
		self.add_custom_label=builder.get_object("add_custom_label")
		self.add_file_eb=builder.get_object("add_file_eb")
		self.add_file_label=builder.get_object("add_file_label")

		self.global_management_popover=builder.get_object("global_management_popover")
		self.activate_all_eb=builder.get_object("activate_all_eb")
		self.activate_all_label=builder.get_object("activate_all_label")
		self.deactivate_all_eb=builder.get_object("deactivate_all_eb")
		self.deactivate_all_label=builder.get_object("deactivate_all_label")
		self.remove_all_eb=builder.get_object("remove_all_eb")
		self.remove_all_label=builder.get_object("remove_all_label")
		self.update_wl_dns_box=builder.get_object("update_wl_dns_box")
		self.update_wl_dns_eb=builder.get_object("update_wl_dns_eb")
		self.update_wl_dns_label=builder.get_object("update_wl_dns_label")

		self.mode_header_label=builder.get_object("mode_header_label")
		self.mode_set_label=builder.get_object("mode_set_label")
		self.mode_button=builder.get_object("mode_button")
		self.mode_button_image=builder.get_object("mode_button_img")
		self.mode_popover=builder.get_object("mode_popover")
		self.blackmode_box=builder.get_object("blackmode_box")
		self.blackmode_eb=builder.get_object("blackmode_eb")
		self.whitemode_box=builder.get_object("whitemode_box")
		self.whitemode_eb=builder.get_object("whitemode_eb")
		self.disablemode_box=builder.get_object("disablemode_box")
		self.disablemode_eb=builder.get_object("disablemode_eb")
				
		self.list_box=builder.get_object("list_box")
		self.list_box_sw=builder.get_object("list_box_scrolledwindow")
		self.list_box_vp=builder.get_object("list_box_viewport")
		self.list_item_box=builder.get_object("list_item_box")

		self.option_waiting_box=builder.get_object("option_waiting_box")
		self.option_spinner=builder.get_object("option_spinner")
		self.option_spinner_label=builder.get_object("option_spinner_label")

		self.feedback_msg_box=builder.get_object("feedback_msg_box")
		self.feedback_error_img=builder.get_object("feedback_error_img")
		self.feedback_ok_img=builder.get_object("feedback_ok_img")
		self.options_msg_label=builder.get_object("options_msg_label")
		self.options_pbar=builder.get_object("options_pbar")
		self.apply_btn=builder.get_object("apply_btn")
		
		self.stack_opt= Gtk.Stack()
		self.stack_opt.set_transition_duration(750)
		self.stack_opt.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack_opt.set_margin_top(0)
		self.stack_opt.set_margin_bottom(0)

		self.stack_opt.add_titled(self.list_box,"listBox","List Box")
		self.stack_opt.add_titled(self.option_waiting_box,"waitingBox","Waiting Box")
		self.stack_opt.show_all()
		self.main_box.pack_start(self.stack_opt,True,True,5)

		self.list_data={}
		self.search_list={}
		self.pack_start(self.main_box,True,True,0)
		self.set_css_info()
		self.init_threads()
		self.connect_signals()

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.add_custom_eb.set_name("POPOVER_OFF")
		self.add_file_eb.set_name("POPOVER_OFF")
		self.mode_button.set_name("EDIT_ITEM_BUTTON")
		self.search_entry.set_name("CUSTOM-ENTRY")
		self.mode_header_label.set_name("OPTION_LABEL")
		self.mode_set_label.set_name("OPTION_LABEL")
		self.list_item_box.set_name("WINDOW")

	#def set_css_info	

	def init_threads(self):

		self.load_list_info_t=threading.Thread()
		self.load_list_info_t.daemon=True
		self.load_file_t=threading.Thread()
		self.load_file_t.daemon=True
		self.write_tw_t=threading.Thread()
		self.write_tw_t.daemon=True
		self.apply_changes_t=threading.Thread()
		self.apply_changes_t.daemon=True
		self.change_guard_mode_t=threading.Thread()
		self.change_guard_mode_t.daemon=True
		self.open_help_t=threading.Thread(target=self.open_help)
		self.open_help_t.daemon=True
		self.update_wl_dns_t=threading.Thread()
		self.update_wl_dns_t.daemon=True

		GObject.threads_init()	

	#def init_threads		

	def connect_signals(self):

		self.add_button.connect("clicked",self.add_list)
		
		self.add_custom_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.add_custom_eb.connect("button-press-event", self.add_custom_list)
		self.add_custom_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.add_custom_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.add_file_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.add_file_eb.connect("button-press-event", self.add_file_list)
		self.add_file_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.add_file_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.global_management_button.connect("clicked",self.global_management)
		self.activate_all_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.activate_all_eb.connect("button-press-event", self.activate_all_lists,True)
		self.activate_all_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.activate_all_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.deactivate_all_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.deactivate_all_eb.connect("button-press-event", self.activate_all_lists,False)
		self.deactivate_all_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.deactivate_all_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.remove_all_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.remove_all_eb.connect("button-press-event", self.remove_all_lists)
		self.remove_all_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.remove_all_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.update_wl_dns_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.update_wl_dns_eb.connect("button-press-event", self.update_whitelists_dns)
		self.update_wl_dns_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.update_wl_dns_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.help_button.connect("clicked",self.help_clicked)

		self.search_entry.connect("changed",self.search_entry_changed)

		self.mode_button.connect("clicked",self.mode_button_clicked)
		self.blackmode_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.blackmode_eb.connect("button-press-event", self.change_mode,"BlackMode")
		self.blackmode_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.blackmode_eb.connect("leave-notify-event", self.mouse_exit_popover)
		
		self.whitemode_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.whitemode_eb.connect("button-press-event", self.change_mode,"WhiteMode")
		self.whitemode_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.whitemode_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.disablemode_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.disablemode_eb.connect("button-press-event", self.change_mode,"DisableMode")
		self.disablemode_eb.connect("motion-notify-event", self.mouse_over_popover)
		self.disablemode_eb.connect("leave-notify-event", self.mouse_exit_popover)

		self.apply_btn.connect("clicked",self.apply_btn_clicked)
		

	#def connect_signals	
			

	def set_mode(self):
	
		self.mode_button.set_name("GUARD_ENABLED_BUTTON")
		if self.core.mainWindow.guardMode=="BlackMode":
			img=Gtk.Image.new_from_file(self.blacklist_image)
			label=_("Black List mode")
		elif self.core.mainWindow.guardMode=="WhiteMode":	
			img=Gtk.Image.new_from_file(self.whitelist_image)
			label=_("White List mode")
		elif self.core.mainWindow.guardMode=="DisableMode":
			img=Gtk.Image.new_from_file(self.manage_list_image)
			label=_("Lliurex Guard is disabled")
			self.mode_button.set_name("GUARD_DISABLED_BUTTON")
		else:
			img=Gtk.Image.new_from_file(self.manage_list_image)
			label=_("Unknown mode")
			self.mode_button.set_name("GUARD_UNKNOWN_BUTTON")

		self.mode_button.set_image(img)
		self.mode_set_label.set_text(label)
		self._manage_mode_options()

	#def set_mode

	def _manage_mode_options(self):

		if  self.core.mainWindow.guardMode!="DisableMode":
			self.disablemode_box.show()
			if self.core.mainWindow.guardMode=="BlackMode":
				self.blackmode_box.hide()
				self.whitemode_box.show()
				self.add_button.set_sensitive(True)
				self.global_management_button.set_sensitive(True)
				self.update_wl_dns_box.hide()

			elif self.core.mainWindow.guardMode=="WhiteMode":
				self.blackmode_box.show()
				self.whitemode_box.hide()
				self.add_button.set_sensitive(True)
				self.global_management_button.set_sensitive(True)
				
				if not self.core.guardmanager.is_server and not self.core.guardmanager.is_client:
					self.update_wl_dns_box.show()
				else:
					self.update_wl_dns_box.hide()
				
						
			else:
				self.add_button.set_sensitive(False)
				self.global_management_button.set_sensitive(False)
				
		else:
			self.blackmode_box.show()
			self.whitemode_box.show()
			self.disablemode_box.hide()
			self.add_button.set_sensitive(False)
			self.global_management_button.set_sensitive(False)


	#def _manage_mode_options			

	def init_item_list(self):
	
		tmp=self.list_item_box.get_children()
		for item in tmp:
			self.list_item_box.remove(item)

	#def init_item_list
			

	def draw_list(self,action):

		self.init_item_list()

		search=False
		if action=="init":
			self.list_data=copy.deepcopy(self.core.mainWindow.list_info)
			
		elif action=="search":
			search=True

		if not search:	
			tmp_list=self.list_data
		
		else:
			tmp_list=self.search_list

		order_list=self.core.guardmanager.get_order_list(tmp_list)
		count=len(tmp_list)
		for item in order_list:
			self.new_item_box(item,count)
			count-=1		
		

	#def draw_list		

	def new_item_box(self,order,count,args=None):

		hbox=Gtk.HBox()
				
		vbox_list=Gtk.VBox()
		vbox_list.id=order
		hbox_list_data=Gtk.HBox()
		hbox_list_description=Gtk.VBox()
		name_box=Gtk.HBox()
		list_name=Gtk.Label()
		list_name.set_text(self.list_data[order]["name"]+": ")
		list_name.set_margin_left(10)
		list_name.set_margin_right(5)
		list_name.set_margin_top(0)
		list_name.set_margin_bottom(0)
		list_name.set_width_chars(40)
		list_name.set_max_width_chars(40)
		list_name.set_xalign(-1)
		list_name.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		list_name.set_name("LIST_NAME")
		list_name.set_valign(Gtk.Align.START)

		list_entries=Gtk.Label()
		list_entries.set_text(str(self.list_data[order]["lines"])+_(" entries"))
		list_entries.set_margin_left(10)
		list_entries.set_margin_right(5)
		list_entries.set_margin_top(0)
		list_entries.set_margin_bottom(0)
		list_entries.set_width_chars(20)
		list_entries.set_max_width_chars(20)
		list_entries.set_xalign(-1)
		list_entries.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		list_entries.set_name("LIST_LINE")
		list_entries.set_valign(Gtk.Align.START)
		name_box.pack_start(list_name,False,False,1)
		name_box.pack_start(list_entries,False,False,1)

		list_desc=Gtk.Label()
		list_desc.set_text(self.list_data[order]["description"])
		list_desc.set_margin_left(10)
		list_desc.set_margin_right(5)
		list_desc.set_margin_top(5)
		list_desc.set_margin_bottom(0)
		list_desc.set_width_chars(40)
		list_desc.set_max_width_chars(40)
		list_desc.set_xalign(-1)
		list_desc.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		list_desc.set_name("LIST_DESC")
		list_desc.set_valign(Gtk.Align.START)

		hbox_list_description.pack_start(name_box,False,False,1)
		hbox_list_description.pack_end(list_desc,False,False,1)

		activate_button=Gtk.CheckButton()
		activate_button.set_halign(Gtk.Align.CENTER)
		activate_button.set_valign(Gtk.Align.CENTER)
		activate_button.set_margin_top(5)


		if self.list_data[order]["active"]:
			activate_button.set_active(True)
			activate_button.set_tooltip_text(_("Click to disable the list"))
		else:
			activate_button.set_active(False)
			activate_button.set_tooltip_text(_("Click to enable the list"))

				
		activate_button.connect("toggled",self.list_toogled,hbox)


		manage_list=Gtk.Button()
		manage_image_list=Gtk.Image.new_from_file(self.manage_list_image)
		manage_list.add(manage_image_list)
		manage_list.set_margin_top(5)
		manage_list.set_margin_right(10)
		manage_list.set_halign(Gtk.Align.CENTER)
		manage_list.set_valign(Gtk.Align.CENTER)

		manage_list.set_name("EDIT_ITEM_BUTTON")
		manage_list.set_tooltip_text(_("Manage list"))
		manage_list.connect("clicked",self.manage_list_options,hbox)
		popover = Gtk.Popover()
		manage_list.popover=popover
		vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

		edit_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		edit_box.set_margin_left(10)
		edit_box.set_margin_right(10)
		edit_eb=Gtk.EventBox()
		edit_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		edit_eb.connect("button-press-event", self.edit_list_clicked,hbox)
		edit_eb.connect("motion-notify-event", self.mouse_over_popover)
		edit_eb.connect("leave-notify-event", self.mouse_exit_popover)
		edit_label=Gtk.Label()
		edit_label.set_text(_("Edit the list"))
		edit_eb.add(edit_label)
		edit_eb.set_name("POPOVER_OFF")
		edit_box.add(edit_eb)

		remove_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		remove_box.set_margin_left(10)
		remove_box.set_margin_right(10)
		remove_eb=Gtk.EventBox()
		remove_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		remove_eb.connect("button-press-event", self.delete_list_clicked,hbox)
		remove_eb.connect("motion-notify-event", self.mouse_over_popover)
		remove_eb.connect("leave-notify-event", self.mouse_exit_popover)
		remove_label=Gtk.Label()
		remove_label.set_text(_("Remove the list"))
		remove_eb.add(remove_label)
		remove_eb.set_name("POPOVER_OFF")
		remove_box.add(remove_eb)

		restore_box=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		restore_box.set_margin_left(10)
		restore_box.set_margin_right(10)
		restore_eb=Gtk.EventBox()
		restore_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		restore_eb.connect("button-press-event", self.restore_list_clicked,hbox)
		restore_eb.connect("motion-notify-event", self.mouse_over_popover)
		restore_eb.connect("leave-notify-event", self.mouse_exit_popover)
		restore_label=Gtk.Label()
		restore_label.set_text(_("Restore the list"))
		restore_eb.add(restore_label)
		restore_eb.set_name("POPOVER_OFF")
		restore_box.add(restore_eb)

		vbox.pack_start(edit_box, True, True,8)
		vbox.pack_start(remove_box,True,True,8)
		vbox.pack_start(restore_box,True,True,8)
		vbox.show_all()

		#restore_box.hide()
		popover.add(vbox)
		popover.set_position(Gtk.PositionType.BOTTOM)
		popover.set_relative_to(manage_list)
				
		hbox_list_data.pack_start(hbox_list_description,False,False,5)
		hbox_list_data.pack_end(manage_list,False,False,5)
		hbox_list_data.pack_end(activate_button,False,False,5)

		if self.list_data[order]["remove"]:
			hbox_list_data.set_name("REMOVE_BOX")
			remove_box.hide()
			restore_box.show()
		else:	
			hbox_list_data.set_name("APP_BOX")
			remove_box.show()
			restore_box.hide()

		list_separator=Gtk.Separator()
		list_separator.set_margin_top(5)
		list_separator.set_margin_left(10)
		list_separator.set_margin_right(10)

		if count!=1:
			list_separator.set_name("SEPARATOR")
		else:
			list_separator.set_name("WHITE_SEPARATOR")	

		vbox_list.pack_start(hbox_list_data,False,False,5)
		vbox_list.pack_end(list_separator,False,False,5)

		hbox.pack_start(vbox_list,True,True,5)
		hbox.show_all()
		hbox.set_halign(Gtk.Align.FILL)

		self.list_item_box.pack_start(hbox,False,False,1)
		self.list_item_box.queue_draw()
		self.list_item_box.set_valign(Gtk.Align.FILL)
		hbox.queue_draw()	

	#def new_item_box	

	def add_list(self,widget):

		self.manage_feedback_box(True,False)
		self.add_list_popover.show()

	#def add_list	

	def add_custom_list(self,widget,event=None):

		self.add_list_popover.hide()
		self.core.editBox.init_form()
		self.core.editBox.render_form(True)
		self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.core.mainWindow.stack_window.set_visible_child_name("editBox")	

	#def add_custom_list		

	def add_file_list(self,widget,event=None):

		self.add_list_popover.hide()

		dialog = Gtk.FileChooserDialog(_("Please choose a file to add new list"), None,
		Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
		Gtk.STOCK_OPEN, Gtk.ResponseType.OK))		
		self.add_filter(dialog)
		response=dialog.run()

		if response==Gtk.ResponseType.OK:
			file=dialog.get_filename()
			dialog.destroy()
			self.manage_waiting_form(OptionsBox.WAITING_LOADING_FILE_CODE)
			self.load_file_t=threading.Thread(target=self.load_file_info,args=(file,))
			self.load_file_t.start()
			GLib.timeout_add(100,self.pulsate_load_file)


		dialog.destroy()	


	#def add_file_list	

	def add_filter(self,dialog):

		filter_text = Gtk.FileFilter()
		filter_text.set_name("Text files")
		filter_text.add_mime_type("text/plain")
		dialog.add_filter(filter_text)

	#def add_filer	

	def pulsate_load_file(self):

		if self.load_file_t.is_alive():
			return True

		else:
			if self.read_file['status']:
				if self.read_file['data'][1]>0:
					self.core.editBox.init_form()
					
					if self.read_file['data'][1]<=self.core.guardmanager.limit_lines:
						self.core.editBox.render_form(True)
						GLib.timeout_add(100,self.core.editBox.write_tw,False,self.read_file['data'][0])
						return False
					else:
						self.option_spinner.stop()
						self.core.mainWindow.lock_quit=False
						self.core.editBox.render_form(False,self.read_file['data'][2])
						self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
						self.core.mainWindow.stack_window.set_visible_child_name("editBox")	
						self.core.editBox.stack_edit.set_visible_child_name("urlEditor")	
						return False
			else:
				self.option_spinner.stop()
				self.core.mainWindow.lock_quit=False
				self.main_box.set_sensitive(True)
				self.options_msg_label.set_text(self.core.mainWindow.get_msg(self.read_file['code'])+"\n"+self.read_file['data'])
				#self.options_msg_label.set_name("MSG_ERROR_LABEL")
				self.manage_feedback_box(False,True)
				self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.stack_opt.set_visible_child_name("listBox")
				return False			

	#def pulsate_load_file					

	def load_file_info(self,args):

		self.read_file=self.core.guardmanager.read_local_file(args,True)
	
	#def load_file_info	


	def global_management(self,widget,event=None):

		self.manage_feedback_box(True,False)
		self.global_management_popover.show()

	#def global_management	

	def activate_all_lists(self,widget,event,active):

		self.global_management_popover.hide()

		for item in self.list_item_box:
			item.get_children()[0].get_children()[0].get_children()[1].set_active(active)
		
		for item in self.list_data:
			self.list_data[item]["active"]=active
		
	#def activate_all_list

	def remove_all_lists(self,wiget,event):

		self.global_management_popover.hide()

		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Lliurex Guard")
		dialog.format_secondary_text(_("Do you want delete all lists?"))
		response=dialog.run()
		dialog.destroy()

		if response==Gtk.ResponseType.YES:

			for item in self.list_item_box:
				order=item.get_children()[0].id
				item.get_children()[0].get_children()[0].get_children()[2].popover.get_children()[0].get_children()[1].hide()
				item.get_children()[0].get_children()[0].get_children()[2].popover.get_children()[0].get_children()[2].show()
				item.get_children()[0].get_children()[0].set_name("REMOVE_BOX")
				self.list_data[order]["remove"]=True



	#def remove_all_lists	

	def update_whitelists_dns(self,widget,event):

		self.global_management_popover.hide()
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Lliurex Guard")
		dialog.format_secondary_text(_("Do you want to update white list dns?"))
		response=dialog.run()
		dialog.destroy()

		if response==Gtk.ResponseType.YES:
			list_data=copy.deepcopy(self.list_data)
			self.manage_waiting_form(36)
			self.update_wl_dns_t=threading.Thread(target=self.update_wl_dns,args=(list_data,))
			self.update_wl_dns_t.start()
			GLib.timeout_add(100,self.pulsate_update_wl_dns)

	#def update_whitelists_dns

	def pulsate_update_wl_dns(self):
	
		if self.update_wl_dns_t.is_alive():
			return True

		else:
			self.core.mainWindow.lock_quit=False
			self.main_box.set_sensitive(True)
			self.option_spinner.stop()
			self.stack_opt.set_transition_duration(550)
			self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
			self.stack_opt.set_visible_child_name("listBox")


			if self.result_update_wl_dns['status']:
				#self.options_msg_label.set_name("MSG_CORRECT_LABEL")
				self.manage_feedback_box(False,False)
				self.options_msg_label.set_text(self.core.mainWindow.get_msg(self.result_update_wl_dns['code']))
				self.list_data=self.result_update_wl_dns['data']

			else:
				self.manage_feedback_box(False,True)
				#self.options_msg_label.set_name("MSG_ERROR_LABEL")
				self.options_msg_label.set_text(self.core.mainWindow.get_msg(self.result_update_wl_dns['code'])+'\n'+self.result_update_wl_dns['data'])
	

	#def pulsate_update_wl_dns	

	def update_wl_dns(self,args):

		self.result_update_wl_dns=self.core.guardmanager.update_list_dns(args)

	#def update_wl_dns	


	def mode_button_clicked(self,widget,event=None):

		self.mode_popover.show()

	#def mode_button_clicked

	def change_mode(self,widget,event,mode):

		self.manage_feedback_box(True,False)
		self.mode_popover.hide()
		self.mode=mode
		if self.mode=="BlackMode":
			text=_("Do yo want to change to black list mode?\nIf you activate this mode, you will not be able to access the urls contained in the active lists")
		elif self.mode=="WhiteMode":
			text=_("Do yo want to change to white list mode?\nIf you activate this mode, you can only access the urls contained in the active lists")
		elif self.mode=="DisableMode":
			text=_("Do you want to deactivate LliureX Guard?\nIf you deactivate it, no filter will be applied")

		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Lliurex Guard")
		dialog.format_secondary_text(text)
		response=dialog.run()
		dialog.destroy()

		if response==Gtk.ResponseType.YES:
			self.manage_waiting_form(OptionsBox.WAITING_CHANGE_GUARDMODE_CODE)
			self.change_guard_mode_t=threading.Thread(target=self.change_guard_process,args=(self.mode,))
			self.change_guard_mode_t.start()
			GLib.timeout_add(100,self.pulsate_change_guard_mode)

		else:
			self.mode_popover.hide()
			
	#def change_mode			

	def pulsate_change_guard_mode(self):

		if self.change_guard_mode_t.is_alive():
			return True

		else:
			if self.result_mode['status']:
				self.core.mainWindow.load_info("mode")
				return False
				
			else:
				self.core.mainWindow.lock_quit=False
				self.option_spinner.stop()
				self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.stack_opt.set_visible_child_name("listBox")
				self.options_msg_label.set_text(self.core.mainWindow.get_msg(self.result_mode['code'])+'\n'+self.result_mode['data'])
				self.manage_feedback_box(False,True)
				#self.options_msg_label.set_name("MSG_ERROR_LABEL")
				#self.options_pbar.hide()
				return False			

	#def pulsate_change_guard_mode
	
	def change_guard_process(self,mode):

		self.result_mode=self.core.guardmanager.change_guardmode(mode)	

	#def change_guard_process		

	def list_toogled(self,widget,hbox):

		order=hbox.get_children()[0].id
		status_orig=self.list_data[order]["active"]
		status=not status_orig
		if status:
			hbox.get_children()[0].get_children()[0].get_children()[1].set_tooltip_text(_("Click to disable the list"))
		else:
			hbox.get_children()[0].get_children()[0].get_children()[1].set_tooltip_text(_("Click to enable the list"))


		self.list_data[order]["active"]=status

	#def list_toggled 	

	def manage_list_options(self,button,hbox,event=None):
		
		self.manage_feedback_box(True,False)
		button.popover.show()

	#def manage_list_options

	def delete_list_clicked(self,widget,event,hbox):

		hbox.get_children()[0].get_children()[0].get_children()[2].popover.hide()
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Lliurex Guard")
		dialog.format_secondary_text(_("Do you want delete the list?"))
		response=dialog.run()
		dialog.destroy()

		if response==Gtk.ResponseType.YES:
			hbox.get_children()[0].get_children()[0].get_children()[2].popover.get_children()[0].get_children()[1].hide()
			hbox.get_children()[0].get_children()[0].get_children()[2].popover.get_children()[0].get_children()[2].show()
			order=hbox.get_children()[0].id
			hbox.get_children()[0].get_children()[0].set_name("REMOVE_BOX")
			
			self.list_data[order]["remove"]=True
	
	#def delete_list_clicked	
	
	def restore_list_clicked(self,widget,event,hbox):

		hbox.get_children()[0].get_children()[0].get_children()[2].popover.hide()
		dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Lliurex Guard")
		dialog.format_secondary_text(_("Do you want restore the list?"))
		response=dialog.run()
		dialog.destroy()

		if response==Gtk.ResponseType.YES:
			hbox.get_children()[0].get_children()[0].get_children()[2].popover.get_children()[0].get_children()[1].show()
			hbox.get_children()[0].get_children()[0].get_children()[2].popover.get_children()[0].get_children()[2].hide()
			hbox.get_children()[0].get_children()[0].set_name("APP_BOX")
			order=hbox.get_children()[0].id
			self.list_data[order]["remove"]=False
			
	#def restore_list_clicked

	def edit_list_clicked(self,widget,event,hbox): 	

		#self.main_box.set_sensitive(False)
		hbox.get_children()[0].get_children()[0].get_children()[2].popover.hide()
		self.order=hbox.get_children()[0].id
		lines=self.list_data[self.order]["lines"]
		self.core.editBox.init_form()
		self.manage_waiting_form(OptionsBox.WAITING_LOADING_LIST_CODE)
		self.load_list_info_t=threading.Thread(target=self.load_list_info)
		self.load_list_info_t.start()
		GLib.timeout_add(100,self.pulsate_load_list_info,lines)


	#def edit_list_clicked

	def pulsate_load_list_info(self,lines):

		if self.load_list_info_t.is_alive():
			return True
		else:

			if self.read_list['status']:
				if lines<=self.core.guardmanager.limit_lines:
					self.core.editBox.render_form(True)
					GLib.timeout_add(100,self.core.editBox.write_tw,False)
					return False
				else:
					self.core.mainWindow.lock_quit=False
					self.option_spinner.stop()
					self.core.editBox.render_form(False,self.read_list['data'][1])
					self.core.editBox.load_values(self.order)
					self.core.mainWindow.stack_window.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
					self.core.mainWindow.stack_window.set_visible_child_name("editBox")		
					self.core.editBox.stack_edit.set_visible_child_name("urlEditor")
					return False
			else:
				self.core.mainWindow.lock_quit=False
				self.main_box.set_sensitive(True)
				self.options_msg_label.set_text(self.core.mainWindow.get_msg(self.read_list['code'])+"\n"+self.read_list['data'])
				self.manage_feedback_box(False,True)
				self.option_spinner.stop()
				self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.stack_opt.set_visible_child_name("listBox")
				return False		

	#def pulsate_load_info

	def load_list_info(self):
		
		self.read_list=self.core.guardmanager.read_guardmode_list(self.order,self.list_data)

	#def load_info		

	
	def apply_btn_clicked(self,widget):

		self.manage_waiting_form(OptionsBox.WAITING_APPLY_CHANGES_CODE)
		self.apply_changes_t=threading.Thread(target=self.apply_changes)
		self.apply_changes_t.start()
		GLib.timeout_add(100,self.pulsate_apply_changes)

	#def apply_btn_clicked

	def pulsate_apply_changes(self):

		if self.apply_changes_t.is_alive():
			return True

		else:
			self.core.mainWindow.lock_quit=False
			if self.result_apply['status']:
				self.core.mainWindow.load_info("apply")
				return False
				
			else:
				self.option_spinner.stop()
				self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
				self.stack_opt.set_visible_child_name("listBox")
				self.options_msg_label.set_text(self.core.mainWindow.get_msg(self.result_apply['code'])+"\n"+self.result_apply['data'])
				self.manage_feedback_box(False,True)
				#self.options_msg_label.set_name("MSG_ERROR_LABEL")	
				if self.result_apply['code']!=10:
					self.main_box.set_sensitive(True)
				return False
				
	#def pulsat_apply_changes
	
	def apply_changes(self):

		self.result_apply=self.core.guardmanager.apply_changes(self.list_data,self.core.mainWindow.list_info)
	
	#def apply_changes		

	def search_entry_changed(self,widget):

		self.search_list={}
		self.search_list=self.list_data.copy()
		
		search=self.search_entry.get_text().lower()
		
		if search=="":
			self.draw_list("edit")
		else:
			self.manage_feedback_box(True,False)
			for item in self.list_data:
				name=self.list_data[item]["name"].lower()
				desc=self.list_data[item]["description"].lower()
				if search in name:
					pass
				elif search in desc:
					pass
				else:
					self.search_list.pop(item)

			if len(self.search_list)>0:
				self.draw_list("search")	

	#def search_entry_changed				

	def help_clicked(self,widget):

		lang=os.environ["LANG"]

		if 'ca_ES' in lang:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Guard+en+Lliurex.'
		else:
			self.help_cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex-Guard-en-Lliurex'

		self.init_threads()
		self.open_help_t.start()

	#def help_clicked	

	def open_help(self):

		os.system(self.help_cmd)

	#def open_help	

	def mouse_over_popover(self,widget,event=None):

		widget.set_name("POPOVER_ON")

	#def mouser_over_popover	

	def mouse_exit_popover(self,widget,event=None):

		widget.set_name("POPOVER_OFF")		
	
	#def mouse_exit_popover

	def manage_waiting_form(self,msg_code):

		self.main_box.set_sensitive(False)
		self.core.mainWindow.lock_quit=True
		self.manage_feedback_box(True,False)
		self.options_msg_label.set_text("")
		self.option_spinner_label.set_name("WAITING_LABEL")
		self.option_spinner_label.set_text(self.core.mainWindow.get_msg(msg_code))
		self.option_spinner.start()
		self.stack_opt.set_transition_duration(150)
		self.stack_opt.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack_opt.set_visible_child_name("waitingBox")
		self.init_threads()

	#def manage_waiting_form

	def manage_feedback_box(self,hide,error):

		if hide:
			self.feedback_msg_box.set_name("HIDE_BOX")
			self.feedback_error_img.hide()
			self.feedback_ok_img.hide()
			self.options_msg_label.set_text("")
		else:
			if error:
				self.feedback_msg_box.set_name("ERROR_BOX")
				self.feedback_error_img.show()
				self.feedback_ok_img.hide()
			else:
				self.feedback_msg_box.set_name("SUCCESS_BOX")
				self.feedback_error_img.hide()
				self.feedback_ok_img.show()
			self.options_msg_label.set_name("FEEDBACK_LABEL")


	#def manage_feedback_box



	
#class OptionsBox

from . import Core
