#!/usr/bin/env python

# Import necessary Libraries
from ftplib import FTP
import json
import sys
import os
import logging

linear_json = logging.getLogger('linear.json')

class ReadConfig(object):
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
		self.ftp_path = "/ftptest"
		# FTP send interval
		self.ftp_server_upload_time = 10

		# Interval between two modbus read
		self.mod_fetch_time = 1
		# Output file name
		self.mod_data_file_initial = 'xxxx'

		# com port address for modbus
		self.mod_port_addr = []
		#Modbus number of slaves attached
		self.mod_slaves = []
		# modbus parameters
		self.mod_baudrate = []
		self.mod_parity = []
		self.mod_databits = []
		self.mod_stopbits = []
		self.mod_poll_timeout = []
		# Serial port activeness status
		self.serial_port_status = []
		# Total number of serial ports
		self.serial_port_count = 0

	def ReadJson(self, cred_file_path):
		# Fetch the File name
		cred_file = os.path.basename(cred_file_path)
		# Fetch the file extension
		ext = os.path.splitext(cred_file)[1]
		# if file type is JSON
		if ext in (".json"):
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

			# Fetch number of Modbus devices attached to the controller
			self.serial_port_count = len(data["serial"])

			# Fetch Modbus details
			self.mod_fetch_time = data["Modbus_interval"]
			self.mod_data_file_initial = data["Output_Filename"]
			for loop in range(self.serial_port_count):
				self.mod_port_addr.append(data["serial"][loop]["device"])
				self.mod_baudrate.append(data["serial"][loop]["baudrate"])
				self.mod_parity.append(data["serial"][loop]["parity"])
				self.mod_databits.append(data["serial"][loop]["databits"])
				self.mod_stopbits.append(data["serial"][loop]["stopbits"])
				self.mod_poll_timeout.append(data["serial"][loop]["timeout"])
				self.serial_port_status.append(data["serial"][loop]["status"])
				self.mod_slaves.append(data["serial"][loop]["slaves"])
		# if file type is not JSON
		else:
			linear_json.error("File not in JSON Format")
