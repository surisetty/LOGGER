#!/usr/bin/env python

# Import necessary Libraries
import sys
import os
import time
import json
import csv
# import logging
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
		# logging.basicConfig(level=10,
  #                   format='%(levelname)s %(asctime)s %(threadName)s %(message)s',
  #                   filename='./project/Log_files/test.log',
  #                   filemode='a')

		# List to store modbus read addresses
		self.read_reg_addr = []
		# # number of registers to read
		# self.read_reg_count = []
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
		# logging.info("MODBUS Node Initialized...")
		# print("MODBUS Node Initialized...")

	#***********************************************************#
	#******    Function to Read the Input File    **************#
	#***********************************************************#
	def Read_input_file(self, file_path_list):
		for loop in range(len(file_path_list)):
			# Fetch the File name
			mod_file_name = os.path.basename(file_path_list[loop])
			# Fetch the file extension
			ext = os.path.splitext(mod_file_name)[1]
			if ext in (".addr"):
				# logging.info("Reading the input file with Addr Extension for file %s", mod_file_name)
				# print("Reading the input file with Addr Extension for file", mod_file_name)
				with open(file_path_list[loop]) as f:
					lines=f.readlines()
				x = lines[0].split(',')
				x[-1] = x[-1].strip()
				w = [int(i) for i in x]
				# w = [int(x) for x in next(lines[0])]
				# print ("w : ", w)
				# save the count of registers to read from the modbus device
				# x = lines[0].split(',')
				# x[-1] = x[-1].strip()

				self.slaves_addr.append(w)
				# save the addresses of registers to read from the modbus device
				self.read_reg_addr.append(lines[1].split(','))
			else:
				# logging.error("Error in Reading file, change extension to .addr")
				print("Error in Reading file, change extension to .addr")
	#***********************************************************#
	#******    Function to Create the Modbus Read File    ******#
	#***********************************************************#
	def Mod_Create_file(self, rjson):
		# read the Modbus data for the specified addresses
		read_value = self.Mod_Read(self.read_reg_addr, rjson)
		# convert the data read from modbus in a particular format
		value = self.Mod_File_Conversion(read_value, rjson)
		print ("read_value : ", value)

		# Increment the file counter, when file is sent
		self.mod_data_file_timestamp = time.strftime("%Y%m%d-%H%M%S")

		# create the file name
		self.mod_data_file = self.mod_data_file_path + rjson.mod_data_file_initial \
							+ self.mod_data_file_timestamp + self.mod_data_file_ext
		# write the data into the file
		with open(self.mod_data_file, 'w') as f: 
			f.write(value)
		# with open("New_files/test2.csv", append_write, newline='') as f: 
		# 	writer = csv.writer(f , delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		# 	for i in range(len(value)):
		# 		writer.writerow(value[i])
		# print ("done")
		# logging.info("Mode cycle completed. Data file created")

	#***********************************************************#
	#******    Function to Read the MODBUS data addr    ********#
	#***********************************************************#
	def Mod_Read(self, addr_list, rjson):
		# Create a Modbus Client with the foloowing details
		client= ModbusClient(method = "rtu", port=rjson.mod_port_addr,stopbits = 1,\
							 bytesize = 8, parity = 'N', baudrate= 9600, timeout= self.timeOut)
		# print("Trying to Connect to Modbus ...")
		# logging.info("Trying to Connect to Modbus ...")
		# create a list to store all the read addresses
		get_data = []
		# connect to Modbus Client
		connect = client.connect()
		# if connection successful
		if connect == True:
			# logging.info("Modbus Connection succesful")
			# print("Modbus Connection succesful")
			for loop in range(len(addr_list)):
				temp = []
				# read all register one by one
				for i in range(len(addr_list[loop])):
					# 0x07 is the slave device address
					result = client.read_holding_registers(int(addr_list[loop][i]),\
									 1, unit=int(self.slaves_addr[loop][0]))
					# append the register data in the list
					temp.append(result.registers[0])
				get_data.append(temp)
				# logging.info("Modbus Read completed for file : ", loop)
			# close the modbus client after data read
			client.close()
			# logging.info("Modbus Closed")
			return get_data
		# if connection failed
		else:
			result = []
			# logging.error("Modbus connection failed")
			# print ("Modbus connection failed")
			for loop in range(len(addr_list)):
				result.append("Error")
			return result

	#***********************************************************#
	#******    Function to put the data in csv format    *******#
	#***********************************************************#
	def Mod_File_Conversion(self, data,rjson):
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