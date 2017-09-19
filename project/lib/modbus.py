#!/usr/bin/env python

# Import necessary Libraries
import sys
import os
import time
import json
import csv
import pymodbus3
from pymodbus3.client.sync import ModbusSerialClient as ModbusClient

#***********************************************************#
#********************    Modbus Class Node    **************#
#***********************************************************#
class MODBUS_node(object):
	#***********************************************************#
	#***************    Class Initialization    ****************#
	#***********************************************************#
	def __init__(self):
		# List to store modbus read addresses
		self.read_reg_addr = []
		# number of registers to read
		self.read_reg_count = 0
		# input file to modbus, containing addresses to read
		self.file = "xxxxx"
		# com port address for modbus
		self.port_addr = "xxxxxxxx"
		# Timeout for MODBUS Failure
		self.timeOut = 3
		# Interval between two modbus read
		self.modbus_fetch_time = 1
		# slave device address
		self.device_addr = "0x07"
		# File containing the modbus responses of the read addresses 
		self.mod_created_file_name = ''
		# File location and name containing the modbus responses of the read addresses 
		self.mod_data_file = 'New_files/file'
		# File extension of the file containing the modbus responses of the read addresses 
		self.mod_data_file_ext = '.csv'
		# File number counter
		self.mod_file_counter = 0
		print("MODBUS Node Initialized...")

	#***********************************************************#
	#******    Function to Read the Input File    **************#
	#***********************************************************#
	def Read_ADDR_Input_file(self, file_path):
		# Fetch the File name
		mod_file_name = os.path.basename(file_path)
		# Fetch the file extension
		ext = os.path.splitext(mod_file_name)[1]
		if ext in (".addr"):
			print("Reading the input file with Addr Extension")
			with open(file_path) as f:
				lines=f.readlines()
			# save the count of registers to read from the modbus device
			self.read_reg_count = lines[0]
			# save the addresses of registers to read from the modbus device
			self.read_reg_addr = lines[1].split(',')
		else:
			print("Error in Reading file, change extension to .addr")

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
			print ("Reading MODBUS Credentials")
			# Open and Load JSON File
			with open(cred_file_path) as data_file:    
				data = json.load(data_file)

			# Fetch all the credentials
			self.port_addr = data["serial"]["COM0"]["device"]
			self.file = data["serial"]["COM0"]["Device_files"][0]
			self.modbus_fetch_time = data["Modbus_interval"]
		# if file type is not JSON
		else:
			print ("File not in JSON Format")

	#***********************************************************#
	#******    Function to Create the Modbus Read File    ******#
	#***********************************************************#
	def Mod_Create_file(self):
		# read the Modbus data for the specified addresses
		read_value = self.Mod_Read(self.read_reg_addr)
		# convert the data read from modbus in a particular format
		value = self.Mod_File_Conversion(read_value)
		# create the file name
		self.mod_created_file_name = self.mod_data_file + str(self.mod_file_counter) \
									+ self.mod_data_file_ext
		# check for the file existence
		if os.path.exists(self.mod_created_file_name) == True:
			# append if file already exists
			append_write = 'a' 
		else:
			# make a new file if not present
			append_write = 'w'
		# write the data into the file
		with open(self.mod_created_file_name, append_write) as f: 
			f.write(value)
		# with open("New_files/test2.csv", append_write, newline='') as f: 
		# 	writer = csv.writer(f , delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		# 	for i in range(len(value)):
		# 		writer.writerow(value[i])
		print ("done")


	#***********************************************************#
	#******    Function to Read the MODBUS data addr    ********#
	#***********************************************************#
	def Mod_Read(self, addr_list):
		# Create a Modbus Client with the foloowing details
		client= ModbusClient(method = "rtu", port=self.port_addr,stopbits = 1,\
							 bytesize = 8, parity = 'N', baudrate= 9600, timeout= self.timeOut)
		print("Trying to Connect to Modbus ...")
		# create a list to store all the read addresses
		get_data = []
		# connect to Modbus Client
		connect = client.connect()
		# if connection successful
		if connect == True:
			print("Modbus Connection succesful")
			# read all register one by one
			for i in range(len(addr_list)):
				# 0x07 is the slave device address
				result = client.read_holding_registers(int(addr_list[i]), 1, unit=0x07)
				# append the register data in the list
				get_data.append(result.registers[0])
			# close the modbus client after data read
			client.close()
			return get_data
		# if connection failed
		else:
			print ("Modbus connection failed")
			result = "Error"
			return result

	#***********************************************************#
	#******    Function to put the data in csv format    *******#
	#***********************************************************#
	def Mod_File_Conversion(self, data):
		row = ""
		row += "ADDRMODBUS" + ", " + self.device_addr + "\n"
		row += "TypeMODBUS" + ", " + self.file + "\n"
		str_addr = ', '.join(str(e) for e in self.read_reg_addr)
		row += str(len(data)) + ", " + str_addr + "\n"
		str_data = ', '.join(str(e) for e in data)
		row += time.ctime(time.time()) + "," + str_data + "\n"
		# row = []
		# row.append("ADDRMODBUS" + " " + self.device_addr)
		# row.append("TypeMODBUS" + " " + self.file)
		# str_addr = ', '.join(str(e) for e in self.read_reg_addr)
		# row.append(str(len(data)) + " " + str_addr)
		# str_data = ', '.join(str(e) for e in data)
		# row.append(time.ctime(time.time()) + " " + str_data)
		return row