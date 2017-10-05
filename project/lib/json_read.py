#!/usr/bin/env python

# Import necessary Libraries
from ftplib import FTP
import json
import sys
import os
import logging

#***********************************************************#
#********************    FTP Class Node    *****************#
#***********************************************************#

class Read_Config(object):
	#***********************************************************#
	#***************    Class Initialization    ****************#
	#***********************************************************#
	def __init__(self):
		# FTP User ID
		self.ftp_user_id = "Anonymous"
		# FTP password
		self.ftp_password = "Anonymous"
		# FTP host_name
		self.ftp_ip_addr = "xx.xx.xx.xx"
		# FTP port number
		self.ftp_port_num = 21
		# FTP desination path
		self.ftp_path = ""
		# FTP send interval
		self.ftp_server_upload_time = 100
		# com port address for modbus
		self.mod_port_addr = "xxxxxxxx"
		# Interval between two modbus read
		self.mod_fetch_time = 1
		# # slave device address
		# self.mod_device_addr = "01"
		# Output file name
		self.mod_data_file_initial = 'xxxx'
		#Modbus input file
		self.mod_input_file = []
		# Total number of serial ports
		self.serial_port_count = 0
		# read logging Level
		self.logging_level = 10
		
		logging.basicConfig(level=self.logging_level,
                    format='%(levelname)s %(asctime)s %(threadName)s %(message)s',
                    filename='./project/Log_files/test.log',
                    filemode='a')

	#***********************************************************#
	#******    Function to Read the Credentials File    ********#
	#***********************************************************#
	def Read_JSON(self, cred_file_path):
		# Fetch the File name
		cred_file = os.path.basename(cred_file_path)
		# Fetch the file extension
		ext = os.path.splitext(cred_file)[1]
		# if file type is JSON
		if ext in (".json"):
			logging.info("ReadingCredentials")
			# print ("ReadingCredentials")
			# Open and Load JSON File
			with open(cred_file_path) as data_file:    
				data = json.load(data_file)

			# Fetch FTP details
			self.ftp_user_id = data["ftp"]["name"]
			self.ftp_password = data["ftp"]["password"]
			self.ftp_ip_addr = data["ftp"]["server"]
			self.ftp_port_num = data["ftp"]["port"]
			self.ftp_path = data["ftp"]["path"]
			self.ftp_server_upload_time = data["Ftp_interval"]

			# Fetch Modbus details
			self.mod_port_addr = data["serial"]["COM0"]["device"]
			self.mod_fetch_time = data["Modbus_interval"]
			self.mod_data_file_initial = data["Output_Filename"]
			total_files = len(data["serial"]["COM0"]["Device_files"])
			for loop in range(total_files):
				self.mod_input_file.append(data["serial"]["COM0"]["Device_files"][loop])

			# Fetch number of Modbus devices attached to the controller
			self.serial_port_count = 1
			# Reading the logging level
			self.logging_level = data["Logging_Level"]

		# if file type is not JSON
		else:
			logging.error("File not in JSON Format")
			# print ("File not in JSON Format")