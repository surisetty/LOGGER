#!/usr/bin/env python

# Import necessary Libraries
import sys
import os
import time
import json
import csv
import minimalmodbus 
import serial
import logging
from lib.rtu_read import RTU_READ

minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

linear_modbus = logging.getLogger('linear_logger.modbus')

class ModbusNode(object):
	def __init__(self):
		# List to store modbus read addresses
		self.read_all_addr = []
		# File containing the modbus responses of the read addresses 
		self.mod_data_file = ""
		# File location and name containing the modbus responses of the read addresses 
		self.mod_data_file_path = sys.path[0] + "/Data/"
		# File extension of the file containing the modbus responses of the read addresses 
		self.mod_data_file_ext = '.csv'
		#create file name initial
		timestr = time.strftime("%Y%m%d-%H%M%S")
		# File number counter
		self.mod_data_file_timestamp = timestr
		# log data
		linear_modbus.info("MODBUS Node Initialized...")
		# call RTU_READ node


	def getAllFilesonActivePorts(self, ports):
		read_all_files = []
		for loop in range(len(ports)):
			slaves_on_port = []
			for i in range(len(ports[loop])):
				slaves_on_port.append(ports[loop][i])
			read_all_files.append(slaves_on_port)
		return read_all_files

	def ReadInputFilesPortwise(self, file_path_string, files_list):
		address = []
		length = []
		datatype = []
		endianness = []
		RTU = RTU_READ()
		for loop in range(len(files_list)):
			filename = file_path_string + files_list[loop]
			RTU.ReadRtuFile(filename)
			if RTU.rtu_file_active_status == "True":
				address.append(RTU.file_addresses)
				length.append(RTU.address_length)
				datatype.append(RTU.datatypes)
				endianness.append(RTU.rtu_file_endian_mode)
		return (address, length, datatype, endianness)


	def ReadInputFile(self, ports):
		all_addresses = []
		all_length = []
		all_datatype = []
		all_endianness = []
		# List to store all the files attached on all active ports
		read_all_files = self.getAllFilesonActivePorts(ports)
		file_path_string = sys.path[0] + "/config/"
		for loop in range(len(read_all_files)):
			(address, length, datatype, endianness) = self.ReadInputFilesPortwise(file_path_string, read_all_files[loop])
			all_addresses.append(address)
			all_length.append(length)
			all_datatype.append(datatype)
			all_endianness.append(endianness)
		print(all_datatype)
		print(all_addresses)
		print(all_endianness)
		print(all_length)
			