#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, GLib
import os
import json
import codecs
import datetime
import xmlrpc.client as n4dclient
import ssl
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


class GuardManager(object):

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

		if server!=None:
			self.set_server(server)

		context=ssl._create_unverified_context()
		self.n4d_local = n4dclient.ServerProxy("https://localhost:9779",context=context,allow_none=True)	
			
	
	#def __init__	
	

	def set_server(self,server):	
		
		self.server_ip=server
		context=ssl._create_unverified_context()	
		self.n4d=n4dclient.ServerProxy("https://"+self.server_ip+":9779",context=context,allow_none=True)
	
	#def set_server
		
	def detect_flavour(self):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		self.flavours = [ x.strip() for x in result.split(',') ]

	#def detect_flavour

	def validate_user(self,user,password):
		
		ret=self.n4d.validate_user(user,password)
		self.user_validated,self.user_groups=ret
			
		
		if self.user_validated:
			self.validation=(user,password)
			session_user=os.environ["USER"]
			msg_log="Session User: %s"%session_user+" LlxGuard User: %s"%self.validation[0]
			self.write_log(msg_log)

					
		#return self.user_validated
		
	#def validate_user

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[LLIUREX_GUARD]: "+ str(function) + str(msg))

	#def _debug		

	def read_guardmode(self):

		'''
		Result code:
			-22:Mode readed successfully
			-23:Error reading mode
		'''
			
		read_guardmode=self.n4d.read_guardmode(self.validation,"LliurexGuardManager",True)
		msg="Read LliureX Guard Mode: "
		self._debug(msg,read_guardmode)
		msg_log=msg+str(read_guardmode)
		self.write_log(msg_log)
		if read_guardmode['status']:
			return {'status':True,'code':22,'data':read_guardmode['data']}
		else:
			return {'status':False,'code':23,'data':read_guardmode['data']}

	#def read_guardmode

	def change_guardmode(self,mode):

		'''
		Result code:
			-8: Guard mode changed successfully
			-9: Error changing guard mode
			-10: Error restarting dnsmasq
	
		'''	

		change_guardmode=self.n4d.change_guardmode(self.validation,"LliurexGuardManager",mode)
		msg="LliureX Guard Mode changed to %s"%mode
		self._debug(msg,change_guardmode)
		msg_log=msg+str(change_guardmode)
		self.write_log(msg_log)
		
		if change_guardmode['status']:
			msg="LliureX Guard Mode changed. Dnsmasq restarted "
			restart_dnsmasq=self.restart_dnsmasq(msg)
			if restart_dnsmasq['status']:
				return {'status':True,'code':8}
			else:
				'''
				disable_llxguard=self.n4d.change_guardmode(self.validation,"LliurexGuardManager","DisableMode")
				if disable_llxguard['status']:
					restart=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")
				'''	
				return {'status':False,'code':10,'data':restart_dnsmasq['data']}	
		else:
			return {'status':False,'code':9,'data':change_guardmode['data']}		
				
	#def change_guardmode 		

	def read_guardmode_headers(self):

		'''
		Result code:
			-24: List headers readed successfully
			-25: Error reading list files
			'''			

		read_guardmode_headers=self.n4d.read_guardmode_headers(self.validation,"LliurexGuardManager")
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

			return {'status':True,'code':24,'data':tmp_list}	

		else:
			return {'status':False,'code':25,'data':str(read_guardmode_headers['data'])}
		

	#def read_guardmode_headers	

	def read_guardmode_list(self,order,data):

		'''
		Result code:
			-12: List info readed successfully
			-13: Error reading list info
		'''
			
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
			read_guardmode_list=self.n4d.read_guardmode_list(self.validation,"LliurexGuardManager",listId,data[order]['active'])
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
			code=12		
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
			code=13
			result=error_info
			msg_log=msg+ "with errors. Error details: "+str(error_info)
		
		self.write_log(msg_log)
		return {'status':status,'code':code,'data':result}

	#def read_guardmode_list	
			
	def read_local_file(self,file,create_tmpfile):

		'''
		Result code:
			-15: File loaded successfully
			-16: Error loading file info
			-27: Empty file
			-30: Size of file off limit
		'''

		content=[]
		count_lines=0
		tmp_file=""
		try:
			if os.path.exists(file) and os.path.getsize(file)>0:
				if create_tmpfile:
					if os.path.getsize(file)>self.limit_file_size:
						return {'status':False,'code':30,'data':''}	
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

				return {'status':True,'code':15,'data':[content,count_lines,tmp_file]}
			else:
				return {'status':False,'code':27,'data':''}	

		except Exception as e:		
			return {'status':False,'code':16,'data':str(e)}

	#def read_local_file		

	def save_conf(self,args):

		'''
		Result code:
			-5: Error saving list info
		'''

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
			result['code']=5
			result['data']=str(e)
		
		msg="List %s. Saved changes "%info["id"]
		self._debug(msg,result)
		msg_log=msg+" "+str(result)	
		self.write_log(msg_log)

		return result
			

			
	#def save_conf		

	def check_data(self,list_data,data,edit,loaded_file,orig_id=None):

		'''
		Result code:
			-1: Missing list name
			-2: List name duplicate
			-30: Size file off limit
 	
		'''	

		if data["name"]=="":
			return {"result":False,"code":1,"data":""}

		else:
			check_duplicates=True
			if edit:
				if data["id"]==orig_id:
					check_duplicates=False

			if check_duplicates:		
				for item in list_data:
					if list_data[item]["id"]==data["id"]:
						return {"result":False,"code":2,"data":""}

			if loaded_file !=None:
				if os.path.getsize(loaded_file)>self.limit_file_size:
					return {'result':False,'code':31,'data':''}			

		return {"result":True,"code":0}			
			 			
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


		'''
		Result code:
			-18: Changes applied successfully
			-19: Error removing list
			-20: Error activating list
			-21: Error deactivating list
		'''	

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
							if "client" in self.flavours:
								send=self.send_tmpfile_toserver(list_data[item]["tmpfile"])
									
						list_to_active.append(list_data[item])
									
									
					if not list_data[item]["active"]:
						if list_data[item]["tmpfile"]!="":
							#self.tmpfile_list.append(list_data[item]["tmpfile"])
							if "client" in self.flavours:
								send=self.send_tmpfile_toserver(list_data[item]["tmpfile"])
								
						list_to_deactive.append(list_data[item])

					if list_data[item]["replaced_to"]!="":
						orig_name=list_data[item]["replaced_to"]
						list_to_remove.append(orig_name)
			
			if len(list_to_remove)>0:
				result_remove=self.n4d.remove_guardmode_list(self.validation,"LliurexGuardManager",list_to_remove)	
				msg="Applied Changes.Removed list "
				self._debug(msg,result_remove)
				msg_log=msg+str(result_remove)+". List removed: "+str(list_to_remove)
				self.write_log(msg_log)
				if not result_remove['status']:
					error=True
					code=19
					data=result_remove['data']

			if not error:
				if len(list_to_active)>0:
						result_active=self.n4d.activate_guardmode_list(self.validation,"LliurexGuardManager",list_to_active)	
						msg="Applied Changes.Actived list "
						self._debug(msg,result_active)
						msg_log=msg+str(result_active)+". List actived: "+str(list_to_active)
						self.write_log(msg_log)

						if not result_active['status']:
							error=True
							code=20
							data=result_active['data']

				if not error:
					if len(list_to_deactive)>0:
						result_deactive=self.n4d.deactivate_guardmode_list(self.validation,"LliurexGuardManager",list_to_deactive)	
						msg="Applied Changes.Deactived lists "
						self._debug(msg,result_deactive)
						msg_log=msg+str(result_deactive)+". List deactived: "+str(list_to_deactive)
						self.write_log(msg_log)
						if not result_deactive['status']:
							error=True
							code=21
							data=result_deactive['data']

			if not error:
				#self.remove_tmp_file(tmpfile_list)
				msg="Lliurex Guard applied changes. Dnsmasq restart"
				restart_dnsmasq=self.restart_dnsmasq(msg)
				if restart_dnsmasq['status']:
					return {'status':True,'code':18}
				else:
					'''
					disable_llxguard=self.n4d.change_guardmode(self.validation,"LliurexGuardManager","DisableMode")
					if disable_llxguard['status']:
						restart=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")
					'''
					return {'status':False,'code':10,'data':restart_dnsmasq['data']}
			else:
				return {'status':False,'code':code,'data':data}									

		else:
			return {'status':True,'code':0}						

	#def apply_changes

	def restart_dnsmasq(self,msg):

		restart_dnsmasq=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")
		self.connection=False
		self.timeout=120
		self.count=0

		while not self.connection:
			time.sleep(1)
			try:
				if 'server' in self.flavours and 'client' in self.flavours:
					res=urllib.request.urlopen("http://"+self.server_ip)
				self.connection=True
			except Exception as e:
				if self.count<self.timeout:
					self.count+=1
				else:
					msg_log="Lliurex Guard checking connection with server. Time Out. Error:%s"%str(e)
					self.write_log(msg_log)
					self.connection=True

			
		self.set_server(self.server_ip)	
		self._debug(msg,restart_dnsmasq)
		msg_log=msg+str(restart_dnsmasq)
		self.write_log(msg_log)
		
		return restart_dnsmasq				

	#def restart_dnsmasq()	

	def send_tmpfile_toserver(self,tmp_file):

		send_tmpfile=self.n4d_local.send_file("","ScpManager",self.validation[0],self.validation[1],"server",tmp_file,"/tmp")
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

		self.n4d.remove_tmp_file(self.validation,"LliurexGuardManager")			

		
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

		'''
		Result code:
			-33: Lines to copy >limit
		'''	

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
				code=33
			
				for item in text:
					if count<2500:
						text_to_copy.append(item+"\n")
						count+=1
					else:
						break

		return {'status':True,'code':code,'data':text_to_copy} 	

	#def get_clipboard_content				

	def update_list_dns(self,list_data):

		'''
			Result code:
				-34: Unable to read file
				-35: Read file successfully

		'''
		
		status=True
		error_info=[]
		code=""
		for item in list_data:
			read_guardmode_list=self.n4d.read_guardmode_list(self.validation,"LliurexGuardManager",list_data[item]["id"],list_data[item]['active'])
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
				code=34
				error_info=read_guardmode_list['data']
				break

		if status:
			code=35
			result=list_data
		else:
			result=error_info

		return {'status':status,'code':code,'data':result}
		
				

	#def update_list_dns	

#class GuardManager
