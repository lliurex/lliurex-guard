 
import os
import json
import codecs
import shutil
import xmlrpclib as n4dclient
import ssl
import subprocess
from os import listdir
from os.path import isfile,isdir,join


class LliurexGuardManager(object):

	def __init__(self):

		self.default_list_path="/usr/share/lliurex-guard/blacklists"
		self.mode_file_path="/etc/dnsmasq.d/lliurex-guard.conf"
		self.conf_dir="/etc/lliurex-guard"
		self.blacklist_dir=os.path.join(self.conf_dir,"blacklist")
		self.blacklist_disable_dir=os.path.join(self.conf_dir,"blacklist.d")
		self.set_bm_mode="addn-hosts = /etc/lliurex-guard/blacklist"
		self.disable_bm_mode="#addn-hosts = /etc/lliurex-guard/blacklist"
		self.blacklist_redirection="169.254.254.254"
		self.whitelist_dir=os.path.join(self.conf_dir,"whitelist")
		self.whitelist_disable_dir=os.path.join(self.conf_dir,"whitelist.d")
		self.set_wm_mode="conf-dir = /etc/lliurex-guard/whitelist"
		self.disable_wm_mode="#conf-dir = /etc/lliurex-guard/whitelist"
		self.whitelist_redirection="server=/"
		self.whitelist_filter="address=/#/"+self.blacklist_redirection
		self.disable_whitelist_filter="#"+self.whitelist_filter
		self.list_tmpfile=[]
		server='localhost'
		context=ssl._create_unverified_context()
		self.n4d = n4dclient.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		
	#def __init__	


	def _create_guardmode_conf_file(self):

		f=open(self.mode_file_path,'w')
		f.write(self.disable_bm_mode+"\n")
		f.write(self.disable_wm_mode+"\n")
		f.write(self.disable_whitelist_filter)
		f.close()

	#def _create_guardmode_conf

	def _create_guardmode_conf_dir(self,mode_to_set):

		
		if not os.path.exists(self.conf_dir):
			os.mkdir(self.conf_dir)

		if mode_to_set =="BlackMode":
			if not os.path.exists(self.blacklist_dir):
				os.mkdir(self.blacklist_dir)

			if not os.path.exists(self.blacklist_disable_dir):
				os.mkdir(self.blacklist_disable_dir)
				if os.path.exists(self.default_list_path):
					os.system("cp -R "+self.default_list_path+"/* "+self.blacklist_disable_dir)

		elif mode_to_set=="WhiteMode":			
			if not os.path.exists(self.whitelist_dir):
				os.mkdir(self.whitelist_dir)

			if not os.path.exists(self.whitelist_disable_dir):
				os.mkdir(self.whitelist_disable_dir)		
			
	#def _create_guardmode_conf	

	def _detect_flavour(self):
		
		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		
		self.flavours = [ x.strip() for x in result.split(',') ]

	#def _detect_flavour	

	def _get_dns(self):

		self._detect_flavour()
		dns_vars=[]

		if 'server' in self.flavours:
			dns_vars=self.n4d.get_variable("","VariablesManager","DNS_EXTERNAL")
		else:
			pass	
		
		return dns_vars

	#def _get_dns	

	def read_guardmode(self):
		
		try:
			if not os.path.exists(self.mode_file_path):
				self._create_guardmode_conf_file()

			f=open(self.mode_file_path,'r')
			lines=f.readlines()
			count=0
			for line in lines:
				if "#" in line:
					count+=1
				else:
					if "addn-hosts" in line:
						guardMode="BlackMode"
					else:
						guardMode="WhiteMode"
			
			
			if count==3:
				self.guardMode="DisableMode"
			else:
				self.guardMode=guardMode

			f.close()
			self._set_variables()

			return {'status':True,'msg':"Guard Mode read successfully",'data':self.guardMode}
		
		except Exception as e:
			return {'status':False,'msg':"Unable to read Guard Mode",'data':str(e)}

	#def read_guard_mode
	
	def _set_variables(self):

		if self.guardMode=="BlackMode":
			self.active_path=self.blacklist_dir
			self.disable_path=self.blacklist_disable_dir
			self.redirection=self.blacklist_redirection
		elif self.guardMode=="WhiteMode":
			self.active_path=self.whitelist_dir
			self.disable_path=self.whitelist_disable_dir
			self.redirection=self.whitelist_redirection
			self.dns_vars=self._get_dns()

	#def _set_variables		
	
	def change_guardmode(self,mode_to_set,rescue=False):

		try:
			f=open(self.mode_file_path,'w')

			if mode_to_set=="BlackMode":
				f.write(self.set_bm_mode+"\n")
				f.write(self.disable_wm_mode+"\n")
				f.write(self.disable_whitelist_filter)
			elif mode_to_set=="WhiteMode":
				f.write(self.disable_bm_mode+"\n")
				f.write(self.set_wm_mode+"\n")
				f.write(self.whitelist_filter)
			elif mode_to_set=="DisableMode":
				f.write(self.disable_bm_mode+"\n")
				f.write(self.disable_wm_mode+"\n")
				f.write(self.disable_whitelist_filter)	
				
			
			f.close()
			self._create_guardmode_conf_dir(mode_to_set)
			if rescue:
				restart=self.restart_dnsmasq(True)
			return {'status':True,'msg':"Changed LliureX Guard Mode sucessfully",'data':""}
			
		except Exception as e:
			return {'status':False,'msg':"Unable to change Guard Mode",'data':str(e)}	

	#def change_guard_mode
	
	def restart_dnsmasq(self,nonretry=False):			

		cmd="systemctl restart dnsmasq.service 1>/dev/null"
		error=False
		data=""
		try:
			restart=os.system(cmd)
			if restart !=0:
				error=True
				data=str(restart)
				
		except Exception as e:
			error=True
			data=str(e)

		if not error:			
			return {'status':True,'msg':"Dnsmaq restart successfully"}
		else:
			if not nonretry:
				self.change_guardmode("DisableMode",True)
			return {'status':False,'msg':"Error restarting Dnsmaq",'data':data}

	#def __restart_dnsmasq				
	

	def read_guardmode_headers(self):
		
		list_config={}
		result=True
		data=[]
		count=1
		error=False

		active_list=self._read_list_headers(self.active_path)

		if active_list['status']:
			disable_list=self._read_list_headers(self.disable_path)
			if not disable_list['status']:
				error=True
				result=disable_list
		else:
			error=True
			result=active_list		
	
		if not error:		
			data=active_list['data']+disable_list['data']
			
			for item in data:
				list_config[str(count)]=item
				count+=1

			return {'status':True,'msg':'Reading %s sucessfully'%self.guardMode,'data':list_config}	
		else:
			return result	


	#def read_guardmode_list
	
	def _read_list_headers(self,folder):

		files_headers=[]

		try:
			for item in listdir(folder):
				t=join(folder,item)
				if isfile(t):
					f=codecs.open(t,'r',encoding="utf-8")
					tmp={}
					tmp["id"]=item.split(".")[0]
					tmp["active"]=True
					match=0
					lines=f.readlines()
					for line in lines:
						line=line.encode("utf-8")
						if "NAME" in line:
							tmp["name"]=line.split(":")[1].split("\n")[0]
							match+=1
						if "DESCRIPTION" in line:
							tmp["description"]=line.split(":")[1].split("\n")[0]
							match+=1

						if match==2:
							if self.guardMode=="BlackMode":
								tmp["lines"]=len(lines)-2

							else:
								num_lines=(len(lines)-2)/2
								tmp["lines"]=num_lines
							break	


					f.close()
					lines=None
					if folder==self.blacklist_disable_dir:
						tmp["active"]=False
					elif folder==self.whitelist_disable_dir:
						tmp["active"]=False

					files_headers.append(tmp)
			
			return {'status':True,'msg':"Lists readed successfully",'data':files_headers}

		except Exception as e:			
			return {'status':False,'msg':"Unable to readed lists",'data':str(e)}

	#def _read_list_headers
				
	def read_guardmode_list(self,listId,active):

		if active:
			path=self.active_path
				
		else:
			path=self.disable_path	
				
		try:
			file=os.path.join(path,listId+".list")
			content=[]
			count_lines=0
			if os.path.exists(file):
				#f=codecs.open(file,'r',encoding="utf-8")
				f=open(file,'r')
				lines=f.readlines()
				for line in lines:
					if "NAME" not in line:
						if "DESCRIPTION" not in line:
							if self.guardMode=="BlackMode":
								if self.redirection in line:
									line=line.split(self.redirection)[1].split(" ")[1]
									content.append(line)	
									count_lines+=1
							else:
								if self.redirection in line:
									line=line.split(self.redirection)[1]
									line=line.split("/")[0]
									tmp_line=line+"\n"
									if tmp_line not in content:
										content.append(line+"\n")	
										count_lines+=1
										
							
				f.close()
				lines=None
				
				return {'status':True,'msg':"Read content list successfully",'data':[content,count_lines]}	
		except Exception as e:
			return {'status':False,'msg':"Unable to read content list",'data':str(e)}
					

	#def read_guardmode_list	


	def remove_guardmode_list(self,lists):

		try:
			for item in lists:
					file=item+".list"
					if os.path.exists(os.path.join(self.active_path,file)):
						os.remove(os.path.join(self.active_path,file))
					else:
						if os.path.exists(os.path.join(self.disable_path,file)):
							os.remove(os.path.join(self.disable_path,file))	
							
			return {'status':True,'msg':"Listed removed sucessfully"}		

		except Exception as e:

			return {'status':False,'msg':"Error removing lists",'data':str(e)}		
							

	#def remove_guardmode_list
	
	def activate_guardmode_list(self,lists):

		result=self._move_guardmode_list(lists,self.active_path,self.disable_path)

		if result['status']:
			return {'status':True,'msg':"Lists activated successfully"}
		else:
			return result			
		
	#def activate_guardmode_list
	
	def deactivate_guardmode_list(self,lists):

		result=self._move_guardmode_list(lists,self.disable_path,self.active_path)
		
		if result['status']:
			return {'status':True,'msg':"Lists deactivated successfully"}
		else:
			return result

	#def deactivate_guardmode_list	

	def _move_guardmode_list(self,lists,dest_path,orig_path):

		
		try:
			for item in lists:
				if item["tmpfile"]!="":
					result_format=self._format_guardmode_list(item)
					if result_format['status']:
						dest_file=os.path.join(dest_path,item["id"]+".list")
						shutil.copy2(item["tmpfile"],dest_file)
						os.system("chmod 644 "+dest_file)
						self.list_tmpfile.append(item["tmpfile"])
						if os.path.exists(os.path.join(orig_path,item["id"]+".list")):
							os.remove(os.path.join(orig_path,item["id"]+".list"))
					else:
						return result_format	
					
				else:
					if os.path.exists(os.path.join(orig_path,item["id"]+".list")):
						shutil.copy2(os.path.join(orig_path,item["id"]+".list"),os.path.join(dest_path,item["id"]+".list"))			
						os.remove(os.path.join(orig_path,item["id"]+".list"))
			
			return {'status':True,'msg':""}
			
		except Exception as e: 				
			return {'status':False,'msg':"Error copyng list ",'data':str(e)}

	#def _move_guardmode_list	

	def _format_guardmode_list(self,item):

		
		try:
			if os.path.exists(item["tmpfile"]):
				f=codecs.open(item["tmpfile"],'r',encoding="utf-8")
				lines=f.readlines()
				f.close()
				f=open(item["tmpfile"],'w')

				header_name="#NAME:"+unicode(item["name"]).encode("utf-8")+"\n"
				f.write(header_name)
				header_desc="#DESCRIPTION:"+unicode(item["description"]).encode("utf-8")+"\n"
				f.write(header_desc)
				for line in lines:
					if line !="":
						if self.guardMode=="BlackMode":
							tmp_line=self.redirection+" "+line
							f.write(tmp_line)
						else:
							for dns in self.dns_vars:
								if "https" in line:
									line=line.replace("https://","")
								else:
									line=line.replace("http://","")	
								tmp_line=self.whitelist_redirection+line.split("\n")[0]+"/"+dns
								f.write(tmp_line+"\n")	
				
				f.close()
				lines=None
				
			return {'status':True,'msg':'List formated successfully'}
		
		except Exception as e:
			return {'status':False,'msg':'Error formatting the list','data':str(e)}						
		

	#def _format_guarmode_list		
			
	def remove_tmp_file(self):

		print(self.list_tmpfile)
		
		for item in self.list_tmpfile:
			if os.path.exists(item):
				os.remove(item)

		self.list_tmpfile=[]
	#def _remove_tmp_file			