"""
This module is used for handling
telegram notification

created by berrabe
"""

import os
import signal
import json
import time
import logging
import requests
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from . import zte_

logger = logging.getLogger(__name__)


class TelegramBot():
	"""
	Class to store where all magic happens
	"""

	def __init__(self, **kwargs):
		try:
			logger.info("Initialization For Telegram Bot")

			self.token_telegram = kwargs['token_telegram']
			self.chat_id_telegram = kwargs['chat_id_telegram']
			self.router_ip_address = kwargs['router_ip_address']
			self.router_user = kwargs['router_user']
			self.router_password = kwargs['router_password']

			logger.info("Your Bot Token Is %s", self.token_telegram)
			logger.info("Your Chat Id Is %s", self.chat_id_telegram)

			self.custom_keyboard = [['/Reboot', '/No'], ['/IPInfo']]
			self.choices_keyboard_markup = ReplyKeyboardMarkup(self.custom_keyboard)
			self.choices_keyboard_remove = ReplyKeyboardRemove()

			self.updater = Updater(self.token_telegram, use_context=True)
			self.dispather_telegram = self.updater.dispatcher

			self.dispather_telegram.add_handler(CommandHandler("Reboot", self.reboot))
			self.dispather_telegram.add_handler(CommandHandler("No", self.stop_updater))
			self.dispather_telegram.add_handler(CommandHandler("IPInfo", self.ipinfo))

		except Exception:
			logger.exception('ERROR on Initialization Telegram Bot')


	def start_updater(self):
		"""
		Method for starting updater and handler for new telegram message.
		must call by manual with object instance
		"""

		logger.info("Starting Telegram Bot Updater and Handler")

		try:
			self.updater.start_polling()
			self.updater.idle()

		except Exception:
			logger.exception('ERROR on Starting Telegram Updater and Handler')


	def stop_updater(self, update, context):
		"""
		Method for stopping updater and handler for telegram bot.
		must killed with signal because it is use python threading.
		auto triggered when you choice /NO on telegram keyboard.
		"""

		try:
			pid = os.getpid()

			logger.info("/NO Triggered, Stopping Telegram Handler and Send SIGKILL Signal to PID %s", pid)

			context.bot.sendMessage(
				chat_id=self.chat_id_telegram,
				text=f"<code>OK, Stopping App On PID {pid}</code>",
				parse_mode=ParseMode.HTML,
				reply_markup=self.choices_keyboard_remove)

			os.kill(pid, signal.SIGKILL)

		except Exception:
			logger.exception('ERROR on Stopping Telegram Handler')



	def send_alert(self, ip_public):
		"""
		Method for send alert to your chat id when your ip public is changed.
		this method call by manual with object instance.
		this message also send you custom keyboard with 3 custom command.
		so you dont have type command.
		"""

		logger.info("Sending Telegram Alert")

		try:
			self.updater.bot.send_message(
				chat_id=self.chat_id_telegram,
				text=f"`Your public ip [ {ip_public} ] cannot be accessed, do you want rebooting ZTE F609 ?`",
				reply_markup=self.choices_keyboard_markup,
				parse_mode=ParseMode.MARKDOWN_V2 )

		except Exception:
			logger.exception('ERROR on Send Telegram Alert')



	def reboot(self, update, context):
		"""
		Method for rebooting Router ZTE F609.
		this method NEED Module zte_.py.
		this method is auto triggered
		when choose /Reboot on telegram bot custom keyboard
		"""

		logger.info("/Reboot Triggered, Rebooting Router ZTE F609")

		try:
			context.bot.sendMessage(
				chat_id=self.chat_id_telegram,
				text="<code>Rebooting Router ZTE F609</code>",
				parse_mode=ParseMode.HTML,
				reply_markup=self.choices_keyboard_remove)

			router = zte_.RouterZteF609(self.router_ip_address, self.router_user, self.router_password)

			if router.reboot() == 'SUCCESS':
				logger.info("Rebooting Router ZTE F609 Completed Successfully, Waiting 120 Seconds")

				time.sleep(120)
				context.bot.sendMessage(
					chat_id=self.chat_id_telegram,
					text="`Rebooting Router ZTE F609 Completed Successfully, Do You Want Reboot Again ?`",
					parse_mode=ParseMode.MARKDOWN_V2,
					reply_markup=self.choices_keyboard_markup)

			else:
				logger.info("ERROR Rebooting Router ZTE F609")
				context.bot.sendMessage(
					chat_id=self.chat_id_telegram,
					text="`ERROR Rebooting Router ZTE F609`",
					parse_mode=ParseMode.MARKDOWN_V2,
					reply_markup=self.choices_keyboard_remove)

		except Exception:
			logger.exception('ERROR on Rebooting Router ZTE F609')



	def ipinfo(self, update, context):
		"""
		Method for checking ip public information for your network.
		this method use API from https://ipinfo.io.
		and this method is auto triggered
		when you choose /IPInfo on telegram bot custom keyboard
		"""

		logger.info("/IPInfo Triggered, Send IP Information")

		try:
			req_ = requests.get("https://ipinfo.io")

			if req_.status_code == 200:

				ip_info = req_.json()
				ip_public = req_.json()['ip']

				logger.info("Get Public IP Success (%s) - %s", req_.status_code, ip_public)

				context.bot.sendMessage(
					chat_id=self.chat_id_telegram,
					text=f"<code>{json.dumps(ip_info, indent=4, sort_keys=True)}</code>",
					parse_mode=ParseMode.HTML,
					reply_markup=self.choices_keyboard_remove)

		except Exception:
			logger.exception('ERROR on IP Information')
