#!/usr/bin/env python

# Import necessary Libraries
import sys
import os
import time
import json
import csv
import logging
import pymodbus3
from pymodbus3 import exceptions 
from pymodbus3.client.sync import ModbusSerialClient as ModbusClient

mylogger_modbus = logging.getLogger('mylogger.modbus')

#***********************************************************#
#********************    Modbus Class Node    **************#
#***********************************************************#
class ModbusNode(object):
	#***********************************************************#
	#***************    Class Initialization    ****************#
	#***********************************************************#
	def __init__(self):
		# List to store modbus read addresses
		self.read_reg_addr = []
		# Timeout for MODBUS Failure
		self.timeOut = 3
		# File containing the modbus responses of the read addresses 
		self.mod_data_file = ""
		# File location and name containing the modbus responses of the read addresses 
		self.mod_data_file_path = sys.path[0] + "/Data/"
		# File extension of the file containing the modbus responses of the read addresses 
		self.mod_data_file_ext = '.csv'
		# Slaves addresses 
		self.slaves_addr = []
		#create file name initial
		timestr = time.strftime("%Y%m%d-%H%M%S")
		# File number counter
		self.mod_data_file_timestamp = timestr

		mylogger_modbus.info("MODBUS Node Initialized...")

	#***********************************************************#
	#******    Function to Read the Input File    **************#
	#***********************************************************#
	def ReadInputFile(self, file_path_list):
		for loop in range(len(file_path_list)):
			# Fetch the File name
			mod_file_name = os.path.basename(file_path_list[loop])
			# Fetch the file extension
			ext = os.path.splitext(mod_file_name)[1]
			if ext in (".addr"):
				mylogger_modbus.info("Reading the input file with Addr Extension for file %s", mod_file_name)
				with open(file_path_list[loop]) as f:
					lines=f.readlines()
				x = lines[0].split(',')
				x[-1] = x[-1].strip()
				w = [int(i) for i in x]

				self.slaves_addr.append(w)
				# save the addresses of registers to read from the modbus device
				self.read_reg_addr.append(lines[1].split(','))
			else:
				mylogger_modbus.error("Error in Reading file, change extension to .addr")

	#***********************************************************#
	#******    Function to Create the Modbus Read File    ******#
	#***********************************************************#
	def ModCreateFile(self, rjson):
		# read the Modbus data for the specified addresses
		read_value = self.ModRead(self.read_reg_addr, rjson)
		# convert the data read from modbus in a particular format
		value = self.ModFileConversion(read_value, rjson)
		# Increment the file counter, when file is sent
		self.mod_data_file_timestamp = time.strftime("%Y%m%d-%H%M%S")

		# create the file name
		self.mod_data_file = self.mod_data_file_path + rjson.mod_data_file_initial \
							+ self.mod_data_file_timestamp + self.mod_data_file_ext
		# write the data into the file
		with open(self.mod_data_file, 'w') as f: 
			f.write(value)

	#***********************************************************#
	#******    Function to Read the MODBUS data addr    ********#
	#***********************************************************#
	def ModRead(self, addr_list, rjson):
		# Create a Modbus Client with the following details
		client= ModbusClient(method = "rtu", port=rjson.mod_port_addr,stopbits = 1,\
							 bytesize = 8, parity = 'N', baudrate= 9600, timeout= self.timeOut)
		mylogger_modbus.info("Trying to Connect to Modbus ...")
		# create a list to store all the read addresses
		get_data = []
		# connect to Modbus Client
		connect = client.connect()
		# if connection successful
		if connect == True:
			mylogger_modbus.info("Modbus Connection succesful")
			for loop in range(len(addr_list)):
				temp = []
				# read all register one by one
				for i in range(len(addr_list[loop])):
					try:
						conv_addr = int(addr_list[loop][i], 16)
						# collect data byte by byte
						result = client.read_holding_registers(conv_addr,\
									 1, unit=int(self.slaves_addr[loop][0]))
						# append the register data in the list
						temp.append(result.registers[0])
					# Handle all kinds of existing errors while making the connection
					except pymodbus3.exceptions.ModbusIOException as e:
						result = "error"
						mylogger_modbus.error("Device not connected, Check Cable Connection : ({0})"\
										.format(e))
			
				get_data.append(temp)
				mylogger_modbus.info("Modbus Read completed for file : %s", str(loop))
			# close the modbus client after data read
			client.close()
			mylogger_modbus.info("Modbus Closed")
			return get_data
		# if connection failed
		else:
			result = []
			mylogger_modbus.error("Modbus connection failed")
			for loop in range(len(addr_list)):
				result.append("Error")
			return result

	#***********************************************************#
	#******    Function to put the data in csv format    *******#
	#***********************************************************#
	def ModFileConversion(self, data,rjson):
		row = ""
		for loop in range(len(data)):
			row += "ADDRMODBUS" + ", " + str(self.slaves_addr[loop][0]) + "\n"
			row += "TypeMODBUS" + ", " + rjson.mod_input_file[loop] + "\n"
			str_addr = ', '.join(str(e) for e in self.read_reg_addr[loop])
			row += str(len(data[loop])) + ", " + str_addr + "\n"
			str_data = ', '.join(str(e) for e in data[loop])
			row += time.ctime(time.time()) + "," + str_data + "\n" 

			row += "\n"
		return row