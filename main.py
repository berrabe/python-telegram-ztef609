"""
This is main file for this application
just run it with python3 main.py

Created By : berrabe
"""

import logging
from src import checker_, tele_


logging.basicConfig(
	level = logging.INFO,
	# filename='python-ztef609.log', filemode='a',
	format = '[ %(levelname)s ] [ %(name)s ] [ %(asctime)s ] => %(message)s',
	datefmt='%d-%b-%y %H:%M:%S'
	)

logger = logging.getLogger(__name__)



def main():
	"""
	All logic goes to this function
	for easy to read and debug
	"""

	# directly call staticmethod of class Checker w/ make instance
	ip_info = checker_.Checker.ip_info()
	status = checker_.Checker.ping_public_ip(ip_info['ip'])


	if status == 'UNREACHABLE':

		obj = tele_.TelegramBot(
			token_telegram = 'YOUR TELEGRAM BOT TOKEN',
			chat_id_telegram = 'YOUR TELEGRAM CHAT ID',
			router_ip_address = 'http://192.168.1.1',
			router_user = 'admin',
			router_password = 'Telkomdso123')

		obj.send_alert(ip_info['ip'])
		obj.start_updater()


if __name__ == '__main__':
	main()
