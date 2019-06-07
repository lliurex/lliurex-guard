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
import sys
import syslog
from os import listdir
from os.path import isfile,isdir,join
from jsondiff import diff


class GuardManager(object):

	def __init__(self,server=None):

		super(GuardManager, self).__init__()

		self.dbg=1
		self.user_validated=False
		self.user_groups=[]
		self.validation=None
		self.limit_lines=2500

		if server!=None:
			self.set_server(server)

		context=ssl._create_unverified_context()
		self.n4d_local = n4dclient.ServerProxy("https://localhost:9779",context=context,allow_none=True)	
		self.detect_flavour()	
	
	#def __init__	
	

	def set_server(self,server):	
		
		context=ssl._create_unverified_context()	
		self.n4d=n4dclient.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
	
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
			session_user=os.environ["USERNAME"]
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
			
		read_guardmode=self.n4d.read_guardmode(self.validation,"LliurexGuardManager")
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
		msg="LliureX Guard Mode changed "
		self._debug(msg,change_guardmode)
		msg_log=msg+str(change_guardmode)
		self.write_log(msg_log)
		
		if change_guardmode['status']:
			restart_dnsmasq=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")
			msg="LliureX Guard Mode changed.Dnsmasq restarted "
			self._debug(msg,restart_dnsmasq)
			msg_log=msg+str(restart_dnsmasq)
			self.write_log(msg_log)
			if restart_dnsmasq['status']:
				return {'status':True,'code':8}
			else:
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
			return {'status':False,'code':25,'data':read_guardmode_headers['data']}
		

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
			msg="Readed local file "
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
			msg="Readed list file "
			self._debug(msg,read_guardmode_list)
			if read_guardmode_list['status']:
				content=read_guardmode_list['data'][0]
				count_lines=read_guardmode_list['data'][1]
			else:
				status=False
				error_info=read_guardmode_list['data']

		if status:
			code=12		
			if count_lines>self.limit_lines:
				if not tmpfile:
					tmp_file=self._create_tmp_file(listId)
					'''
					tmp_file=tempfile.mkstemp("_"+listId)[1]
					basename=os.path.basename(tmp_file)
					shutil.move(tmp_file,os.path.join(self.tmp_folder,basename))
					tmp_file=os.path.join(self.tmp_folde,basename)
					'''
					f=open(tmp_file,'w')
					tmp_content="".join(content)
					f.write(tmp_content)
					f.close()
					tmp_content=None
				else:
					tmp_file=read_tmp_file['data'][2]	

			data=[content,tmp_file]
		else:
			code=13
			data=error_info
		msg_log=msg+"error: "+status+" Error details: "+str(error_info)
		self.write_log(msg_log)
		return {'status':status,'code':code,'data':data}

	#def read_guardmode_list	
			
	def read_local_file(self,file,create_tmpfile):

		'''
		Result code:
			-15: File loaded successfully
			-116: Error loading file info
		'''

		content=[]
		count_lines=0
		tmp_file=""
		try:
			if os.path.exists(file):
				f=open(file,'r')
				lines=f.readlines()
				for line in lines:
					if "NAME" not in line:
						if "DESCRIPTION" not in line:
							if line !="":
								if line.startswith(".") or line.startswith("_") or line.startswith("-"):
									line=line[1:]
								content.append(line)	
								count_lines+=1
				f.close()
				lines=None
				tmp_file=file
				
				if create_tmpfile:
					tmp_file=self._create_tmp_file(os.path.basename(file))
					'''
					tmp_file=tempfile.mkstemp("_"+os.path.basename(file))[1]
					basename=os.path.basename(tmp_file)
					shutil.move(tmp_file,os.path.join(self.tmp_folder,basename))
					tmp_file=os.path.join(self.tmp_folde,basename)
					'''
					f=open(tmp_file,'w')
					f.write("".join(content))
					f.close()

			return {'status':True,'code':15,'data':[content,count_lines,tmp_file]}

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
				
			else:
				tmp_list=args[2]

			if content=="":
				tmp_content=[]
				f=open(tmp_list,'r')
				lines=f.readlines()
				f.close()
				for line in lines:
					tmp_content.append(line)
					result["lines"]=len(tmp_content)
					#content="".join(tmp_content)
			else:		
				f=open(tmp_list,"w")
				f.write(content)
				f.close()
			content=None
			tmp_content=None
			result["status"]=True
			result["tmpfile"]=tmp_list
			
		except Exception as e:
			result['status']=False
			result['code']=5
			result['data']=str(e)
		
		msg="Saved list changes"
		self._debug(msg,result)
		msg_log=msg+str(result)	
		self.write_log(msg_log)

		return result
			

			
	#def save_conf		

	def check_data(self,list_data,data,edit,orig_id=None):

		'''
		Result code:
			-1: Missing list name
			-2: List name duplicate
	
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

		return {"result":True,"code":0}			
			 			
	#def check_data
	
	def get_listId(self,name):

		listId= ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
		listId=listId.lower().replace(" ","_")
		listId=re.sub('[^\w\s-]', '', listId).strip()
		listId=re.sub('[-\s]+', '-', listId)

		return listId

	#def get_siteId

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
		tmpfile_list=[]
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
							tmpfile_list.append(list_data[item]["tmpfile"])
							if "client" in self.flavours:
								send=self._send_tmpfile_toserver(list_data[item]["tmpfile"])
									
						list_to_active.append(list_data[item])
									
									
					if not list_data[item]["active"]:
						if list_data[item]["tmpfile"]!="":
							tmpfile_list.append(list_data[item]["tmpfile"])
							if "client" in self.flavours:
								send=self._send_tmpfile_toserver(list_data[item]["tmpfile"])
								
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
				self._remove_tmp_file(tmpfile_list)
				result_restart=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")
				if result_restart['status']:
					return {'status':True,'code':18}
				else:
					disable_llxguard=self.n4d.change_guardmode(self.validation,"LliurexGuardManager","DisableMode")
					if disable_llxguard['status']:
						restart=self.n4d.restart_dnsmasq(self.validation,"LliurexGuardManager")

					return {'status':False,'code':10,'data':result_restart['data']}
			else:
				return {'status':False,'code':code,'data':data}									

		else:
			return {'status':True,'code':0}						

	#def apply_changes

	def _send_tmpfile_toserver(self,tmp_file):

		send_tmpfile=self.n4d_local.send_file("","ScpManager",self.validation[0],self.validation[1],"server",tmp_file,"/tmp")
			
		return send_tmpfile
	#def _send_tmpfile_toserver		

	def _create_tmp_file(self,listId):
	
		tmp_file=tempfile.mkstemp("_"+listId)
		tmp_file=tmp_file[1]
		
		return tmp_file

	#def _create_tmp_file	

	def _remove_tmp_file(self,tmpfile_list):

		if "client" in self.flavours:
			for item in tmpfile_list:
				if os.path.exists(item):
					os.remove(item)

		self.n4d.remove_tmp_file(self.validation,"LliurexGuardManager")			

		
	#def _remove_tmp_file	

	def write_log(self,msg):
	
		syslog.openlog("LLIUREX-GUARD")
		syslog.syslog(msg)	

	#def write_log	
#class GuardManager
