"""
This Module Is Used For
Checking Public IP and
Ping It

created by berrabe
"""


import subprocess
import logging
import requests

logger = logging.getLogger(__name__)

class Checker():
	"""
	Class For Checking Your Current Public IP,
	And Then Test With Ping It

	created by berrabe
	"""

	@staticmethod
	def ip_info():
		"""
		This Method is used for checking Your IP Public
		With API From https://ipinfo.io
		"""

		logger.info("Checking IP Information")

		try:
			req_ = requests.get("https://ipinfo.io")

			if req_.status_code == 200:
				ip_info = req_.json()

				logger.info("Checking IP Information Success %s", req_.status_code)

				# print(f"""
				# 	\r[+] Public IP => {ip_info['ip']}
				# 	\r[+] City => {ip_info['city']}
				# 	\r[+] Region => {ip_info['region']}
				# 	\r[+] Country => {ip_info['country']}
				# 	\r[+] Loc => {ip_info['loc']}
				# 	\r[+] Org => {ip_info['org']}
				# 	\r[+] Timezone => {ip_info['timezone']}
				# 	""")
			return ip_info

		except Exception:
			logger.exception('ERROR on Checking IP Information')


	@staticmethod
	def ping_public_ip(ip_public):
		"""
		This method is used to check public ip with ping
		command ping from OS with library subprocess
		"""

		logger.info("Ping-ing Public IP - %s", ip_public)

		try:
			proc = subprocess.Popen(f"ping -c 10 {ip_public}",
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				shell=True,
				universal_newlines=True)

			# std_out, std_err = proc.communicate()
			proc.communicate()

			if proc.returncode == 0:
				logger.info("Public IP Connected - REACHABLE (%s) - %s",proc.returncode , ip_public)
				# print(f"\n[+] Public IP Connected - NORMAL => {ip_public}\n")
			else:
				logger.info("Public IP Cannot Be Connected - UNREACHABLE (%s) - %s", proc.returncode, ip_public)
				# print(f"\n[-] Public IP Cannot Be Connected - ERROR => {ip_public}\n")
				return 'UNREACHABLE'

			return 'REACHABLE'

		except Exception:
			logger.exception('ERROR on Ping Public IP')
