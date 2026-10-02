#!/usr/bin/python3 
import os
import copy
import json
import codecs
import grp
import pwd
import shutil
import ssl
import subprocess
from os import listdir
from os.path import isfile,isdir,join
from pathlib import Path
import n4d.server.core as n4dcore
import n4d.responses


class LliurexGuardManagerNatFree:

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.conf_dir="/etc/lliurex-guard-natfree"
		self.blacklist_dir=os.path.join(self.conf_dir,"blacklist")
		self.blacklist_disable_dir=os.path.join(self.conf_dir,"blacklist.d")
		self.blacklist_redirection="169.254.254.254"
		self.whitelist_dir=os.path.join(self.conf_dir,"whitelist")
		self.whitelist_disable_dir=os.path.join(self.conf_dir,"whitelist.d")
		self.whitelist_redirection="server=/"
		self.list_tmpfile=[]
		self.shared_folder="/var/www/lliurex-guard-natfree"
	
		#def __init__

	def startup(self,options):

		if self._is_server():
			if self._create_guardmode_conf_dir():
				self._startup()

	#def startup

	def _startup(self):

		self.internal_variable=self.core.get_variable("LLIUREXGUARD_NATFREE").get('return',None)

		if self.internal_variable==None:
			try:
				self._initialize_variable()
				self.core.set_variable("LLIUREXGUARD_NATFREE",self.internal_variable)
			except Exception as e:
				print(str(e))

	#def _starup

	def read_guardmode(self):
		
		try:
			self.guardMode=self.internal_variable.get("mode")
			self._set_variables()
			result={'status':True,'msg':"Guard Mode read successfully",'data':self.guardMode}
			return n4d.responses.build_successful_call_response(result)
	
		except Exception as e:
			print(f"[LliurexGuardManagerNatFree]: Unable to read Guard Mode: {e}")
			result={'status':False,'msg':"Unable to read Guard Mode",'data':str(e)}
			return n4d.responses.build_successful_call_response(result)
	
	#def read_guard_mode
	
	def _set_variables(self):

		mapping = {
			"BlackMode": (self.blacklist_dir, self.blacklist_disable_dir, self.blacklist_redirection),
			"WhiteMode": (self.whitelist_dir, self.whitelist_disable_dir, self.whitelist_redirection)
		}

		default_values = ("", "", "")

		self.active_path, self.disable_path, self.redirection = mapping.get(self.guardMode, default_values)
	
	#def _set_variables

	def change_guardmode(self, mode_to_set: str):

		variable = copy.deepcopy(self.internal_variable)
		variable["mode"] = mode_to_set
		active_list = []

		dest_path = Path(self.shared_folder)

		try:
			dest_path.mkdir(parents=True, exist_ok=True)

			for file in dest_path.iterdir():
				if file.is_file():
					file.unlink()

			if mode_to_set in ("BlackMode", "WhiteMode"):
				list_folder = Path(self.blacklist_dir) if mode_to_set == "BlackMode" else Path(self.whitelist_dir)

				if list_folder.exists():
					for file in list_folder.iterdir():
						if file.is_file():
							active_list.append(file.name)
							shutil.copy2(file, dest_path / file.name)

			variable["list_to_config"] = active_list
			self.internal_variable = copy.deepcopy(variable)

			self.core.set_variable("LLIUREXGUARD_NATFREE", variable)
			
			result = {'status': True, 'msg': "Changed LliureX Guard Mode successfully", 'data': ''}
			return n4d.responses.build_successful_call_response(result)

		except Exception as e:
			print(f"[LliurexGuardManagerNatFree]: Error changing Guard Mode: {e}")
			result = {'status': False, 'msg': "Unable to change Guard Mode", 'data': str(e)}	
			return n4d.responses.build_successful_call_response(result)

	#def change_guardmode
	
	def read_guardmode_headers(self):

		list_config = {}

		active_list = self._read_list_headers(self.active_path)

		if not active_list.get('status'):
			return n4d.responses.build_successful_call_response(active_list)

		disable_list = self._read_list_headers(self.disable_path)

		if not disable_list.get('status'):
			return n4d.responses.build_successful_call_response(disable_list)

		combined_data = active_list.get('data', []) + disable_list.get('data', [])

		for count, item in enumerate(combined_data, start=1):
			list_config[str(count)] = item

		result = {
			'status': True, 
			'msg': f'Reading {self.guardMode} successfully', 
			'data': list_config
		}	

		return n4d.responses.build_successful_call_response(result)

	#def read_guardmode_headers

	def read_guardmode_list(self, listId: str, active: bool):

		path_dir = Path(self.active_path) if active else Path(self.disable_path)
		alt_dir = Path(self.disable_path) if active else Path(self.active_path)

		filename = f"{listId}.list"
		target_file = path_dir / filename

		try:
			if not target_file.exists():
				target_file = alt_dir / filename

			if target_file.exists():
				content = []
				count_lines = 0

				lines = target_file.read_text(encoding="utf-8").splitlines()

				for line in lines:
					line = line.strip()
					if not line or "NAME" in line or "DESCRIPTION" in line:
						continue

					if self.redirection in line:
						if self.guardMode == "BlackMode":
							if "address=/" in line:
								domain = line.split("address=/")[1].split(f"/{self.redirection}")[0]
								content.append(f"{domain}\n")
								count_lines += 1
						else:
							parts = line.split(self.redirection)
							if len(parts) > 1:
								domain = parts[1].split("/")[0]
								tmp_line = f"{domain}\n"

								if tmp_line not in content:
									content.append(tmp_line)
									count_lines += 1
					
				result = {'status': True, 'msg': "Read content list successfully", 'data': [content, count_lines]}
				
			else:
				result = {'status': False, 'msg': "Unable to read content list. The file does not exist", 'data': "The file does not exist"}

			return n4d.responses.build_successful_call_response(result)

		except Exception as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Unable to read content list: {e}")
			result = {'status': False, 'msg': "Unable to read content list", 'data': str(e)}
			return n4d.responses.build_successful_call_response(result)
	
	#def read_guardmode_list

	def remove_guardmode_list(self, list_to_manage: list) :

		active_dir = Path(self.active_path)
		disable_dir = Path(self.disable_path)

		try:
			for item in list_to_manage:
				filename = f"{item}.list"
				active_file = active_dir / filename
				disable_file = disable_dir / filename

				if active_file.exists():
					active_file.unlink()
				elif disable_file.exists():
					disable_file.unlink()

			ret = self.change_guardmode(self.guardMode)
			
			if not ret.get("status"):
				return n4d.responses.build_successful_call_response(ret.get("return"))

			result = {'status': True, 'msg': "list_to_manage removed successfully"}
			return n4d.responses.build_successful_call_response(result)      
		
		except Exception as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error removing list_to_manage: {e}")
			result = {'status': False, 'msg': "Error removing list_to_manage", 'data': str(e)}      
			return n4d.responses.build_successful_call_response(result)

	#def remove_guardmode_list
	
	def activate_guardmode_list(self,list_to_manage:list):

		result=self._move_guardmode_list(list_to_manage,self.active_path,self.disable_path)

		if result.get('status'):
			result={'status':True,'msg':"list_to_manage activated successfully"}
			ret=self.change_guardmode(self.guardMode)
			final_response = result if ret.get("status") else ret.get("return")
			return n4d.responses.build_successful_call_response(final_response)
		else:
			return n4d.responses.build_successful_call_response(result)
	
	#def activate_guardmode_list
	
	def deactivate_guardmode_list(self, list_to_manage: list):

		result = self._move_guardmode_list(list_to_manage, self.disable_path, self.active_path)

		if result.get('status'):
			result = {'status': True, 'msg': "list_to_manage deactivated successfully"}
			ret = self.change_guardmode(self.guardMode)
			final_response = result if ret.get("status") else ret.get("return")
			return n4d.responses.build_successful_call_response(final_response)
		else:
			return n4d.responses.build_successful_call_response(result)

	#def deactivate_guardmode_list
	
	def _initialize_variable(self):
		
		self.internal_variable={
			"mode":"DisableMode",
			"list_to_config":[]
		}
		
	#def _initialize_variable

	def _create_guardmode_conf_dir(self):

		directories = [
			Path(self.conf_dir),
			Path(self.blacklist_dir),
			Path(self.blacklist_disable_dir),
			Path(self.whitelist_dir),
			Path(self.whitelist_disable_dir),
			Path(self.shared_folder)
		]

		try:
			for directory in directories:
				directory.mkdir(parents=True, exist_ok=True)

			return True 
		except OSError as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error creating guardmode configuration directories: {e}")
			return False

	#def _create_guardmode_conf_dir

	def _is_server(self):

		try:
			result = subprocess.run(
				['lliurex-version', '-v'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)

			flavours = [x.strip() for x in result.stdout.split(',') if x.strip()]

			return any('adi' in item or 'pro' in item for item in flavours)
		except (subprocess.CalledProcessError, FileNotFoundError) as e:
			print(f"[LliurexGuardManagerNatFree]: Error checking LliureX version: {e}")
			return False
	
	#def _is_server
	
	def _read_list_headers(self, folder: str):

		files_headers = []
		folder_path = Path(folder)

		try:
			if folder_path.exists():
				for file_path in folder_path.iterdir():
					if file_path.is_file() and file_path.suffix == '.list':
						tmp = {
							"id": file_path.stem,
							"active": folder not in (self.blacklist_disable_dir, self.whitelist_disable_dir),
							"name": "",
							"description": "",
							"lines": 0
						}

						lines = file_path.read_text(encoding="utf-8").splitlines()
						match_count = 0

						for line in lines:
							line = line.strip()
							if "NAME" in line and ":" in line:
								tmp["name"] = line.split(":", 1)[1].strip()
								match_count += 1
							elif "DESCRIPTION" in line and ":" in line:
								tmp["description"] = line.split(":", 1)[1].strip()
								match_count += 1

							if match_count == 2:
								tmp["lines"] = max(0, len(lines) - 2)
								break
						files_headers.append(tmp)
			return {'status': True, 'msg': "list_to_manage read successfully", 'data': files_headers}

		except Exception as e: 
			print(f"[LliurexGuardManagerNatFree]: Error reading list_to_manage: {e}")
			return {'status': False, 'msg': "Unable to read list_to_manage", 'data': str(e)}

  	#def _read_list_headers

	def _move_guardmode_list(self, list_to_manage:list, dest_path: str, orig_path: str):
		
		dest_dir = Path(dest_path)
		orig_dir = Path(orig_path)

		try:
			for item in list_to_manage:
				item_id = item.get("id")
				tmp_file_str = item.get("tmpfile", "")

				dest_file = dest_dir / f"{item_id}.list"
				orig_file = orig_dir / f"{item_id}.list"

				if tmp_file_str != "":
					tmp_file = Path(tmp_file_str)

					result_format = self._format_guardmode_list(item)

					if result_format.get('status'):
						shutil.copy2(tmp_file, dest_file)
						dest_file.chmod(0o644)
						self.list_tmpfile.append(tmp_file_str)

						if orig_file.exists():
							orig_file.unlink()
					else:
						return result_format    
				else:
					if orig_file.exists():
						shutil.copy2(orig_file, dest_file)			
						orig_file.unlink()

			return {'status': True, 'msg': ""}

		except Exception as e:
			print(f"[LliurexGuardManagerNatFree]: Error copying list: {e}")
			return {'status': False, 'msg': "Error copying list", 'data': str(e)}
	
	#def _move_guardmode_list

	def _format_guardmode_list(self, item: dict):

		try:
			tmp_file = Path(item["tmpfile"])
			if tmp_file.exists():
				lines = tmp_file.read_text(encoding="utf-8").splitlines()
				stat_info = tmp_file.stat()
				orig_uid = stat_info.st_uid
				orig_gid = stat_info.st_gid
				try:
					os.chown(tmp_file, 0, 0)
				except OSError as e:
					print(f"[LliurexGuardManagerNatFree]: Warning, could not chown to root: {e}")

				output_lines = [
					f"#NAME:{item['name']}",
					f"#DESCRIPTION:{item['description']}"
					]

				for line in lines:
					line = line.strip()
					if not line:
						continue

					if self.redirection in line:
						output_lines.append(line)
					else:
						if "https" in line:
							line = line.replace("https://", "")
						else:
							line = line.replace("http://", "")

						if len(line.split("/")) == 1:
							if self.guardMode == "BlackMode":
								output_lines.append(f"address=/{line}/{self.redirection}")
							else:
								output_lines.append(f"{self.redirection}{line}")
				tmp_file.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
				try:
					os.chown(tmp_file, orig_uid, orig_gid)
				except OSError as e:
					print(f"[LliurexGuardManagerNatFree]: Error restoring original permissions: {e}")

			return {'status': True, 'msg': 'List formatted successfully'}

		except Exception as e:
			print(f"[LliurexGuardManagerNatFree]: Error formatting the list: {e}")
			return {'status': False, 'msg': 'Error formatting the list', 'data': str(e)}
	
	#def _format_guardmode_list	
