

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
from ctypes import *
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

linear_modbus = logging.getLogger('linear_logger.modbus')

class ModbusNode(object):
	def __init__(self):
		# List to store modbus read addresses
		self.read_reg_addr = []
		# Timeout for MODBUS Failure
		self.timeOut =3
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
		self.set_float = 0
		linear_modbus.info("MODBUS Node Initialized...")

	def float_conv(self, num):
		regStr = chr(num[1]>>8) + chr(num[1]&0x00FF) + chr(num[0]>>8) + chr(num[0]&0x00FF)
		val = minimalmodbus._bytestringToFloat(regStr)	
		#print("float value: ",round(val, 3))
		return round(val, 3)
		# i = int(hex_num, 16)                   # convert from hex to a Python int
		# cp = pointer(c_int(i))           # make this into a c integer
		# fp = cast(cp, POINTER(c_float))  # cast the int pointer to a float pointer
		# return fp.contents.value

	def ReadInputFile(self, file_path_list):
		for loop in range(len(file_path_list)):
			# Fetch the File name
			mod_file_name = os.path.basename(file_path_list[loop])

			# Fetch the file extension
			ext = os.path.splitext(mod_file_name)[1]
			# print("file_name", mod_file_name)
			if ext in (".addr"):
				linear_modbus.info("Reading the input file with Addr Extension for file %s", mod_file_name)
				with open(file_path_list[loop]) as f:
					lines=f.readlines()
				x = lines[0].split(',')
				x[-1] = x[-1].strip()
				w = [int(i) for i in x]
				self.slaves_addr.append(w)
				# save the addresses of registers to read from the modbus device
				m = []
				for line_count in range(1,len(lines)):
					lines[line_count] = lines[line_count].rstrip('\r\n')
					l = lines[line_count].split(',')
					if (len(l) > 2):
						del l[-1]
					l = list(map(int, l))
					m.append(l)

					# l = lines[line_count].split(',')
					# l[-1] = l[-1].strip()
					# print (l)
					# m = []
					# for l_count in range(len(l)):
					# 	m.append([int(i) for i in l[l_count]])
					# self.read_reg_addr.append(m)
				self.read_reg_addr.append(m)
			else:
				linear_modbus.error("Error in Reading file, change extension to .addr")
	
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

	def ModRead(self, addr_list, rjson):

		# Create a Modbus Client with the following details
		#client= ModbusClient(method = "rtu", port=rjson.mod_port_addr,stopbits = 1,\
		#					 bytesize = 8, parity = 'N', baudrate= 9600, timeout= self.timeOut)
		instrument = minimalmodbus.Instrument('/dev/ttyUSB0',1)
		instrument.serial.baudrate= 9600
		instrument.serial.bytesize = 8
		instrument.serial.parity = 'N'
		instrument.serial.stopbits = 1
		instrument.serial.timeout = self.timeOut
		#print("mod read started")
		linear_modbus.info("Trying to Connect to Modbus ...")
		# create a list to store all the read addresses
		get_data = []
		# connect to Modbus Client
		#connect = client.connect()
		# print (client.Decode)
		# if connection successful
		connect = True
		if connect == True:
			linear_modbus.info("Modbus Connection succesful")
			for loop in range(len(addr_list)):
				temp = []
				for i in range(len(addr_list[loop])):
					# read all register one by one
					try:
						# conv_addr = int(addr_list[loop][i], 16)
						# collect data byte by byte
						#result = client.read_holding_registers(int(addr_list[loop][i][0]),\
						#			 int(addr_list[loop][i][1]), unit=int(self.slaves_addr[loop][0]))
						instrument = minimalmodbus.Instrument('/dev/ttyUSB0',int(self.slaves_addr[loop][0]))
						result = instrument.read_registers(int(addr_list[loop][i][0]),int(addr_list[loop][i][1]),3) 
						# append the register data in the list
						temp.append(result)
						#temp.append(result.registers)
						# print("Raw Data:",result)
						time.sleep(.30)
					except ValueError as e:
						linear_modbus.error("Value Error : ({0})".format(e))
					except TypeError as e:
						linear_modbus.error("Type Error : ({0})".format(e))
					except IOError as e:
						linear_modbus.error("IO Error : ({0})".format(e))
				get_data.append(temp)
				linear_modbus.info("Modbus Read completed for file : %s", str(loop))
			# close the modbus client after data read
			#client.close()
			linear_modbus.info("Modbus Closed")
			#print(get_data)
			return get_data
		# if connection failed
		else:
			result = []
			linear_modbus.error("Modbus connection failed")
			for loop in range(len(addr_list)):
				result.append("Error")
			return result
		

	def ModFileConversion(self, data,rjson):
		row = ""
		for loop in range(len(data)):
			if rjson.mod_input_file[loop] == "MFM.addr":
				self.set_float = 1
			
			#add 1st line in output file	
			row += "ADDRMODBUS" + ";" + str(self.slaves_addr[loop][0]) + "\n"
			# add 2nd line in output file
			row += "TypeMODBUS" + ";" + rjson.mod_input_file[loop] + "\n"
			# adding 3rd linw in output  file
			temp_addr = []
			temp_count = []
			
			for i in range(len(self.read_reg_addr[loop])):
				temp_addr.append(i+1)
				# temp_addr.append(self.read_reg_addr[loop][i][0])
				temp_count.append(self.read_reg_addr[loop][i][1])
			count = 0
			for i in range(len(temp_count)):
				count = count + int(temp_count[i])	
			str_addr = ';'.join(str(e) for e in temp_addr)

			# change the below line for counts value as we did yesterday, (check the rasp code)
			row += str(len(temp_count)) + ";" + str_addr + "\n"
			

			#adding 4rth line in output file
			
			temp_data = []
			for i in range(len(data[loop])):
				val = ""
				if (data[loop]) == "Error":
					val = "Error"
					temp_data.append(val)
				else:
					if temp_count[i] == 2:
						if len(data[loop][i]) == 1:
							b = '{0:x}'.format(int(data[loop][i][0]))
							val = b
							#print("error_handled")
						else:
							a = '{0:x}'.format(int(data[loop][i][1]))
							b = '{0:x}'.format(int(data[loop][i][0]))
							# val = str(data[loop][i][1]) + str(data[loop][i][0])
							val = a + b
							#print(val)
					else:
						val = '{0:x}'.format(int(data[loop][i][0]))#str(hex(data[loop][i][0]))

					# change this code for doing changes in the float file output

					if self.set_float == 1:
						# print("float value: ",self.float_conv(val))
						#time.sleep(.1)
						temp_data.append(self.float_conv(data[loop][i]))
						# temp_data.append(val)
					else:
						temp_data.append(int(val,16))

			str_data = ';'.join(str(e) for e in temp_data)
			row += time.strftime("%d/%m/%Y-%H:%M:%S", time.localtime()) + ";" + str_data + "\n" 
			self.set_float = 0
		return row
