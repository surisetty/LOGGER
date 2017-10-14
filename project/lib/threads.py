#!/usr/bin/python

import os
import time
import sys
from lib.json_read import Read_Config
from lib.ftpServer import FTP_node
from lib.modbus import MODBUS_node

# exit flag for thread exit, initialized to 0
exitFlag = 0



class Threads(object):
	
	def __init__(self):
		# Get the credential file as an input
		self.cred_file = sys.path[0] + "/config/config.json"

	def mod_read(threadName, delay, rjson):
		# continue reading the data until exit flag is set high
		while 1:
			if exitFlag:
				# exit the thread when exit flag is set
				threadName.exit()
			# sleep for the required time 
			time.sleep(delay)
			# Read the required Addresses
			Modbus.Mod_Create_file(rjson)
			
	
	def send_file(threadName, delay):
		while 1:
			cred = Ftp.FTP_connect(RJSON.ftp_user_id, RJSON.ftp_password, RJSON.ftp_ip_addr,\
										 RJSON.ftp_port_num, RJSON.ftp_path)
			# continue reading the data until exit flag is set high
			if exitFlag:
				# exit the thread when exit flag is set
				threadName.exit()
			# sleep for the required time
			time.sleep(delay)
			# Upload the required file
			test = Ftp.FTP_upload(cred, Modbus.mod_data_file)
			# FTP connection close
			Ftp.FTP_Close()
			# remove the uploaded file when sent
			os.remove(Modbus.mod_data_file)
			# create file name
			timestr = time.strftime("%Y%m%d-%H%M%S")
			# Increment the file counter, when file is sent
			Modbus.mod_data_file_timestamp = timestr




