#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import os
import json
import codecs
import datetime
import glob
import unicodedata
import subprocess
import tempfile
import time
import re
import sys
import syslog
import urllib.request
from os import listdir
from os.path import isfile,isdir,join
from jsondiff import diff
import n4d.client

class GuardManager(object):

	MISSING_LIST_NAME_ERROR=-1
	LIST_NAME_DUPLICATE=-2
	SAVING_FILE_ERROR=-5
	CHANGE_GUARDMODE_ERROR=-9
	RESTARTING_DNSMASQ_ERROR=-10
	READ_LIST_INFO_ERROR=-13
	LOADING_FILE_ERROR=-16
	REMOVING_LIST_ERROR=-19
	ACTIVATING_LIST_ERROR=-20
	DEACTIVATING_LIST_ERROR=-21
	READ_GUARDMODE_ERROR=-23
	READ_GUARDMODE_HEADERS_ERROR=-25
	EMPTY_FILE_ERROR=-27
	LOAD_FILE_SIZE_OFF_LIMITS_ERROR=-30
	EDIT_FILE_OFF_LIMITS_ERROR=-31
	LINES_TO_COPY_OFF_LIMITS_ERROR=-33
	READ_FILE_ERROR=-34

	ALL_CORRECT_CODE=0
	CHANGE_GUARDMODE_SUCCESSFUL=8
	READ_LIST_INFO_SUCCESSFUL=12
	LOAD_FILE_SUCCESSFUL=15
	CHANGES_APPLIED_SUCCESSFUL=18
	READ_GUARDMODE_SUCCESSFUL=22
	READ_GUARDMODE_HEADERS_SUCCESSFUL=24
	READ_FILE_SUCCESSFUL=35


	def __init__(self,server=None):

		super(GuardManager, self).__init__()

		self.dbg=0
		self.user_validated=False
		self.user_groups=[]
		self.validation=None
		self.limit_lines=2500
		self.limit_file_size=28000000
		self.garbage_files=[]

		self.detect_flavour()

		'''
		if server!=None:
			self.set_server(server)
		
		context=ssl._create_unverified_context()
		self.n4d_local = n4dclient.ServerProxy("https://localhost:9779",context=context,allow_none=True)	
		'''
	
	#def __init__	
	
	'''
	def set_server(self):	
		
		self.server_ip=server
		context=ssl._create_unverified_context()	
		self.n4d=n4dclient.ServerProxy("https://"+self.server_ip+":9779",context=context,allow_none=True)
	
	'''
	#def set_server
		
	def detect_flavour(self):
		
		self.is_server=""
		self.is_client=""
		self.is_desktop=""

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]

		for item in flavours:
			if 'server' in item:
				self.is_server=True
				self.is_desktop=False
				break
			elif 'client' in item:
				self.is_client=True
				self.is_desktop=False
				break
			elif 'desktop' in item:
				self.is_desktop=True	

	#def detect_flavour

	def validate_user(self,server,user,password):
		
		try:
			self.server_ip=server
			self.client=n4d.client.Client("https://%s:9779"%server,user,password)

			ret=self.client.validate_user()
			self.user_validated=ret[0]
			self.user_groups=ret[1]
			self.credentials=[user,password]
		
			if self.user_validated:
				session_user=os.environ["USER"]
				self.ticket=self.client.get_ticket()
				if self.ticket.valid():
					self.client=n4d.client.Client(ticket=self.ticket)
					msg_log="Session User: %s"%session_user+" LlxGuard User: %s"%user
					self.write_log(msg_log)
					
					self.local_client=n4d.client.Client("https://localhost:9779",user,password)
					local_t=self.local_client.get_ticket()
					if local_t.valid():
						self.local_client=n4d.client.Client(ticket=local_t)
					else:
						self.user_validated=False	
				else:
					self.user_validated=False

		except Exception as e:
			msg_log="Session User Error: %s"%(str(e))
			self.write_log(msg_log)
			self.user_validated=False
	
		#return self.user_validated
		
	#def validate_user

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[LLIUREX_GUARD]: "+ str(function) + str(msg))

	#def _debug		

	def read_guardmode(self):
			
		read_guardmode=self.client.LliurexGuardManager.read_guardmode(True)
		msg="Read LliureX Guard Mode: "
		self._debug(msg,read_guardmode)
		msg_log=msg+str(read_guardmode)
		self.write_log(msg_log)
		if read_guardmode['status']:
			return {'status':True,'code':GuardManager.READ_GUARDMODE_SUCCESSFUL,'data':read_guardmode['data']}
		else:
			return {'status':False,'code':GuardManager.READ_GUARDMODE_ERROR,'data':read_guardmode['data']}

	#def read_guardmode

	def change_guardmode(self,mode):

		change_guardmode=self.client.LliurexGuardManager.change_guardmode(mode)
		msg="LliureX Guard Mode changed to %s"%mode
		self._debug(msg,change_guardmode)
		msg_log=msg+str(change_guardmode)
		self.write_log(msg_log)
		
		if change_guardmode['status']:
			msg="LliureX Guard Mode changed. Dnsmasq restarted "
			restart_dnsmasq=self.restart_dnsmasq(msg)
			if restart_dnsmasq['status']:
				return {'status':True,'code':GuardManager.CHANGE_GUARDMODE_SUCCESSFUL}
			else:
				return {'status':False,'code':GuardManager.RESTARTING_DNSMASQ_ERROR,'data':restart_dnsmasq['data']}	
		else:
			return {'status':False,'code':GuardManager.CHANGE_GUARDMODE_ERROR,'data':change_guardmode['data']}		
				
	#def change_guardmode 		

	def read_guardmode_headers(self):

		read_guardmode_headers=self.client.LliurexGuardManager.read_guardmode_headers()
		msg="LliureX Guard mode lists readed "
		self._debug(msg,read_guardmode_headers)
		msg_log=msg+str(read_guardmode_headers)
		self.write_log(msg_log)
		if read_guardmode_headers['status']:
			tmp_list=read_guardmode_headers['data']
			for item in tmp_list:
				#tmp_list[item]['edited']=False
				tmp_list[item]['remove']=False
				tmp_list[item]["replaced_to"]=""
				tmp_list[item]["tmpfile"]=""

			return {'status':True,'code':GuardManager.READ_GUARDMODE_HEADERS_SUCCESSFUL,'data':tmp_list}	

		else:
			return {'status':False,'code':GuardManager.READ_GUARDMODE_HEADERS_ERROR,'data':str(read_guardmode_headers['data'])}
		

	#def read_guardmode_headers	

	def read_guardmode_list(self,order,data):
			
		tmpfile=False
		status=True
		tmp_file=""
		lines=[]
		error_info=[]
		listId=data[order]["id"]
		if data[order]["tmpfile"]!="":
			read_tmp_file=self.read_local_file(data[order]["tmpfile"],False)
			msg="List %s. Readed local file (%s)"%(listId,data[order]["tmpfile"])
			self._debug(msg,read_tmp_file)
			if read_tmp_file['status']:
				content=read_tmp_file['data'][0]
				count_lines=read_tmp_file['data'][1]
				tmpfile=True

			else:
				status=False
				error_info=read_tmp_file['data']
		else:
			read_guardmode_list=self.client.LliurexGuardManager.read_guardmode_list(listId,data[order]['active'])
			msg="List %s. Readed file"%listId
			self._debug(msg,read_guardmode_list)
			if read_guardmode_list['status']:
				content=read_guardmode_list['data'][0]
				count_lines=read_guardmode_list['data'][1]
			else:
				status=False
				error_info=read_guardmode_list['data']
			read_guardmode_list=None	
		if status:
			code=GuardManager.READ_LIST_INFO_SUCCESSFUL		
			if count_lines>self.limit_lines:
				if not tmpfile:
					tmp_file=self._create_tmp_file(listId)
					f=open(tmp_file,'w')
					tmp_content="".join(content)
					f.write(tmp_content)
					f.close()
					tmp_content=None
					self.garbage_files.append(tmp_file)
				else:
					tmp_file=read_tmp_file['data'][2]	
				content=None
				read_tmp_file=None	
			result=[content,tmp_file]
			msg_log=msg + " successfully"
		else:
			code=GuardManager.READ_LIST_INFO_ERROR
			result=error_info
			msg_log=msg+ "with errors. Error details: "+str(error_info)
		
		self.write_log(msg_log)
		return {'status':status,'code':code,'data':result}

	#def read_guardmode_list	
			
	def read_local_file(self,file,create_tmpfile):

		content=[]
		count_lines=0
		tmp_file=""
		try:
			if os.path.exists(file) and os.path.getsize(file)>0:
				if create_tmpfile:
					if os.path.getsize(file)>self.limit_file_size:
						return {'status':False,'code':GuardManager.LOAD_FILE_SIZE_OFF_LIMITS_ERROR,'data':''}	
				f=open(file,'r')
				lines=f.readlines()
				for line in lines:
					if "NAME" not in line:
						if "DESCRIPTION" not in line:
							if line !="":
								line=self._format_line(line)
								content.append(line)	
								count_lines+=1
				f.close()
				lines=None
				tmp_file=file
				
				if create_tmpfile:
					tmp_file=self._create_tmp_file(os.path.basename(file))
					f=open(tmp_file,'w')
					f.write("".join(content))
					f.close()
					if count_lines>self.limit_lines:
						content=None

				self.garbage_files.append(tmp_file)		

				return {'status':True,'code':GuardManager.LOAD_FILE_SUCCESSFUL,'data':[content,count_lines,tmp_file]}
			else:
				return {'status':False,'code':GuardManager.EMPTY_FILE_ERROR,'data':''}	

		except Exception as e:		
			return {'status':False,'code':GuardManager.LOADING_FILE_ERROR,'data':str(e)}

	#def read_local_file		

	def save_conf(self,args):

		error=False
		result={}
		info=args[0]
		content=args[1]
		try:
			if args[2]==None:
				tmp_list=self._create_tmp_file(info["id"])
				self.garbage_files.append(tmp_list)
			else:
				tmp_list=args[2]

			if content=="":
				tmp_content=[]
				f=open(tmp_list,'r')
				lines=f.readlines()
				f.close()
				f=open(tmp_list,'w')
				for line in lines:
					if line!="":
						line=self._format_line(line)
						f.write(line)
		
				f.close()		
				result["lines"]=len(lines)
			else:
				format_content=[]	
				content=content.split("\n")	
				for line in content:
					if line !="":
						line=self._format_line(line)
						format_content.append(line+"\n")	
				f=open(tmp_list,"w")
				f.write("".join(format_content))
				f.close()
			content=None
			format_content=None
			result["status"]=True
			result["tmpfile"]=tmp_list
			
		except Exception as e:
			result['status']=False
			result['code']=GuardManager.SAVING_FILE_ERROR
			result['data']=str(e)
		
		msg="List %s. Saved changes "%info["id"]
		self._debug(msg,result)
		msg_log=msg+" "+str(result)	
		self.write_log(msg_log)

		return result
			

			
	#def save_conf		

	def check_data(self,list_data,data,edit,loaded_file,orig_id=None):

		if data["name"]=="":
			return {"result":False,"code":GuardManager.MISSING_LIST_NAME_ERROR,"data":""}

		else:
			check_duplicates=True
			if edit:
				if data["id"]==orig_id:
					check_duplicates=False

			if check_duplicates:		
				for item in list_data:
					if list_data[item]["id"]==data["id"]:
						return {"result":False,"code":GuardManager.LIST_NAME_DUPLICATE,"data":""}

			if loaded_file !=None:
				if os.path.getsize(loaded_file)>self.limit_file_size:
					return {'result':False,'code':GuardManager.EDIT_FILE_SIZE_OFF_LIMITS_ERROR,'data':''}			

		return {"result":True,"code":GuardManager.ALL_CORRECT_CODE}			
			 			
	#def check_data
	
	def get_listId(self,name):

		listId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		listId=listId.lower().replace(" ","_")
		listId=re.sub('[^\w\s-]', '', listId).strip()
		listId=re.sub('[-\s]+', '-', listId)

		return listId

	#def get_siteId

	def get_order_list(self,info):

		tmp=[]
		order_list=[]

		for item in info:
			name=info[item]["name"].lower()
			x=()
			x=item,name
			tmp.append(x)

		tmp.sort(key=lambda list:list[1])
		for	item in tmp:
			order_list.append(item[0])

		return order_list

	#def get_order_list		


	def apply_changes(self,list_data,orig_data):

		list_to_remove=[]
		list_to_active=[]
		list_to_deactive=[]
		self.tmpfile_list=[]
		error=False
		code=""
		data=""

		if len(orig_data)==0:
			changes=list_data.keys()
		else:	
			changes=diff(orig_data,list_data).keys()

		if len(changes)>0:
			for item in list_data:
				if item in changes:	
					if list_data[item]["remove"]:
						list_to_remove.append(list_data[item]["id"])
						continue

							
					if list_data[item]["active"]:
						if list_data[item]["tmpfile"]!="":
							#self.tmpfile_list.append(list_data[item]["tmpfile"])
							if self.is_client:
								send=self.send_tmpfile_toserver(list_data[item]["tmpfile"])
									
						list_to_active.append(list_data[item])
									
									
					if not list_data[item]["active"]:
						if list_data[item]["tmpfile"]!="":
							#self.tmpfile_list.append(list_data[item]["tmpfile"])
							if self.is_client:
								send=self.send_tmpfile_toserver(list_data[item]["tmpfile"])
								
						list_to_deactive.append(list_data[item])

					if list_data[item]["replaced_to"]!="":
						orig_name=list_data[item]["replaced_to"]
						list_to_remove.append(orig_name)
			
			if len(list_to_remove)>0:
				result_remove=self.client.LliurexGuardManager.remove_guardmode_list(list_to_remove)	
				msg="Applied Changes.Removed list "
				self._debug(msg,result_remove)
				msg_log=msg+str(result_remove)+". List removed: "+str(list_to_remove)
				self.write_log(msg_log)
				if not result_remove['status']:
					error=True
					code=GuardManager.REMOVING_LIST_ERROR
					data=result_remove['data']

			if not error:
				if len(list_to_active)>0:
						result_active=self.client.LliurexGuardManager.activate_guardmode_list(list_to_active)	
						msg="Applied Changes.Actived list "
						self._debug(msg,result_active)
						msg_log=msg+str(result_active)+". List actived: "+str(list_to_active)
						self.write_log(msg_log)

						if not result_active['status']:
							error=True
							code=GuardManager.ACTIVATING_LIST_ERROR
							data=result_active['data']

				if not error:
					if len(list_to_deactive)>0:
						result_deactive=self.client.LliurexGuardManager.deactivate_guardmode_list(list_to_deactive)	
						msg="Applied Changes.Deactived lists "
						self._debug(msg,result_deactive)
						msg_log=msg+str(result_deactive)+". List deactived: "+str(list_to_deactive)
						self.write_log(msg_log)
						if not result_deactive['status']:
							error=True
							code=GuardManager.DEACTIVATING_LIST_ERROR
							data=result_deactive['data']

			if not error:
				#self.remove_tmp_file(tmpfile_list)
				msg="Lliurex Guard applied changes. Dnsmasq restart"
				restart_dnsmasq=self.restart_dnsmasq(msg)
				if restart_dnsmasq['status']:
					return {'status':True,'code':GuardManager.CHANGES_APPLIED_SUCCESSFUL}
				else:
					'''
					disable_llxguard=self.n4d.change_guardmode(self.validation,"LliurexGuardManager","DisableMode")
					if disable_llxguard['status']:
						restart=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")
					'''
					return {'status':False,'code':GuardManager.RESTARTING_DNSMASQ_ERROR,'data':restart_dnsmasq['data']}
			else:
				return {'status':False,'code':code,'data':data}									

		else:
			return {'status':True,'code':GuardManager.ALL_CORRECT_CODE}						

	#def apply_changes

	def restart_dnsmasq(self,msg):

		restart_dnsmasq=self.client.LliurexGuardManager.restart_dnsmasq()
		self.connection=False
		self.timeout=120
		self.count=0

		while not self.connection:
			time.sleep(1)
			try:
				if self.is_server or self.is_client:
					res=urllib.request.urlopen("http://"+self.server_ip)
				self.connection=True
			except Exception as e:
				if self.count<self.timeout:
					self.count+=1
				else:
					msg_log="Lliurex Guard checking connection with server. Time Out. Error:%s"%str(e)
					self.write_log(msg_log)
					self.connection=True

			
		#self.set_server(self.server_ip)	
		self.client=n4d.client.Client(ticket=self.ticket)
		self._debug(msg,restart_dnsmasq)
		msg_log=msg+str(restart_dnsmasq)
		self.write_log(msg_log)
		
		return restart_dnsmasq				

	#def restart_dnsmasq()	

	def send_tmpfile_toserver(self,tmp_file):

		send_tmpfile=self.local_client.ScpManager.send_file(self.credentials[0],self.credentials[1],"server",tmp_file,"/tmp")
		msg_log="Send tmp file %s to server"%tmp_file+ " "+str(send_tmpfile)	
		self.write_log(msg_log)
		
		return send_tmpfile

	#def send_tmpfile_toserver		

	def _create_tmp_file(self,listId):
	
		tmp_file=tempfile.mkstemp("_"+listId)
		tmp_file=tmp_file[1]
		
		return tmp_file

	#def _create_tmp_file	

	def remove_tmp_file(self):

		'''
		if "client" in self.flavours:
			for item in self.tmpfile_list:
				if os.path.exists(item):
					os.remove(item)
		'''
		for item in self.garbage_files:
			if os.path.exists(item):
				os.remove(item)
		
		self.garbage_files=[]	

		self.client.LliurexGuardManager.remove_tmp_file()			

		
	#def _remove_tmp_file	

	def write_log(self,msg):
	
		syslog.openlog("LLIUREX-GUARD")
		syslog.syslog(msg)	

	#def write_log	

	def _format_line(self,line):

		firstchar=line[0]
		
		if firstchar in [".","_","-","+","*","$"," ","&","!","¡","#","%","?","¿"]:
			line=line[1:]
		
		return line

	#def _format_line

	def get_clipboard_content(self):

		text_to_copy=[]
		code=""
		
		try:
			p = subprocess.Popen(['xclip','-selection', 'clipboard', '-o'], stdout=subprocess.PIPE)
			data=p.communicate()[0]
		except Exception as e:
			print (str(e))
			data=""
	
		if type(data) is bytes:
			result=data.decode()
		else:
			result=data
		
		if result!="":	
			text=result.split("\n")
			   		
			if len(text)<=self.limit_lines:
				for item in text:
					text_to_copy.append(item+"\n")
				
			else:
				count=0
				code=GuardManager.LINES_TO_COPY_OFF_LIMITS_ERROR
			
				for item in text:
					if count<2500:
						text_to_copy.append(item+"\n")
						count+=1
					else:
						break

		return {'status':True,'code':code,'data':text_to_copy} 	

	#def get_clipboard_content				

	def update_list_dns(self,list_data):

		status=True
		error_info=[]
		code=""
		for item in list_data:
			read_guardmode_list=self.client.LliurexGuardManager.read_guardmode_list(list_data[item]["id"],list_data[item]['active'])
			if read_guardmode_list['status']:
				content=read_guardmode_list['data'][0]
				count_lines=read_guardmode_list['data'][1]
				tmp_file=self._create_tmp_file(list_data[item]["id"])
				f=open(tmp_file,'w')
				tmp_content="".join(content)
				f.write(tmp_content)
				f.close()
				tmp_content=None
				self.garbage_files.append(tmp_file)
				list_data[item]["tmpfile"]=tmp_file

			else:
				status=False
				code=GuardManager.READ_FILE_ERROR
				error_info=read_guardmode_list['data']
				break

		if status:
			code=GuardManager.READ_FILE_SUCCESSFUL
			result=list_data
		else:
			result=error_info

		return {'status':status,'code':code,'data':result}
		
				

	#def update_list_dns	

#class GuardManager
