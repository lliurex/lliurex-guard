#!/usr/bin/python3  
import os
import json
import codecs
import shutil
import ssl
import subprocess
import threading
import n4d.server.core as n4dcore
import n4d.responses
import urllib
import requests
import time
from os import listdir
from os.path import isfile,isdir,join
from pathlib import Path

class LliurexGuardManagerNatFreeClient:

	NATFREE_STARTUP=True

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.default_white_list_path=Path("/usr/share/lliurex-guard-natfree/data/default_white_list.list")
		self.mode_file_path=Path("/etc/dnsmasq.d/lliurex-guard-natfree.conf")
		self.conf_dir=Path("/etc/lliurex-guard-natfree")
		self.guard_lib_dir=Path("/var/lib/lliurex-guard-natfree")
		self.first_init_path=self.guard_lib_dir / "first_init"
		self.blacklist_dir=self.conf_dir / "blacklist"
		self.dnsmasq_lib_dir=Path("/var/lib/dnsmasq/config")
		self.dnsmasq_conf = Path('/etc/dnsmasq.conf')
		self.set_bm_mode="conf-dir = /etc/lliurex-guard-natfree/blacklist"
		self.blacklist_redirection="169.254.254.254"
		self.disable_bm_mode="#conf-dir = /etc/lliurex-guard/blacklist"
		self.whitelist_dir=self.conf_dir / "whitelist"
		self.set_wm_mode="conf-dir = /etc/lliurex-guard-natfree/whitelist"
		self.disable_wm_mode="#conf-dir = /etc/lliurex-guard/whitelist"
		self.whitelist_redirection="server=/"
		self.whitelist_filter="address=/#/"+self.blacklist_redirection
		self.disable_whitelist_filter="#"+self.whitelist_filter
		self.list_tmpfile=[]
		self.list_to_active=[]
		self.server_download_url="http://server/lliurex-guard-natfree/"
		self.guardmanager_var={}
		
	#def __init__

	def startup(self,options):

		t=threading.Thread(target=self._check_connection)
		t.daemon=True
		t.start()

	#def startup

	def _check_connection(self):

		configure_guard=False

		if self._is_client_mode():
			max_retries=10
			time_to_check=1
			time_count=0
			count_retry=1
			time.sleep(2)

			while True:
				if time_count>=time_to_check:
					configure_guard=self._check_connection_with_adi()
					if configure_guard:
						break
					else:
						if count_retry<max_retries:
							count_retry+=1
							time_count=0
						else:
							break
				else:
					time_count+=1
				
				time.sleep(1)

		if configure_guard:
			if not self.first_init_path.exists():
				self._first_init()
			self._startup()

		else:
			if not self.first_init_path.exists():
				return
			else:
				self.change_guardmode("DisableMode")

	#def _check_connection

	def _startup(self):

		self.core.register_variable_trigger("LLIUREXGUARD_NATFREE","LliurexGuardManagerNatFreeClient",self.guardmanager_trigger)

		tries=10

		for x in range(0,tries):

			self.guardmanager_var=self.core.get_variable("LLIUREXGUARD_NATFREE").get("return")
			if self.guardmanager_var!=None:
				self.guardmanager_trigger(self.guardmanager_var)
				break;
			else:
				time.sleep(1)

		if self.guardmanager_var==None:
			self.guardmanager_var={}

	#def _startup

	def guardmanager_trigger(self,value):

		if value!=None:
			self.change_guardmode(value.get("mode"),list_to_config=value.get("list_to_config"))

	#def guardmanager_trigger

	def read_guardmode(self):

		current_mode=self.guardmanager_var.get("mode","DisableMode")

		result={'status':True,'msg':"Read LliureX Guard Mode",'data': current_mode}
		
		return n4d.responses.build_successful_call_response(result)

	#def read_guardmode

	def change_guardmode(self, mode_to_set: str, list_to_config: list = None):

		if list_to_config is None:
			list_to_config = []

		ret = None

		try:
			self._create_guardmode_conf_dir(mode_to_set)

			if mode_to_set == "BlackMode":
				lines = [self.set_bm_mode, self.disable_wm_mode, self.disable_whitelist_filter]
			elif mode_to_set == "WhiteMode":
				lines = [self.disable_bm_mode, self.set_wm_mode, self.whitelist_filter]
			elif mode_to_set == "DisableMode":
				lines = [self.disable_bm_mode, self.disable_wm_mode, self.disable_whitelist_filter]
			else:
				lines = [self.disable_bm_mode, self.disable_wm_mode, self.disable_whitelist_filter]

			self.mode_file_path.write_text("\n".join(str(l) for l in lines) + "\n", encoding="utf-8")
			
			if mode_to_set != "DisableMode":
				ret_list = self._get_list_from_server(mode_to_set, list_to_config)
				if ret_list:
					ret = self._manage_dnsmasq_service(True)
			else:
				ret = self._manage_dnsmasq_service(False)

			result = {'status': True, 'msg': "Changed LliureX Guard Mode successfully", 'data': ret}
			return n4d.responses.build_successful_call_response(result)

		except Exception as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error changing Guard Mode: {e}")
			result = {'status': False, 'msg': "Unable to change Guard Mode", 'data': str(e)}	
			return n4d.responses.build_successful_call_response(result)

	#def change_guardmode

	def restart_dnsmasq(self, nonretry: bool = False):
		
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
			if not nonretry:
				self.change_guardmode("DisableMode", True)

			result = {'status': False, 'msg': "Error restarting Dnsmasq", 'data': data}
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
			print(f"[LliurexGuardManagerNatFreeClient]: Error Updating white list dns: {e}")
			result = {'status': False, 'msg': 'Error updating white list dns', 'data': str(e)}
			return n4d.responses.build_successful_call_response(result)
	
	#def update_whitelist_dns

	def _is_client_mode(self):

		try:
			result = subprocess.run(
				['lliurex-version', '-v'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)

			flavours = [x.strip() for x in result.stdout.split(',') if x.strip()]

			return any('alu' in item for item in flavours)
		except (subprocess.CalledProcessError, FileNotFoundError) as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error checking LliureX version: {e}")
			return False

	#def is_client_mode

	def _check_connection_with_adi(self):

		try:
			client=n4d.client.Client("https://server:9779",timeout=10)
			test=client.LliurexGuardManagerNatFree.read_guardmode()
			return True
		except Exception as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Check connection with adi Error:{e}")
			return False

	#def _check_connection_with_adi

	def _check_dnsmasq_conf(self):

		extra_dns_file = self.dnsmasq_lib_dir / "extra-dns"

		try:
			if not self.dnsmasq_conf.exists():
				self.dnsmasq_conf.touch(exist_ok=True)

			content = self.dnsmasq_conf.read_text(encoding="utf-8")

			new_directives = []
			if "conf-dir=/etc/dnsmasq.d/" not in content:
				new_directives.append("conf-dir=/etc/dnsmasq.d/\n")
			if "conf-dir=/var/lib/dnsmasq/config" not in content:
				new_directives.append("conf-dir=/var/lib/dnsmasq/config\n")

			if new_directives:
				self.dnsmasq_conf.write_text("".join(new_directives),encoding="utf-8", mode="a")

			if not extra_dns_file.exists():
				desktop_dns = self._get_desktop_dns()
				dns_lines = [f"server={item}" for item in desktop_dns if item]
				extra_dns_file.write_text("\n".join(dns_lines) + "\n", encoding="utf-8")

			if not self.mode_file_path.exists():
				self._create_guardmode_conf_file()

		except OSError as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error checking dnsmasq configuration: {e}")

	#def _check_dnsmasq_conf

	def _create_guardmode_conf_file(self):

		try:
			lines = [
				f"{self.disable_bm_mode}",
				f"{self.disable_wm_mode}",
				f"{self.disable_whitelist_filter}"
			]
			self.mode_file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
		
		except OSError as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error writing configuration file: {e}")

	#def _create_guardmode_conf_file:

	def _create_guardmode_conf_dir(self, mode_to_set: str):

		try:
			self.conf_dir.mkdir(parents=True, exist_ok=True)
			if mode_to_set == "BlackMode":
				self.blacklist_dir.mkdir(parents=True, exist_ok=True)
			elif mode_to_set == "WhiteMode":
				self.whitelist_dir.mkdir(parents=True, exist_ok=True)
		except OSError as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error creating configuration directories: {e}")

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
			print(f"[LliurexGuardManagerNatFreeClient]: Error creating directories: {e}")
			return

		self._check_dnsmasq_conf()

		try:
			self.first_init_path.touch(exist_ok=True)
		except OSError as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error creating init file: {e}")

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
			print(f"[LliurexGuardManagerNatFreeClient]: Error getting desktop DNS: {e}")

		return desktop_dns

	#def _get_desktop_dns 
	
	def _get_list_from_server(self, mode_to_set: str, list_to_config: list):

		if mode_to_set not in ("BlackMode", "WhiteMode"):
			return False

		update_dns = (mode_to_set == "WhiteMode")
		default_path = self.blacklist_dir if mode_to_set == "BlackMode" else self.whitelist_dir

		if default_path.exists():
			for file in default_path.iterdir():
				if file.is_file():
					try:
						file.unlink()
					except OSError as e:
						print(f"[LliurexGuardManagerNatFreeClient]: Warning, could not delete {file.name}: {e}")
		else:
			default_path.mkdir(parents=True, exist_ok=True)

		ctx = ssl._create_unverified_context() 

		try:
			for item in list_to_config:
				tmp_url = f"{self.server_download_url}{item}"
				tmp_path = default_path / item

				with urllib.request.urlopen(tmp_url, context=ctx, timeout=10) as response:
					with open(tmp_path, 'wb') as local_file:
						local_file.write(response.read())

			if not update_dns:
				return True

			if mode_to_set=="WhiteMode" and self.default_white_list_path.exists():
				shutil.copy2(self.default_white_list_path,default_path)

			dns_res = self.update_whitelist_dns()
			return dns_res.get("status", False)

		except Exception as e:
			print(f"[LliurexGuardManagerNatFreeClient]: Error downloading list from server: {e}")
			return False

	#def _get_list_from_server

	def _manage_dnsmasq_service(self, enable_service: bool):

		action = "enable" if enable_service else "disable"

		if not enable_service:
			error_stop, data_stop = self._stop_dnsmasq_service()
			if error_stop:
				print(f"[LliurexGuardManagerNatFreeClient]: Error stopping Dnsmasq. Details: {data_stop}")
				return {'status': False, 'msg': "Error stopping Dnsmasq", 'data': data_stop}
		try:
			subprocess.run(
				['systemctl', action, 'dnsmasq.service'],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				check=True
			)

			self._manage_resolvconf(enable_service)
			msg = f"Dnsmasq {action} successfully"
			return {'status': True, 'msg': msg}
			
		except subprocess.CalledProcessError as e:
			error_msg = f"Error: Dnsmasq {action} failed"
			details = f"Error {e.returncode}: {e.stderr.strip()}"
			print(f"[LliurexGuardManagerNatFreeClient]: {error_msg}. Details: {details}")
			return {'status': False, 'msg': error_msg, 'data': details}
		except Exception as e:
			error_msg = f"Error: Dnsmasq {action} failed"
			print(f"[LliurexGuardManagerNatFreeClient]: {error_msg}. Details: {str(e)}")
			return {'status': False, 'msg': error_msg, 'data': str(e)}

	#def manage_dnsmasq_service

	def _stop_dnsmasq_service(self):

		error = False
		data = ""

		try:
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

		conf_file = Path("/etc/systemd/resolved.conf.d/lliurex-dnsmasq.conf")

		if active:
			if not conf_file.exists():
				subprocess.run(['systemctl', 'stop', 'systemd-resolved'], check=True)
				self.core.get_plugin('NetworkManager').systemd_resolv_conf()
				subprocess.run(['systemctl', 'restart', 'systemd-resolved'], check=True)
		else:
			if conf_file.exists():
				try:
					conf_file.unlink()
				except OSError:
					pass

				subprocess.run(['systemctl', 'restart', 'systemd-resolved'], check=True)

	#def _manage_resolvconf
