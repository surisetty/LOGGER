#!/usr/bin/env python

# Import necessary Libraries
from ftplib import FTP
import json
import sys
import os
import logging

linear_rtu = logging.getLogger('linear.rtu')

class RTU_READ(object):
	def __init__(self):
		self.rtu_file_active_status = False
		self.rtu_file_endian_mode = ""
		self.rtu_file_description = "" 
		self.rtu_device_address = 0
		self.rtu_retry_count = 0
		self.file_addresses = []
		self.address_length = []
		self.datatypes = []
		print("Reading the RTU file")
		linear_rtu.info("Reading the RTU file")
		

	def ReadRtuFile(self, filepath):
		# Fetch the File name
		file = os.path.basename(filepath)
		# Fetch the file extension
		ext = os.path.splitext(file)[1]
		# if file type is RTU
		if ext in (".rtu"):
			# Open and Load RTU File
			with open(filepath) as data_file:    
				data = json.load(data_file)

			self.rtu_file_active_status = data["active"]
			self.rtu_file_endian_mode = data["endian_type"]
			self.rtu_file_description = data["Description"]
			self.rtu_device_address = data["device_address"]
			self.rtu_retry_count = data["retry_count"]
			addresses = data["address"]
			all_addr_in_file = []
			length = []
			datatypes = []
			for i in range(len(addresses)):
				all_addr_in_file.append(data["address"][i]["addr"])
				length.append(data["address"][i]["length"])
				datatypes.append(data["address"][i]["data_type"])
			self.file_addresses = all_addr_in_file
			self.address_length = length
			self.datatypes = datatypes

		# if file type is not RTU
		else:
			linear_rtu.error("File not in RTU Format")
