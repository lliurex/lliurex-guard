import os
import json
import shutil
from subprocess import check_output

class LliurexGuard:
	def __init__(self):
		pass
	#def __init
	
	
	def applyPolicy(self, config):
		try:
			print json.dumps(config)
			print config["policy"]
			print config["whitelist"]
			print config["blacklist"]
			print config["classdomain"]
			
			self.generateSquidList("/etc/squid/lliurex/allow-dst-domains.conf", config["whitelist"], config["classdomain"]);
			self.generateSquidList("/etc/squid/lliurex/deny-dst-domains.conf", config["blacklist"]);
			
			
			return self.generateSquidConf(config["policy"], config["classdomain"], config["whitelist"], config["blacklist"]);
		
		
		except:
			return {"status":"false"}
		
		
		
	
	def getBlackList(self):
		
		try:
			# Reading blacklist specification
			blacklistfile="/etc/lliurex-guard-data/config/blacklist.json"
			if os.path.isfile(blacklistfile):
				json_data=open(blacklistfile)
				print json_data
				conf = json.load(json_data)
				json_data.close()
				
				
			else:
				return {"status":"false"}
			
			# Reading blacklist active items
			blacklistConfig="/etc/lliurex-guard-easy/currentConfig.json"
			if os.path.isfile(blacklistConfig):
				json_data=open(blacklistConfig)
				activeItems = json.load(json_data)
				json_data.close()
			else:
				return {"status":"false"}
			
			for item in conf["domainLists"]:
				if item["file"] in activeItems["blacklist"]:
					item["active"]="True"
				else:
					item["active"]="False"
						
			
			return {"status":"true", "response":conf}
		except Error:
			print "[LliurexGuard]:getBlacList Exception "+str(Error)
			return {"status":"true", "response":conf}
		
		
	def getWhiteList(self):		
		try:
			classdomain="False"
			customWhite="False"
			
			# Reading blacklist active items
			Config="/etc/lliurex-guard-easy/currentConfig.json"
			if os.path.isfile(Config):
				json_data=open(Config)
				activeItems = json.load(json_data)
				json_data.close()
				if "z_customwhite.list" in activeItems["whitelist"]:
					customWhite="True"
				if activeItems["class_domain"]!="":
					classdomain="True"
				
			internal_domain=objects['VariablesManager'].get_variable('INTERNAL_DOMAIN')
			whitelist=[{"file":None, "domain":internal_domain, 
			"description_short":"Classroom Domain", 
			"description": "Allow access to classroom services such as JClic, local Moodle...",
			"active":classdomain},
			{"file":"z_customwhite.list", 
			"description_short":"Custom List", 
			"description": "Customize your own white list with other domains",
			"active":customWhite}]
			
			response={"domainLists":whitelist};
			return {"status":"true", "response": response}

		except:
			return {"status":"false"}
			
			
			
	def getCustomList(self, file):
		filepath="/etc/lliurex-guard-data/config/lists/"+file
		if os.path.isfile(filepath):
			fd=open(filepath)
			list=fd.read()
			fd.close()
			return {"status":"true", "response":list}
			
		else: 
			return  {"status":"false"}
		pass
		
		
	def setCustomList(self, content, file):
		try:
			filepath="/etc/lliurex-guard-data/config/lists/"+file
			fd=open(filepath, "w")
			list=fd.write(content)
			fd.close()
			return {"status":"true"}
		except:
			return {"status":"false"}
		
		
		pass

	def generateSquidConf(self, template="default", classdomain="",  whitelist=[], blacklist=[]):
		'''
		Generates /etc/squid.conf with a specified template: default, deny or allow
		'''
		try:
			orig=open("/etc/squid/squid.conf", "r");
			dest=open("/tmp/squid.conf", "w");
	
			ignore_line=False;
	
			for line in orig:
				print line
				
				# Activate writing after hack
				if (line=="http_access deny !Safe_ports\n"):
					ignore_line=False;
					
				if ignore_line==False:
					dest.write(line);
				
				
				# Deactivate writing before hack
				if (line=="http_access deny deny_dst\n"):
					ignore_line=True;
				
					if template=="deny":
						dest.write("\n\n# LliureXGuard: Only allow domains specified\n");
						dest.write("http_access deny !allow_domain\n");
						dest.write("# End LliureXGuard\n\n");
						
					elif template=="allow":
						dest.write("\n\n# LliureXGuard:  Allow domains except the specified in deny_dst_domains\n");
						dest.write("http_access deny deny_domain\n");
						dest.write("\n# Regulat Expressions\n");
						dest.write("http_access deny deny_domain_expr\n");
						dest.write("# End LliureXGuard\n\n");
						
					else:
						dest.write("\n\n# LliureXGuard:  Default behaviour\n");
						dest.write("http_access deny deny_domain\n");
						dest.write("http_access deny deny_domain_expr\n");
						dest.write("http_access allow allow_domain\n");
						dest.write("# End LliureXGuard\n\n");
						
			
			
			dest.close()
			orig.close()
			
			shutil.copyfile("/tmp/squid.conf", "/etc/squid/squid.conf")
			
			# Setting current config
			fileConfig=open("/etc/lliurex-guard-easy/currentConfig.json","w")
			fileConfig.write('{\n"current_config":"'+str(template)+'",\n');
			fileConfig.write('"class_domain":"'+str(classdomain)+'",\n');
			fileConfig.write('"whitelist":'+str(whitelist).replace("'", '"')+',\n');
			fileConfig.write('"blacklist":'+str(blacklist).replace("'", '"')+'\n}');
			fileConfig.close();

			
			
			os.system("invoke-rc.d squid restart")
			
			
			return {"status":"true"}
			
		except:
			
			return {"status":"false"}
					
					
	def generateSquidList(self, destfile, listfiles, extradomain=""):
		''' Generates list file 
		 Commonly /etc/squid/lliurex/allow-dst-domains.conf  as whitelist
		 or /etc/squid/lliurex/deny-dst-domains.conf as blacklist
		 if listfiles is an empty list, generates an empty file (useful to reset config)
		 '''
		
		path	='/etc/lliurex-guard-data/config/lists/'
	
		dest=open(destfile, "w")
	
		for file in listfiles:
			fullpath=path+str(file)
			if(os.path.isfile(fullpath)):
				f=open(fullpath, "r");
				for line in f:
					if line!="\n":
						dest.write(line);
				
				f.close()
				
		# Adding extra domain
		if extradomain!="":
			dest.write("\n"+extradomain);
		dest.close();
	
	
	def getStatus(self):
		'''
		Returns status of squid (running, or stop), and which template is running
		'''
		# Getting current template
		
		try:
			currentConf="/etc/lliurex-guard-easy/currentConfig.json"
			
			json_data=open(currentConf)
			conf = json.load(json_data)
			json_data.close()
			current_conf=conf["current_config"];
		
		except:
			current_conf=["unconfigured"];

					
		# Getting status
		
		try:
			output=check_output(["pidof", "squid"])
			return {"status":"running", "config":current_conf}
		except:
			return  {"status":"stop", "config":current_conf}
			
		pass
		
	'''def getGuardTemplate(self, template="default"):
		'' '
		Return Configuration specified in "template", if it's not
		specified, returns current configuration file.
		'' '
		fullpath="/etc/lliurex-guard-easy/"+str(template)+".json"
		
		if not os.path.isfile(fullpath):
			return {"policy":"none"}
		else:
			json_data=open(fullpath)
			data=json.load(json_data)
			json_data.close();
			return data;
		
	def setGuardTemplate(self,  conffile, config):
		# Saves json config to file conffile
		fullpath="/etc/lliurex-guard-easy/"+str(template)+".json"
		# TO  DO
	'''
		
