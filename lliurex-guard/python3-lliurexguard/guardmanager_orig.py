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
import shutil
import glob
import unicodedata
import re
import subprocess
import urllib.request as urllib2
import tempfile
import time
from os import listdir
from os.path import isfile,isdir,join



class GuardManager(object):

	def __init__(self,server=None):

		super(GuardManager, self).__init__()

		self.dbg=0
		self.user_validated=False
		self.user_groups=[]
		self.validation=None
		self.list_folder_active="/home/lliurex/Escritorio/blacklist/active"
		self.list_folder_disable="/home/lliurex/Escritorio/blacklist/disable"
		

		if server!=None:
			self.set_server(server)

		#context=ssl._create_unverified_context()
		#self.n4d_local = n4dclient.ServerProxy("https://localhost:9779",context=context,allow_none=True)	
		#self.detect_flavour()	
	
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
					
		#return self.user_validated
		
	#def validate_user

	def _debug(self,function,msg):

		if self.dbg==1:
			print("[LLIUREX_GUARD]: "+ str(function) + str(msg))

	#def _debug		

	def read_conf(self):
		
		#result=self.n4d.read_conf(self.validation,'EasySitesManager')
		self.list_config={}
		result=True
		data=[]
		for item in listdir(self.list_folder_active):
			print (item)
			t=join(self.list_folder_active,item)
			print(t)
			if isfile(t):
				f=open(t,'r')
				tmp={}
				tmp["id"]=item.split(".")[0]
				match=0
				lines=f.readlines()
				for line in lines:
					if match==2:
						tmp["lines"]=len(lines)-2
						break
					if "NAME" in line:
						tmp["name"]=line.split(":")[1].split("\n")[0]
						match+=1
					if "DESCRIPTION" in line:
						tmp["description"]=line.split(":")[1].split("\n")[0]
						match+=1
				f.close()
				f=None		
				tmp["active"]=True
				tmp["edited"]=False
				tmp["remove"]=False
				data.append(tmp)

		for item in listdir(self.list_folder_disable):
			print (item)
			t=join(self.list_folder_disable,item)
			print(t)
			if isfile(t):
				f=open(t,'r')
				tmp={}
				tmp["id"]=item.split(".")[0]
				match=0
				lines=f.readlines()
				for line in lines:
					if match==2:
						tmp["lines"]=len(lines)-2
						break
					if "NAME" in line:
						tmp["name"]=line.split(":")[1].split("\n")[0]
						match+=1
					if "DESCRIPTION" in line:
						tmp["description"]=line.split(":")[1].split("\n")[0]
						match+=1
				f.close()
				f=None		
				tmp["active"]=False
				tmp["edited"]=False
				tmp["remove"]=False
				data.append(tmp)		

		#self._debug("Read configuration file: ",result)
		count=1
		for item in data:
			self.list_config[count]=item
			count+=1
		
		return True
		
	#def read_conf	

	def read_local_file(self,file):

		load_data=[]

		if os.path.exists(file):
			f=open(file,'r')
			content=f.readlines()
			f.close()
			tmp_file=tempfile.mkstemp("_"+os.path.basename(file))[1]
			f=open(tmp_file,'w')
			for line in content:
				if "NAME" not in line: 
					if "DESCRIPTION" not in line:
						f.write(line)
			f.close()
			load_data=[tmp_file,content]

		return load_data

	#def read_local_file	


	def read_url_list(self,order,data):
		
		tmpfile=False
		listId=data[order]["id"]
		if "tmpfile" in data[order]:
			file=data[order]["tmpfile"]
			tmpfile=True
		else:	
			if data[order]["active"]:
				file=os.path.join(self.list_folder_active,listId+".list")
			else:
				file=os.path.join(self.list_folder_disable,listId+".list")	
		lines=[]
		tmp_file=""
		if os.path.exists(file):
			f=open(file,'r')
			content=f.readlines()
			f.close()
			if len(content)<5000:
				for line in content:
					if "NAME" not in line: 
						if "DESCRIPTION" not in line:
							lines.append(line)
			else:
				if not tmpfile:
					tmp_file=tempfile.mkstemp("_"+os.path.basename(file))[1]
					f=open(tmp_file,'w+')
					for line in content:
						if "NAME" not in line: 
							if "DESCRIPTION" not in line:
								f.write(line)
					f.close()	
				else:
					tmp_file=file				
		
		result={}
		content=None
		result['status']=True
		result['data']=lines
		result['tmpfile']=tmp_file
		return result	
		

	def save_conf(self,args):

		error=False
		result={}

		info=args[0]
		content=args[1]
		if args[2]==None:
			tmp_list=tempfile.mkstemp("_"+info["id"])
			tmp_list=tmp_list[1]
			
		else:
			tmp_name=os.path.basename(args[2]).split("_")[0]+info["id"]+".list"
			rename_file=os.path.join(os.path.split(args[2])[0],tmp_name)
			os.rename(args[2],rename_file)
			tmp_list=rename_file
			if content=="":
				tmp_content=[]
				f=open(tmp_list,'r')
				lines=f.readlines()
				f.close()
				for line in lines:
					if "NAME" not in line: 
						if "DESCRIPTION" not in line:
							tmp_content.append(line)
							result["lines"]=len(tmp_content)
				content="".join(tmp_content)

		f=open(tmp_list,"w")
		header_name="#NAME:"+info["name"]+"\n"
		f.write(header_name)
		header_desc="#DESCRIPTION:"+info["description"]+"\n"
		f.write(header_desc)
		f.write(content)
		f.close()
		content=None
		tmp_content=None
		result["status"]=True
		result["tmpfile"]=tmp_list
		print("#####RESULTADO")
		print(result)
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

	def apply_changes(self,list_data):

		print("aplicando cambios")

		for item in list_data:
			list_name=list_data[item]["id"]+".list"
			print("#####")
			print(list_name)
			if list_data[item]["edited"]:
				if list_data[item]["remove"]:
					list_path_active=os.path.join(self.list_folder_active,list_name)
					if os.path.exists(list_path_active):
						os.remove(list_path_active)
						continue
					else:
						list_path_disable=os.path.join(self.list_folder_disable,list_name)
						if os.path.exists(list_path_disable):
							os.remove(list_path_disable)
							continue
				if list_data[item]["active"]:

					if "tmpfile" in list_data[item]:
						dest_path=os.path.join(self.list_folder_active,list_name)
						print("######DEST PATH")
						print(dest_path)
						print(list_data[item]["tmpfile"])
						shutil.copy(list_data[item]["tmpfile"],dest_path)

						if os.path.exists(os.path.join(self.list_folder_disable,list_name)):
							os.remove(os.path.join(self.list_folder_disable,list_name))

					else:
						if os.path.exists(os.path.join(self.list_folder_disable,list_name)):
							shutil.copy(os.path.join(self.list_folder_disable,list_name),os.path.join(self.list_folder_active,list_name))
							os.remove(os.path.join(self.list_folder_disable,list_name))

				if not list_data[item]["active"]:
					if "tmpfile" in list_data[item]:
						dest_path=os.path.join(self.list_folder_disable,list_name)
						shutil.copy(list_data[item]["tmpfile"],dest_path)

						if os.path.exists(os.path.join(self.list_folder_active,list_name)):
							os.remove(os.path.join(self.list_folder_active,list_name))

					else:
						if os.path.exists(os.path.join(self.list_folder_active,list_name)):
							print("pasando a disable")
							shutil.copy(os.path.join(self.list_folder_active,list_name),os.path.join(self.list_folder_disable,list_name))
							os.remove(os.path.join(self.list_folder_active,list_name))
					
				if list_data[item]["replaced_to"]!="":
					print("eliminar reemplazado")
					orig_name=list_data[item]["replaced_to"]+".list"
					if os.path.exists(os.path.join(self.list_folder_active,orig_name)):
						os.remove(os.path.join(self.list_folder_active,orig_name))
					else:
						if os.path.exists(os.path.join(self.list_folder_disable,orig_name)):
							os.remove(os.path.join(self.list_folder_disable,orig_name))

		return True
								

	#def apply_changes


#class GuardManager
