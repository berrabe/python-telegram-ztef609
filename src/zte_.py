"""
This module is used for rebooting
router ZTE F609 via HTTP request / without Web GUI

in nutshell, to reboot router ZTE F609, we need get some cookie
and variabel, in order like

1 - Get login token -> this will always change every new session,
useful for login

2 - Get SID Cookie -> This cookie is for authentication,
if we don't have this, we can't do anything

3 - Get Seesion Token -> session to reboot the router

after all are met, then we can reboot the router

created by berrabe
"""

import logging
import re
import requests

logger = logging.getLogger(__name__)

class RouterZteF609():
	"""
	this class is used for Initialization, all about variables
	and method that will be used for rebooting router ZTE F609.
	"""

	def __init__(self, url, username, password):
		"""
		method init, for Initialization all variable needed for
		this module to work properly
		"""

		logger.info("Initialization For ZTEF690")
		logger.info("Router URL (%s)", url)
		logger.info("Router username - (%s)", username)
		logger.info("Router password - (%s)", password)

		self.url = url
		self.username = username
		self.password = password
		self.form_login_token = ""
		self.session_token = ""
		self.sid_cookie = ""
		self.path_reboot = "/getpage.gch?pid=1002&nextpage=manager_dev_conf_t.gch"
		self.headers = {
			"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
			"Content-Type" : "application/x-www-form-urlencoded",
			"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
			"Accept-Encoding" : "gzip, deflate",
			"Accept-Language" : "en-US,en;q=0.9"
		}
		self.proxy_dict = {
              "http"  : "http://127.0.0.1:8080",
            }


	def __request_post(self, url, data='', cookies='', proxies=''):
		"""
		placeholder method for request, so that other methods
		don't use their own requests, all mehotd will make a request
		by calling this method
		"""

		try:
			req_ = requests.post(url,
				data = data,
				cookies = cookies,
				headers = self.headers,
				proxies=proxies,
				allow_redirects=False)

			if req_.status_code == 200 or req_.status_code == 302:
				pass
			else:
				logger.info("ERROR __request_post return code (%s)", req_.status_code)
				return "error"

		except Exception:
			logger.exception('ERROR on __request_post')
			return "error"

		return req_



	def get_login_token(self):
		"""
		Method for getting login token, This always changes
		if we want to log in and don't have an active session / cookie
		"""

		logger.info("Get Login Token From Router")

		try:
			get_code = self.__request_post(self.url)

			if get_code != "error":
				loc = get_code.text.find('Frm_Logintoken").value')
				start = loc+25
				end = start+10
				parse = re.findall('"([^"]*)"', get_code.text[start:end])

				logger.info("Get Login Token SUCCESS (%s)", get_code.status_code)
				logger.info("Login Token = (%s)", parse[0])

				self.form_login_token = parse[0]

		except Exception:
			logger.exception('ERROR on Get Login Token')
			return "error"

		return "OK"


	def get_sid_cookie(self):
		"""
		Method for getting SID Cookie, used for authentication,
		if we have this cookie, we can do whatever we want
		because we are authorized users
		"""

		logger.info("Get SID Cookie Code From Router")

		try:

			data = {
				"frashnum" : "",
				"action" : "login",
				"Frm_Logintoken" : self.form_login_token,
				"Username" : self.username,
				"Password" : self.password
			}

			cookies = {
				"_TESTCOOKIESUPPORT": "1",
			}

			get_sid = self.__request_post(f"{self.url}",
				data = data,
				cookies = cookies)

			if get_sid != "error":

				logger.info("Get SID Cookie SUCCESS %s", get_sid.status_code)
				logger.info("SID Cookie = (%s)", get_sid.cookies.get_dict()['SID'])

				self.sid_cookie = get_sid.cookies['SID']

		except Exception:
			logger.exception('ERROR on Get SID Cookie')
			return "error"

		return "OK"


	def get_session_token(self):
		"""
		Method for getting session reboot, When we want to reboot,
		the web app will generate a random session
		to validate the reboot request
		"""

		logger.info("Get Session Token Code From Router")

		try:

			# data = {
			# 	"frashnum" : "",
			# 	"action" : "login",
			# 	"Frm_Logintoken" : self.form_login_token,
			# 	"Username" : self.username,
			# 	"Password" : self.password
			# }
			logger.info("Contacting (%s/%s)", self.url, self.path_reboot)

			cookies = {
				"_TESTCOOKIESUPPORT": "1",
				"SID" : self.sid_cookie
			}

			get_session_token = self.__request_post(f"{self.url}{self.path_reboot}",
				cookies = cookies)

			if get_session_token != "error":
				loc = get_session_token.text.find('var session_token = "')
				start = loc+0
				end = start+40
				parse = re.findall('"([^"]*)"', get_session_token.text[start:end])

				logger.info("Get Session Token SUCCESS %s", get_session_token.status_code)
				logger.info("Session Token = (%s)", parse[0])

				self.session_token = parse[0]

		except Exception:
			logger.exception('ERROR on Get Reboot Session Token')
			return "error"

		return "OK"


	def reboot(self):
		"""
		Method for rebooting the router, you must have
		an reboot session token and SID cookie to run this method
		in order to succeed
		"""

		if self.get_login_token() == 'error':
			return 'error'
		if self.get_sid_cookie() == 'error':
			return 'error'
		if self.get_session_token() == 'error':
			return 'error'

		logger.info("Rebooting Router ZTE-F690")

		try:

			data = {
				"IF_ACTION" : "devrestart",
				"IF_ERRORSTR" : "SUCC",
				"IF_ERRORPARAM" : "SUCC",
				"IF_ERRORTYPE" : "-1",
				"flag" : "1",
				"_SESSION_TOKEN" : self.session_token
			}

			cookies = {
				"_TESTCOOKIESUPPORT": "1",
				"SID" : self.sid_cookie
			}

			reboot = self.__request_post(f"{self.url}{self.path_reboot}",
				data = data,
				cookies = cookies)

			if reboot != "error":
				logger.info("Rebooting Router ZTE-F690 SUCCESS %s", reboot.status_code)

		except Exception:
			logger.exception('ERROR on REBOOT Router')
			return "error"

		return "SUCCESS"
