#!/usr/bin/env python

# Import necessary Libraries
import pymodbus3
from pymodbus3.client.sync import ModbusSerialClient as ModbusClient
import json
import csv
import sys
import os
import time


#***********************************************************#
#********************    Modbus Class Node    **************#
#***********************************************************#

class MODBUS_node(object):
	#***********************************************************#
	#***************    Class Initialization    ****************#
	#***********************************************************#
	def __init__(self):
		self.count = 0 #debug
		self.read_reg_addr = []
		self.read_reg_count = 0
		self.file = "xxxxx"
		self.port_addr = "xxxxxxxx"
		self.modbus_fetch_time = 1
		self.device_addr = "0x07"
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
			self.read_reg_count = lines[0]
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
	#******    Function to Read the Credentials File    ********#
	#***********************************************************#
	def Mod_Create_file(self):
		read_value = self.Mod_Read(self.read_reg_addr)
		value = self.Mod_File_Conversion(read_value)
		if os.path.exists('./New_files/test1.csv') == True:
			append_write = 'a' # append if already exists
		else:
			append_write = 'w' # make a new file if not
		with open("New_files/test1.csv", append_write, newline='') as f: 
			writer = csv.writer(f , delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for i in range(len(value)):
				writer.writerow(value[i])
		print ("done")


	#***********************************************************#
	#******    Function to Read the Credentials File    ********#
	#***********************************************************#
	def Mod_Read(self, addr_list):
		client= ModbusClient(method = "rtu", port=self.port_addr,stopbits = 1,\
							 bytesize = 8, parity = 'N', baudrate= 9600)
		print("Modbus Connect")
		get_data = []
		connect = client.connect()
		if connect == True:
			print("Modbus Connection succesful")
			for i in range(len(addr_list)):
				result = client.read_holding_registers(int(addr_list[i]), 1, unit=0x07)
				get_data.append(result.registers[0])
			client.close()
			return get_data
		else:
			self.count = self.count + 1
			print ("Modbus connection failed")
			result = "Error"
			return result

	#***********************************************************#
	#******    Function to Read the Credentials File    ********#
	#***********************************************************#
	def Mod_File_Conversion(self, data):
		row = []
		row.append("ADDRMODBUS" + " " + self.device_addr)
		row.append("TypeMODBUS" + " " + self.file)
		str_addr = ', '.join(str(e) for e in self.read_reg_addr)
		row.append(str(len(data)) + " " + str_addr)
		str_data = ', '.join(str(e) for e in data)
		row.append(time.ctime(time.time()) + " " + str_data)
		return row