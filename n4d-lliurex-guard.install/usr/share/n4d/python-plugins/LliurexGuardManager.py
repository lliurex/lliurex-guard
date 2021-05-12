 
import os
import json
import codecs
import shutil
import ssl
import subprocess
from os import listdir
from os.path import isfile,isdir,join
import n4d.server.core as n4dcore
import n4d.responses


class LliurexGuardManager:

	def __init__(self):

		self.core=n4dcore.Core.get_core()
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
		'''
		server='localhost'
		context=ssl._create_unverified_context()
		self.n4d = n4dclient.ServerProxy("https://"+server+":9779",context=context,allow_none=True)
		'''
	#def __init__	

	def _check_dnsmasq_conf(self):
		
		with open("/etc/dnsmasq.conf","r") as fd:
			lines = fd.readlines()

		if "conf-dir=/etc/dnsmasq.d/" not in lines:
			with open("/etc/dnsmasq.conf","a") as fd:
				fd.write("conf-dir=/etc/dnsmasq.d/\n")
		if "conf-dir=/var/lib/dnsmasq/config" not in lines:
			with open("/etc/dnsmasq.conf","a") as fd:
				fd.write("conf-dir=/var/lib/dnsmasq/config\n")


		if not os.path.exists("/var/lib/dnsmasq/config/extra-dns"):
			with open("/var/lib/dnsmasq/config/extra-dns","w") as fd:
				desktop_dns=self._get_desktop_dns()
				for item in desktop_dns:
					line="server=%s"%item+"\n"
					fd.write(line)
				fd.close()		

		fd.close()		

	#def check_dnsmasq_conf			

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
		
		self.is_server=False

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()
		
		flavours = [ x.strip() for x in result.split(',') ]

		for item in flavours:
			if 'server' in item:
				self.is_server=True
				break
	
	#def _detect_flavour	

	def _get_dns(self):

		#self._detect_flavour()
		dns_vars=[]
		is_server=False

		if self.is_server:
			#Old n4d: dns_vars=self.n4d.get_variable("","VariablesManager","DNS_EXTERNAL")
			dns_vars=self.core.get_variable("DNS_EXTERNAL").get('return',None)

		else:
			dns_vars=self._get_desktop_dns()
		
		return dns_vars

	#def _get_dns	

	def _first_init(self):

		if not os.path.exists("/var/lib/lliurex-guard"):
			os.makedirs("/var/lib/lliurex-guard")

		if not self.is_server:
			if not os.path.exists("/var/lib/dnsmasq"):
				os.makedirs("/var/lib/dnsmasq")

			if not os.path.exists("/var/lib/dnsmasq/config"):
				os.makedirs("/var/lib/dnsmasq/config")

			self._check_dnsmasq_conf()

			if not os.path.exists("etc/systemd/resolved.conf.d/lliurex-dnsmasq.conf"):
				os.system('systemctl stop systemd-resolved')
				self.core.get_plugin('NetworkManager').systemd_resolv_conf()
				# Restart service to fix bug on /etc/resolv.conf search field
				os.system('systemctl restart systemd-resolved')

		fd = open("/var/lib/lliurex-guard/first_init","w")
		fd.close()

	#def first_init


	def _get_desktop_dns(self):

		desktop_dns=[]
		cmd="nmcli device show | grep DNS | awk '{print$2}'"
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		output=p.communicate()[0]

		if type(output) is bytes:
			output=output.decode()

		output=output.split("\n")

		for item in output:	
			if item!='':
				desktop_dns.append(item)

		return desktop_dns		

	#def _get_desktop_dns	


	def read_guardmode(self,checkconfig=False):
		
		try:
			
			if checkconfig:
				self._detect_flavour()
				if not os.path.exists("/var/lib/lliurex-guard/first_init"):
					self._first_init()

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
			if checkconfig:
				self._set_variables()

			#Old n4d:return {'status':True,'msg':"Guard Mode read successfully",'data':self.guardMode}
			result={'status':True,'msg':"Guard Mode read successfully",'data':self.guardMode}
			return n4d.responses.build_successful_call_response(result)
		
		except Exception as e:
			#Old n4d: return {'status':False,'msg':"Unable to read Guard Mode",'data':str(e)}
			result={'status':False,'msg':"Unable to read Guard Mode",'data':str(e)}
			return n4d.responses.build_successful_call_response(result)
	

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
			#Old n4d:return {'status':True,'msg':"Changed LliureX Guard Mode sucessfully",'data':""}
			result={'status':True,'msg':"Changed LliureX Guard Mode sucessfully",'data':""}
			return n4d.responses.build_successful_call_response(result)
	
		except Exception as e:
			#Old n4d:return {'status':False,'msg':"Unable to change Guard Mode",'data':str(e)}	
			result={'status':False,'msg':"Unable to change Guard Mode",'data':str(e)}	
			return n4d.responses.build_successful_call_response(result)	

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
			#Old n4d:return {'status':True,'msg':"Dnsmaq restart successfully"}
			result={'status':True,'msg':"Dnsmaq restart successfully"}
			return n4d.responses.build_successful_call_response(result)
		else:
			if not nonretry:
				self.change_guardmode("DisableMode",True)
			#Old n4d_return {'status':False,'msg':"Error restarting Dnsmaq",'data':data}
			result={'status':False,'msg':"Error restarting Dnsmaq",'data':data}
			return n4d.responses.build_successful_call_response(result)

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

			#Old n4d: return {'status':True,'msg':'Reading %s sucessfully'%self.guardMode,'data':list_config}	
			result={'status':True,'msg':'Reading %s sucessfully'%self.guardMode,'data':list_config}	
		'''
		else:
			return result
		'''		
		return n4d.responses.build_successful_call_response(result)	
	

	#def read_guardmode_list
	
	def _read_list_headers(self,folder):

		files_headers=[]

		try:
			for item in listdir(folder):
				t=join(folder,item)
				if isfile(t):
					f=codecs.open(t,'r')
					tmp={}
					tmp["id"]=item.split(".")[0]
					tmp["active"]=True
					match=0
					lines=f.readlines()
					for line in lines:
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
			alternative_path=self.disable_path
				
		else:
			path=self.disable_path	
			alternative_path=self.active_path
				
		try:
			existsfile=False
			file=os.path.join(path,listId+".list")
			content=[]
			count_lines=0
			if os.path.exists(file):
				#f=codecs.open(file,'r',encoding="utf-8")
				f=open(file,'r')
				existsfile=True
			else:	
				file=os.path.join(alternative_path,listId+".list")
				if os.path.exists(file):
					f=open(file,'r')
					existsfile=True

			if existsfile:		
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
				
				#Old n4d:return {'status':True,'msg':"Read content list successfully",'data':[content,count_lines]}	
				result={'status':True,'msg':"Read content list successfully",'data':[content,count_lines]}	

			else:
				#Old n4d: return {'status':False,'msg':"Unable to read content list.The file does not exist",'data':"The file does not exist"}
				result={'status':False,'msg':"Unable to read content list.The file does not exist",'data':"The file does not exist"}

			return n4d.responses.build_successful_call_response(result)	
		
		except Exception as e:
			#Old n4d: return {'status':False,'msg':"Unable to read content list",'data':str(e)}
			result={'status':False,'msg':"Unable to read content list",'data':str(e)}
			return n4d.responses.build_successful_call_response(result)
					

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
							
			#Old n4d:return {'status':True,'msg':"Listed removed sucessfully"}		
			result={'status':True,'msg':"Listed removed sucessfully"}		
			return n4d.responses.build_successful_call_response(result)		

		except Exception as e:
			#Old n4d: return {'status':False,'msg':"Error removing lists",'data':str(e)}		
			result={'status':False,'msg':"Error removing lists",'data':str(e)}		
			return n4d.responses.build_successful_call_response(result)		
							

	#def remove_guardmode_list
	
	def activate_guardmode_list(self,lists):

		result=self._move_guardmode_list(lists,self.active_path,self.disable_path)

		if result['status']:
			#Old n4d: return {'status':True,'msg':"Lists activated successfully"}
			result={'status':True,'msg':"Lists activated successfully"}
			return n4d.responses.build_successful_call_response(result)
			
		else:
			return n4d.responses.build_successful_call_response(result)
	
	#def activate_guardmode_list
	
	def deactivate_guardmode_list(self,lists):

		result=self._move_guardmode_list(lists,self.disable_path,self.active_path)
		
		if result['status']:
			#Old n4d: return {'status':True,'msg':"Lists deactivated successfully"}
			result:{'status':True,'msg':"Lists deactivated successfully"}
			return n4d.responses.build_successful_call_response(result)
		
		else:
			return n4d.responses.build_successful_call_response(result)

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
				f=codecs.open(item["tmpfile"],'r')
				lines=f.readlines()
				f.close()
				original_file_perms=self._get_original_file_perms(item["tmpfile"])
				os.system('chown root:root '+item['tmpfile'])
				f=open(item["tmpfile"],'w')

				header_name="#NAME:"+item["name"]+"\n"
				f.write(header_name)
				header_desc="#DESCRIPTION:"+item["description"]+"\n"
				f.write(header_desc)
				for line in lines:
					if line !="":
						if self.redirection in line:
								f.write(line)
						else:		
							if self.guardMode=="BlackMode":
								tmp_line=self.redirection+" "+line
								f.write(tmp_line)
							else:
								if "https" in line:
									line=line.replace("https://","")
								else:
									line=line.replace("http://","")	
								
								for dns in self.dns_vars:
									tmp_line=self.redirection+line.split("\n")[0]+"/"+dns
									f.write(tmp_line+"\n")	
				
				f.close()
				try:
					cmd='chown %s:%s %s'%(original_file_perms[0],original_file_perms[1],item["tmpfile"])
					os.system(cmd)
				except Exception as e:
					print(str(e))
					pass
				lines=None
				
			return {'status':True,'msg':'List formated successfully'}
		
		except Exception as e:
			return {'status':False,'msg':'Error formatting the list','data':str(e)}						
		

	#def _format_guarmode_list		
			
	def remove_tmp_file(self):

		
		for item in self.list_tmpfile:
			if os.path.exists(item):
				os.remove(item)

		self.list_tmpfile=[]
		return n4d.responses.build_successful_call_response()

	#def _remove_tmp_file			

	def update_whitelist_dns(self):

		self._detect_flavour()
		dns_vars = self._get_dns()
		folders_to_update=[self.whitelist_dir,self.whitelist_disable_dir]

		try:
			for folder in folders_to_update:
				for item in listdir(folder):
					t=join(folder,item)
					if isfile(t):
						content=[]
						format_lines=[]
						f=codecs.open(t,'r')
						lines=f.readlines()
						f.close()
						for line in lines:
							if line!="":
								if "NAME" in line:
									format_lines.append(line)
									
								elif "DESCRIPTION" in line:
									format_lines.append(line)
								else:
									if self.whitelist_redirection in line:
										line=line.split(self.whitelist_redirection)[1]
										line=line.split("/")[0]
										tmp_line=line+"\n"
										if tmp_line not in content:
											content.append(line+"\n")
											format_lines.append(line+"\n")

						f=open(t,'w')
						for line in format_lines:
							if "NAME" in line:
								f.write(line)
							elif "DESCRIPTION" in line:
								f.write(line)
							else:
								for dns in dns_vars:
									tmp_line=self.whitelist_redirection+line.split("\n")[0]+"/"+dns
									f.write(tmp_line+"\n")	
						f.close()
									 					
			#Old n4d: return {'status':True,'msg':'The update of the dns has been carried out successfully','data':""}
			result={'status':True,'msg':'The update of the dns has been carried out successfully','data':""}
			return n4d.responses.build_successful_call_response(result)

		except Exception as e:
			#Old n4d: return {'status':False,'msg':'Error updating white list dns','data':str(e)}							
			result={'status':False,'msg':'Error updating white list dns','data':str(e)}							
			return n4d.responses.build_successful_call_response(result)							

	#def update_whitelist_dns

	def _get_original_file_perms(self,file):

		perms_file=[]
		cmd='ls -l %s'%(file)
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]

		if type(result) is bytes:
			result=result.decode()

		result=result.split(' ')
		try:
			perms_file.append(result[2])
			perms_file.append(result[3])
		except:
			pass

		return perms_file

	#def _get_original_file_perms
