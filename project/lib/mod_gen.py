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

linear_modbus = logging.getLogger('linear.modbus')

class ModbusNode(object):
	def __init__(self):
		self.cons_read_reg_timeout = 0.3
		# List to store modbus read addresses
		self.all_addresses = []
		self.all_length = []
		self.all_datatype = []
		self.all_endianness = []
		self.all_device_address = []
		self.all_retry_counts = []
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
		device_address = []
		retry_counts = []
		RTU = RTU_READ()
		for loop in range(len(files_list)):
			filename = file_path_string + files_list[loop]
			RTU.ReadRtuFile(filename)
			if RTU.rtu_file_active_status == "True":
				address.append(RTU.file_addresses)
				length.append(RTU.address_length)
				datatype.append(RTU.datatypes)
				endianness.append(RTU.rtu_file_endian_mode)
				device_address.append((RTU.rtu_device_address))
				retry_counts.append((RTU.rtu_retry_count))
		return (address, length, datatype, endianness, device_address, retry_counts)


	def ReadInputFile(self, ports):
		# List to store all the files attached on all active ports
		read_all_files = self.getAllFilesonActivePorts(ports)
		file_path_string = sys.path[0] + "/config/"
		for loop in range(len(read_all_files)):
			(address, length, datatype, endianness, device_address, retry_counts) = \
										self.ReadInputFilesPortwise(file_path_string, read_all_files[loop])
			self.all_addresses.append(address)
			self.all_length.append(length)
			self.all_datatype.append(datatype)
			self.all_endianness.append(endianness)
			self.all_device_address.append(device_address)
			self.all_retry_counts.append(retry_counts)

	def init_modbus(self, port_addr, device_addr, baudrate, bytesize, parity, stopbits, timeout):
		try:
			instrument = minimalmodbus.Instrument(port_addr, device_addr)
			instrument.serial.baudrate= baudrate
			instrument.serial.bytesize = bytesize
			instrument.serial.parity = parity
			instrument.serial.stopbits = stopbits
			instrument.serial.timeout = timeout
			linear_modbus.info("Modbus Connection established successfully")
			return instrument
		except: 
			linear_modbus.error("Error in establishing Modbus Connection")

	def selectReadFunc(self, instrument, addr, datatype):
		if datatype == 'U32':
			print("U32")
			return instrument.read_long(addr, functioncode=3, signed=True)

		if datatype == 'U16':
			print("U16")
			return instrument.read_register(addr, numberOfDecimals=0, functioncode=3, signed=True)

		if datatype == 'F':
			print("Float")
			return instrument.read_float(addr, functioncode=3, numberOfRegisters=2)


	def modRead(self, rjson):
		for i in range(len(rjson.serial_port_status)):
			if rjson.serial_port_status[i] == 'enabled':
				for j in range(len(self.all_device_address[i])):
					try:
						instrument = self.init_modbus(rjson.mod_port_addr[i], self.all_device_address[i][j] ,\
													  rjson.mod_baudrate[i], rjson.mod_databits[i], rjson.mod_parity[i], \
													  rjson.mod_stopbits[i], rjson.mod_poll_timeout[i])
						instrument.debug = False
						for k in range(self.all_length[i][j][0]):
							retry_counter = 0
							while retry_counter < self.all_retry_counts[i][j]: 
								print (i,j,k)
								try:
									print (self.selectReadFunc(instrument, self.all_addresses[i][j][k], self.all_datatype[i][j][k]))
									break
								except:
									linear_modbus.info("Error in a reading address " + str(self.all_addresses[i][j][0]) + \
												   ". Retrying...")
									if retry_counter == 2:
										raise
									retry_counter += 1
						time.sleep(self.cons_read_reg_timeout)

					except ValueError as e:
						linear_modbus.error("Value Error : ({0})".format(e))
					except TypeError as e:
						linear_modbus.error("Type Error : ({0})".format(e))
					except IOError as e:
						linear_modbus.error("IO Error : ({0})".format(e))
					except:
						linear_modbus.error("Failure due to other errors")
			else:
				linear_modbus.info("Port " + rjson.mod_port_addr[i] +" is disabled")
		return "hello"

	def ModCreateFile(self, rjson):
		# read the Modbus data for the specified addresses
		read_value = self.modRead(rjson)
		# convert the data read from modbus in a particular format
		# value = self.ModFileConversion(read_value, rjson)
		# Increment the file counter, when file is sent
		self.mod_data_file_timestamp = time.strftime("%Y%m%d-%H%M%S")

		# create the file name
		self.mod_data_file = self.mod_data_file_path + rjson.mod_data_file_initial \
							+ self.mod_data_file_timestamp + self.mod_data_file_ext
		# write the data into the file
		with open(self.mod_data_file, 'w') as f: 
			f.write(read_value)	