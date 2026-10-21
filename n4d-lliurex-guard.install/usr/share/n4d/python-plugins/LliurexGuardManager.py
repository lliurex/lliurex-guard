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

class LliurexGuardManager:

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.mode_file_path=Path("/etc/dnsmasq.d/lliurex-guard.conf")
		self.natfree_mode_file_path=Path("/etc/dnsmasq.d/lliurex-guard-natfree.conf")
		self.conf_dir=Path("/etc/lliurex-guard")
		self.blacklist_dir=self.conf_dir / "blacklist"
		self.blacklist_disable_dir=self.conf_dir / "blacklist.d"
		self.blacklist_redirection="169.254.254.254"
		self.whitelist_dir=self.conf_dir / "whitelist"
		self.whitelist_disable_dir=self.conf_dir / "whitelist.d"
		self.whitelist_redirection="server=/"
		self.guard_lib_dir=Path("/var/lib/lliurex-guard")
		self.first_init_path=self.guard_lib_dir / "first_init"
		self.blacklist_dir=self.conf_dir / "blacklist"
		self.dnsmasq_lib_dir=Path("/var/lib/dnsmasq/config")
		self.dnsmasq_override_service=Path("/etc/systemd/system/dnsmasq.service.d/")
		self.dnsmasq_override_service_conf=self.dnsmasq_override_service / "lliurex-guard-override.conf"		
		self.natfree_dnsmasq_override_service_conf=self.dnsmasq_override_service / "lliurex-guard-natfree-override.conf"
		self.set_bm_mode="conf-dir = /etc/lliurex-guard/blacklist"
		self.disable_bm_mode="#conf-dir = /etc/lliurex-guard/blacklist"
		self.set_wm_mode="conf-dir = /etc/lliurex-guard/whitelist"
		self.disable_wm_mode="#conf-dir = /etc/lliurex-guard/whitelist"
		self.whitelist_filter="address=/#/"+self.blacklist_redirection
		self.disable_whitelist_filter="#"+self.whitelist_filter
		self.list_tmpfile=[]
		self.list_to_active=[]
		self.resolvconf_path=Path("/etc/systemd/resolved.conf.d/lliurex-dnsmasq.conf")
		self.network_plugin_path=Path("/usr/share/n4d/python-plugins/NetworkManager")
	
	def startup(self,options):

		if self._is_desktop_standalone():
			self._remove_natfree_config()

	#def startup()

	def read_guardmode(self,checkconfig=False):
		
		try:
			if not self.first_init_path.exists():
				self._first_init()

			if not self.mode_file_path.exists():
				self._create_guardmode_conf_file()

			lines=self.mode_file_path.read_text(encoding="utf-8").splitlines()
			count=sum(1 for line in lines if "#" in line)
			if count >= 3:
				self.guardMode="DisableMode"
			else:
				active_lines=[line for line in lines if "#" not in line]

				if any("blacklist" in line for line in active_lines):
					self.guardMode="BlackMode"
				else:
					self.guardMode="WhiteMode"

			self._set_variables()
			result={'status':True,'msg':"Guard Mode read successfully",'data':self.guardMode}
			return n4d.responses.build_successful_call_response(result)
	
		except Exception as e:
			print(f"[LliurexGuardManager]: Unable to read Guard Mode: {e}")
			result={'status':False,'msg':"Unable to read Guard Mode",'data':str(e)}
			return n4d.responses.build_successful_call_response(result)
	
	#def read_guard_mode

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

		path_dir = self.active_path if active else self.disable_path
		alt_dir = self.disable_path if active else self.active_path

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
			print(f"[LliurexGuardManagerClient]: Unable to read content list: {e}")
			result = {'status': False, 'msg': "Unable to read content list", 'data': str(e)}
			return n4d.responses.build_successful_call_response(result)
	
	#def read_guardmode_list	

	def remove_guardmode_list(self, list_to_manage: list) :

		active_dir = self.active_path
		disable_dir = self.disable_path

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
			print(f"[LliurexGuardManagerClient]: Error removing list_to_manage: {e}")
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

	def change_guardmode(self,mode_to_set,rescue=False):

		ret = None
		ret_list = False
		enable_dnsmasq = False
		restart_dnsmasq = False
		base_lines=["listen-address=127.0.0.1","interface=lo","bind-interfaces","conf-dir=/var/lib/dnsmasq/config"]

		ret_config=self._create_guardmode_conf_dir()

		if not ret_config.get("status"):
			result = {'status': False, 'msg': "Unable to change Guard Mode", 'data': ret_config.get("data")}
			return n4d.responses.build_successful_call_response(result)

		if mode_to_set == "BlackMode":
			lines = [self.set_bm_mode, self.disable_wm_mode, self.disable_whitelist_filter]
			enable_dnsmasq=True
			restart_dnsmasq=True
		elif mode_to_set == "WhiteMode":
			lines = [self.disable_bm_mode, self.set_wm_mode, self.whitelist_filter]
			enable_dnsmasq=True
			restart_dnsmasq=True
		else:
			lines = [self.disable_bm_mode, self.disable_wm_mode, self.disable_whitelist_filter]

		try:
			base_lines.extend(lines)
			self.mode_file_path.write_text("\n".join(str(l) for l in base_lines) + "\n", encoding="utf-8")
		except OSError as file_error:
			msg_log=f"Failed to write configuration file: {file_error}"
			print(f"[LliurexGuardManagerClient]: {msg_log}")
			result = {'status': False, 'msg': "Unable to change Guard Mode", 'data': str(file_error)}
			return n4d.responses.build_successful_call_response(result)
	
		ret_manage = self._manage_dnsmasq_service(enable_dnsmasq)
			
		if not ret_manage.get("status"):
			self._safe_fallback_to_disable()
			result = {'status': False, 'msg': "Unable to change Guard Mode", 'data': ret_manage}
			return n4d.responses.build_successful_call_response(result)

		if restart_dnsmasq:
			ret_restart=self.restart_dnsmasq().get("return")
			if not ret_restart.get("status"):
				self._safe_fallback_to_disable()
				result = {'status': False, 'msg': "Unable to change Guard Mode", 'data': ret_restart}
				return n4d.responses.build_successful_call_response(result)

		ret=ret_manage
		result = {'status': True, 'msg': "Changed LliureX Guard Mode successfully", 'data': ret}
		self.guardMode=mode_to_set
		return n4d.responses.build_successful_call_response(result)

	#def change_guardmode
	
	def restart_dnsmasq(self):
		
		error = False
		data = ""
		
		try:
			subprocess.run(
				['systemctl', 'restart', 'dnsmasq.service'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)
		except subprocess.CalledProcessError as e:
			error = True
			data = f"Error {e.returncode}: {e.stderr.strip()}"
		except Exception as e:
			error = True
			data = str(e)

		if not error:
			result = {'status': True, 'msg': "Dnsmasq restarted successfully"}
			return n4d.responses.build_successful_call_response(result)
		else:
			msg="Error restarting Dnsmasq"
			result = {'status': False, 'msg':msg, 'data': data}
			return n4d.responses.build_successful_call_response(result)

	#def restart_dnsmasq

	def update_whitelist_dns(self):

		dns_vars = self._get_dns()

		try:
			if self.whitelist_dir.exists():
				for file_path in self.whitelist_dir.iterdir():
					if file_path.is_file():
						content = set() 
						format_lines = []

						lines = file_path.read_text(encoding="utf-8").splitlines()

						for line in lines:
							line = line.strip()
							if not line:
								continue

							if "NAME" in line or "DESCRIPTION" in line:
								format_lines.append(line)
							else:
								if self.whitelist_redirection in line:
									parts = line.split(self.whitelist_redirection)
									if len(parts) > 1:
										domain = parts[1].split("/")[0].strip()
										if domain and domain not in content:
											content.add(domain)
											format_lines.append(domain)

						output_lines = []
						for line in format_lines:
							if "NAME" in line or "DESCRIPTION" in line:
								output_lines.append(line)
							else:
								for dns in dns_vars:
									if dns.strip():
										output_lines.append(f"{self.whitelist_redirection}{line}/{dns.strip()}")

						file_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
				result = {'status': True, 'msg': 'The update of the dns has been carried out successfully', 'data': ""}
				return n4d.responses.build_successful_call_response(result)

		except Exception as e:
			msg_log=f"Error Updating white list dns: {e}"
			print(f"[LliurexGuardManagerClient]: {msg_log}")
			result = {'status': False, 'msg': 'Error updating white list dns', 'data': str(e)}
			return n4d.responses.build_successful_call_response(result)
	
	#def update_whitelist_dns	
	
	def _set_variables(self):

		mapping = {
			"BlackMode": (self.blacklist_dir, self.blacklist_disable_dir, self.blacklist_redirection),
			"WhiteMode": (self.whitelist_dir, self.whitelist_disable_dir, self.whitelist_redirection)
		}

		default_values = (Path(""), Path(""), Path(""))

		self.active_path, self.disable_path, self.redirection = mapping.get(self.guardMode, default_values)
	
	#def _set_variables

	def _check_dnsmasq_conf(self):

		extra_dns_file = self.dnsmasq_lib_dir / "extra-dns"

		try:
			if not extra_dns_file.exists():
				desktop_dns = self._get_desktop_dns()
				dns_lines = [f"server={item}" for item in desktop_dns if item]
				extra_dns_file.write_text("\n".join(dns_lines) + "\n", encoding="utf-8")

			if not self.mode_file_path.exists():
				self._create_guardmode_conf_file()

		except OSError as e:
			msg_log=f"Error checking dnsmasq configuration: {e}"
			print(f"[LliurexGuardManager]: {msg_log}")

	#def _check_dnsmasq_conf

	def _create_guardmode_conf_file(self):

		try:
			lines = [
				"#listen-address = 127.0.0.1",
				"#interface = lo",
				"#bind-interfaces",
				"conf-dir = /var/lib/dnsmasq/config",
				f"{self.disable_bm_mode}",
				f"{self.disable_wm_mode}",
				f"{self.disable_whitelist_filter}"
			]
			self.mode_file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
		
		except OSError as e:
			msg_log=f"Error writing configuration file: {e}"
			print(f"[LliurexGuardManager]: {msg_log}")

	#def _create_guardmode_conf_file:

	def _create_guardmode_conf_dir(self):

		directories = [
			self.conf_dir,
			self.blacklist_dir,
			self.blacklist_disable_dir,
			self.whitelist_dir,
			self.whitelist_disable_dir,
		]

		try:
			for directory in directories:
				directory.mkdir(parents=True, exist_ok=True)

			return {"status":True,"data":""}
		except OSError as e:
			print(f"[LliurexGuardManager]: Error creating guardmode configuration directories: {e}")
			return {"status":False,"data":e}

	#def _create_guardmode_conf_dir

	def _get_dns(self):

		dns_vars=[]

		dns_vars=self._get_desktop_dns()
		
		return dns_vars

	#def _get_dns	

	def _first_init(self):
	
		try:
			self.guard_lib_dir.mkdir(parents=True, exist_ok=True)
			self.dnsmasq_lib_dir.mkdir(parents=True, exist_ok=True)
		except OSError as e:
			print(f"[LliurexGuardManager]: Error creating directories: {e}")
			return

		self._check_dnsmasq_conf()

		try:
			self.first_init_path.touch(exist_ok=True)
		except OSError as e:
			print(f"[LliurexGuardManager]: Error creating init file: {e}")

	#def _first_init

	def _get_desktop_dns(self):

		desktop_dns = []

		try:
			result = subprocess.run(
				['nmcli', '-g', 'IP4.DNS,IP6.DNS', 'device', 'show'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True, 
				check=True
			)

			for line in result.stdout.splitlines():
				clean_line = line.strip()
				if clean_line:
					desktop_dns = [ip.strip() for ip in clean_line.split('|')]
		except (subprocess.CalledProcessError, FileNotFoundError) as e:
			msg_log=f"Error getting desktop DNS: {e}"
			print(f"[LliurexGuardManager]: {msg_log}")

		return desktop_dns

	#def _get_desktop_dns 	

	def _manage_dnsmasq_service(self, enable_service: bool):

		action = "enable" if enable_service else "disable"

		if not enable_service:
			error_stop, data_stop = self._stop_dnsmasq_service()
			if error_stop:
				msg_log=f"Error stopping Dnsmasq. Details: {data_stop}"
				print(f"[LliurexGuardManagerClient]: {msg_log}")
				return {'status': False, 'msg': "Error stopping Dnsmasq", 'data': data_stop}
		try:
			subprocess.run(
				['systemctl', action, 'dnsmasq.service'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)

			self._override_dnsmasq_service(enable_service)
			self._manage_resolvconf(enable_service)
			msg = f"Dnsmasq {action} successfully"
			return {'status': True, 'msg': msg}
			
		except subprocess.CalledProcessError as e:
			error_msg = f"Error: Dnsmasq {action} failed"
			details = f"Error {e.returncode}: {e.stderr.strip()}"
			print(f"[LliurexGuardManagerClient]: {error_msg}. Details: {details}")
			return {'status': False, 'msg': error_msg, 'data': details}
		except Exception as e:
			error_msg = f"Error: Dnsmasq {action} failed. Details:{e}"
			print(f"[LliurexGuardManagerClient]: {error_msg}")
			return {'status': False, 'msg': error_msg, 'data': str(e)}

	#def manage_dnsmasq_service

	def _override_dnsmasq_service(self,enable_service=True):

		reload_daemon=False

		if enable_service:
			if not self.dnsmasq_override_service_conf.exists():
				conf = '[Service]\nEnvironment="DNSMASQ_EXCEPT=lo"\nEnvironment="IGNORE_RESOLVCONF=yes"'
				self.dnsmasq_override_service_conf.parent.mkdir(parents=True, exist_ok=True)
				self.dnsmasq_override_service_conf.write_text(conf,encoding='utf-8')
				reload_daemon=True
		
		if reload_daemon:
			subprocess.run(['systemctl', 'daemon-reload'], check=True)

	#def _override_dnsmasq_service

	def _stop_dnsmasq_service(self):

		error = False
		data = ""

		try:
			is_active=(
				subprocess.run(["systemctl","is-active","dnsmasq"],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True,
				).returncode
				==0
			)
			if is_active:
				result = subprocess.run(
					['systemctl', 'stop', 'dnsmasq.service'],
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,
					text=True,
					check=True
				)
		except subprocess.CalledProcessError as e:
			error = True
			data = f"Error {e.returncode}: {e.stderr.strip()}"
		except Exception as e:
			error = True
			data = str(e)

		return [error, data]
	
	#def stop_dnsmasq_service

	def _manage_resolvconf(self, active: bool):

		if active:
			if not self.resolvconf_path.exists():
				subprocess.run(['systemctl', 'stop', 'systemd-resolved'], check=True)
				if self.network_plugin_path.exists():
					self.core.get_plugin('NetworkManager').systemd_resolv_conf()
				else:
					conf = "[Resolve]\nDNS=127.0.0.1\nDNSStubListener=no\n"
					self.resolvconf_path.parent.mkdir(parents=True, exist_ok=True)
					self.resolvconf_path.write_text(conf,encoding='utf-8')

				subprocess.run(['systemctl', 'restart', 'systemd-resolved'], check=True)
		else:
			if self.resolvconf_path.exists():
				try:
					self.resolvconf_path.unlink()
				except OSError:
					pass

				subprocess.run(['systemctl', 'restart', 'systemd-resolved'], check=True)

	#def _manage_resolvconf	

	def _safe_fallback_to_disable(self):

		try:
			lines = ["#listen-address = 127.0.0.1","#interface = lo","#bind-interfaces","conf-dir = /var/lib/dnsmasq/config",self.disable_bm_mode, self.disable_wm_mode, self.disable_whitelist_filter]
			self.mode_file_path.write_text("\n".join(str(l) for l in lines) + "\n", encoding="utf-8")
			self.guardmode="DisableMode"
			self._manage_dnsmasq_service(False)
		except Exception as e:
			msg_log=f"Critial error during _safe_fallback_to_disable. Error:{e}"
			print(f"[LliurexGuardManager]: {msg_log}")

	#def _safe_fallback_to_disable			
	
	def _read_list_headers(self, folder):

		files_headers = []

		try:
			if folder.exists():
				for file_path in folder.iterdir():
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
			print(f"[LliurexGuardManager]: Error reading list_to_manage: {e}")
			return {'status': False, 'msg': "Unable to read list_to_manage", 'data': str(e)}

  	#def _read_list_headers
	
	def _move_guardmode_list(self, list_to_manage, dest_path, orig_path):
		
		dest_dir = dest_path
		orig_dir = orig_path

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
			print(f"[LliurexGuardManager]: Error copying list: {e}")
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
					print(f"[LliurexGuardManager]: Warning, could not chown to root: {e}")

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
					print(f"[LliurexGuardManager]: Error restoring original permissions: {e}")

			return {'status': True, 'msg': 'List formatted successfully'}

		except Exception as e:
			print(f"[LliurexGuardManager]: Error formatting the list: {e}")
			return {'status': False, 'msg': 'Error formatting the list', 'data': str(e)}
	
	#def _format_guardmode_list

	def _is_desktop_standalone(self):

		normalizedFlavours=["adi","pro","alu"]

		try:
			result = subprocess.run(
				['lliurex-version', '-v'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)

			flavours = [x.strip() for x in result.stdout.split(',') if x.strip()]

			return all(p not in i for i in flavours for p in normalizedFlavours)
		
		except (subprocess.CalledProcessError, FileNotFoundError) as e:
			msg_log="Error checking LliureX version: {e}"
			print(f"[LliurexGuardManager]: {msg_log}")
			return False

	#def _is_desktop_standalone

	def _remove_natfree_config(self):

		
		if self.natfree_mode_file_path.exists():
			try:
				self.natfree_mode_file_path.unlink()
			except OSError:
				pass
		
		if self.natfree_dnsmasq_override_service_conf.exists():
			try:
				self.natfree_dnsmasq_override_service_conf.unlink()
				subprocess.run(['systemctl', 'daemon-reload'])
			except OSError:
				pass

	#def _remove_natfree_config	
			
#class LliurexGuardManager
