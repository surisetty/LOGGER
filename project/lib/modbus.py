#!/usr/bin/env python

# Import necessary Libraries
import sys
import os
import time
import json
import csv
import pymodbus3
from pymodbus3.client.sync import ModbusSerialClient as ModbusClient
from lib.json_read import Read_Config

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
		# Timeout for MODBUS Failure
		self.timeOut = 3
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
		print("MODBUS Node Initialized...")

	#***********************************************************#
	#******    Function to Read the Input File    **************#
	#***********************************************************#
	def Read_input_file(self, file_path):
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
	#******    Function to Create the Modbus Read File    ******#
	#***********************************************************#
	def Mod_Create_file(self, rjson):
		# read the Modbus data for the specified addresses
		read_value = self.Mod_Read(self.read_reg_addr, rjson)
		# convert the data read from modbus in a particular format
		value = self.Mod_File_Conversion(read_value, rjson)
		# create the file name
		self.mod_data_file = self.mod_data_file_path + rjson.mod_data_file_initial \
							+ self.mod_data_file_timestamp + self.mod_data_file_ext
		# check for the file existence
		if os.path.exists(self.mod_data_file) == True:
			# append if file already exists
			append_write = 'a' 
		else:
			# make a new file if not present
			append_write = 'w'
		# write the data into the file
		with open(self.mod_data_file, append_write) as f: 
			f.write(value)
		# with open("New_files/test2.csv", append_write, newline='') as f: 
		# 	writer = csv.writer(f , delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		# 	for i in range(len(value)):
		# 		writer.writerow(value[i])
		print ("done")

	#***********************************************************#
	#******    Function to Read the MODBUS data addr    ********#
	#***********************************************************#
	def Mod_Read(self, addr_list, rjson):
		# Create a Modbus Client with the foloowing details
		client= ModbusClient(method = "rtu", port=rjson.mod_port_addr,stopbits = 1,\
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
				result = client.read_holding_registers(int(addr_list[i]), 1, unit=0x01)
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
	def Mod_File_Conversion(self, data,rjson):
		row = ""
		row += "ADDRMODBUS" + ", " + rjson.mod_device_addr + "\n"
		row += "TypeMODBUS" + ", " + "hitachi" + "\n"
		str_addr = ', '.join(str(e) for e in self.read_reg_addr)
		row += str(len(data)) + ", " + str_addr + "\n"
		str_data = ', '.join(str(e) for e in data)
		row += time.ctime(time.time()) + "," + str_data + "\n"
		return row