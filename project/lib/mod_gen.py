#!/usr/bin/env python

# Import necessary Libraries
import sys
import os
import time
import minimalmodbus 
import serial
import logging
from lib.rtu_read import RTU_READ
from lib.exceptions import HandleError

minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True

linear_modbus = logging.getLogger('linear.modbus')

class ModbusNode(object):
	def __init__(self):
		self.cons_read_reg_timeout = 0.3
		# List to store modbus read addresses
		self.all_addresses = []
		self.all_length = []
		self.all_datatype = []
		self.all_functionCodes = []
		self.all_endianness = []
		self.all_device_address = []
		self.all_retry_counts = []
		self.all_files = []
		# File containing the modbus responses of the read addresses 
		self.mod_data_file = ""
		# File location and name containing the modbus responses of the read addresses 
		rtu_file_path = os.path.dirname(os.path.abspath(__file__))
		path, file = os.path.split(rtu_file_path)
		self.rtu_file_path = os.path.join(path, 'config')
		#print("r_path : ", self.rtu_file_path)
		self.data_file_path = os.path.join(path, 'Data')		
		#print("path : ",self.data_file_path)
		self.mod_data_file_path = self.data_file_path
		# File extension of the file containing the modbus responses of the read addresses 
		self.mod_data_file_ext = '.csv'
		#create file name initial
		timestr = time.strftime("%Y%m%d-%H%M%S")
		# File number counter
		self.mod_data_file_timestamp = timestr
		self.mod_file_port_addr = ""
		# log data
		linear_modbus.info("MODBUS Node Initialized...")
		# call RTU_READ node


	def ReadInputFilesPortwise(self, file_path_string, files_name):	
		RTU = RTU_READ()
		filename = file_path_string + '/' + files_name
		#print("myName: ", filename)
		RTU.ReadRtuFile(filename)
		if RTU.rtu_file_active_status == "True":
			address = RTU.file_addresses
			length = RTU.address_length
			datatype = RTU.datatypes
			functionCodes = RTU.functionCodes
			endianness = RTU.rtu_file_endian_mode
			device_address = RTU.rtu_device_address
			retry_counts = RTU.rtu_retry_count
			return (address, length, datatype, endianness, device_address, retry_counts, functionCodes)
		else:
			return(None, None, None, None, None, None, None)


	def ReadInputFile(self, ports):
		try:
			# List to store all the files attached on all active ports
			file_path_string = self.rtu_file_path
			#print("f_path: ", file_path_string)
			for loop in range(len(ports)):
				(address, length, datatype, endianness, device_address, retry_counts, functionCodes) = \
											self.ReadInputFilesPortwise(file_path_string, ports[loop])
				self.all_addresses.append(address)
				self.all_length.append(length)
				self.all_datatype.append(datatype)
				self.all_functionCodes.append(functionCodes)
				self.all_endianness.append(endianness)
				self.all_device_address.append(device_address)
				self.all_retry_counts.append(retry_counts)
				self.all_files = ports
			# print (self.all_addresses)
			# print (self.all_length)
			# print (self.all_datatype)
			# print (self.all_functionCodes)
			# print (self.all_endianness)
			# print (self.all_device_address)
			# print (self.all_retry_counts)
		except Exception as e:
			handler = HandleError('51', 'Can\'t read Input files, RTU read Error' )
			linear_modbus.error("Error : {0} - {1}".format(handler.code, handler.str))



	def getByteLength(self, datatype):
		if datatype == 'U32':
			return 2
		if datatype == 'F':
			return 2
		if datatype == 'U16':
			return 1 
		if datatype == 'S16':
			return 1
		if datatype == 'S32':
			return 2 

	def getEndianness(self,endian):
		if endian == 'big':
			return '>'
		else:
			return '<'

	def selectReadFunc(self, instrument, addr, datatype, functionCode, endian=None):
		if datatype == 'S32':
			# print("U32")
			return instrument.read_long(addr, functioncode=functionCode, signed=True, endian= endian)

		if datatype == 'S16':
			# print("U16")
			return instrument.read_register(addr, numberOfDecimals=0, functioncode=functionCode, signed=True)

		if datatype == 'U32':
			# print("U32")
			return instrument.read_long(addr, functioncode=functionCode, signed=False, endian= endian)

		if datatype == 'U16':
			# print("U16")
			return instrument.read_register(addr, numberOfDecimals=0, functioncode=functionCode, signed=False)

		if datatype == 'F':
			# print("Float")
			value = instrument.read_float(addr, functioncode=functionCode, numberOfRegisters=2, endian= endian )
			return float(format(value, ".3f"))


	def init_modbus(self, port_addr, device_addr, baudrate, bytesize, parity, stopbits, timeout):
			try:
				instrument = minimalmodbus.Instrument(port_addr, device_addr)
				instrument.serial.baudrate= baudrate
				instrument.serial.bytesize = bytesize
				instrument.serial.parity = parity
				instrument.serial.stopbits = stopbits
				instrument.serial.timeout = timeout
				instrument.debug = True
				linear_modbus.info("Modbus Connection established successfully")
				return instrument
			except Exception as e:
				handler = HandleError('52', 'can\'t establish connection, Device not connected' )
				linear_modbus.error("Error : {0} - {1}".format(handler.code, handler.str))


	def modRead(self, rjson, port_num):
		# print("hello")
		# print(rjson.mod_port_addr)
		# print(rjson.mod_baudrate)
		# print(rjson.mod_databits)					  
		# print(rjson.mod_parity)
		# print(rjson.mod_stopbits)
		# print(rjson.mod_poll_timeout)
		# print("end")
		port_data = []
		for file_count in range(len(self.all_device_address)):
			if self.all_addresses[file_count] == None:
				continue
			
			file_result = []
			instrument = self.init_modbus(rjson.mod_port_addr[port_num], self.all_device_address[file_count] ,\
										  rjson.mod_baudrate[port_num], rjson.mod_databits[port_num],\
										  rjson.mod_parity[port_num], rjson.mod_stopbits[port_num],\
										  rjson.mod_poll_timeout[port_num])
			try:
				instrument.debug = False
				for addr_in_files in range(len(self.all_addresses[file_count])):
					addr_data = []
					for len_count in range(self.all_length[file_count][addr_in_files]):
						retry_counter = 0
						while retry_counter < self.all_retry_counts[file_count]:
							try:
								bytelength = self.getByteLength(self.all_datatype[file_count][addr_in_files])
								result =  (self.selectReadFunc(instrument, \
									  (self.all_addresses[file_count][addr_in_files] + len_count * bytelength), \
									   self.all_datatype[file_count][addr_in_files], \
									   self.all_functionCodes[file_count][addr_in_files], \
									   self.getEndianness(self.all_endianness[file_count])))
								addr_data.append(result)
								break
							except Exception as e:
								#print (e)
								handler = HandleError('53', "Error in reading address " + str(self.all_addresses[file_count][addr_in_files]) + \
										   ". Retrying..." + "Check the data in rtu file again" )
								linear_modbus.warn("Error : {0} - {1}".format(handler.code, handler.str))
								if retry_counter == self.all_retry_counts[file_count]:
									result = 'error'
									addr_data.append(result)
									raise
								retry_counter += 1
					time.sleep(self.cons_read_reg_timeout)
					file_result.append(addr_data)		
			except ValueError as e:
				linear_modbus.error("Value Error : ({0})".format(e))
			except TypeError as e:
				linear_modbus.error("Type Error : ({0})".format(e))
			except IOError as e:
				linear_modbus.error("IO Error : ({0})".format(e))
			except:
				linear_modbus.error("Failure due to other errors")
			port_data.append(file_result)
		return port_data

	def ModFileConversion(self, data, rjson):
		try:
			row = ""
			for files in range(len(data)):
				#add 1st line in output file	
				row += "ADDRMODBUS" + ";" + str(self.all_device_address[files]) + "\n"
				# add 2nd line in output file
				row += "TypeMODBUS" + ";" + self.all_files[files] + "\n"
				total_count = 0
				# adding 3rd line in output  file
				counts_val = []
				for counts in range(len(self.all_length[files])):
					total_count = total_count + self.all_length[files][counts]
				for val in range(total_count):
					counts_val.append(val+1)
				addr_count = ';'.join(str(e) for e in counts_val)
				row += str(total_count) + ";" + addr_count + "\n"
				# adding 4th line in output file
				results = []
				for res in range(len(data[files])):
					for length in range(len(data[files][res])):
						results.append(data[files][res][length])

				addr_results = ';'.join(str(e) for e in results)
				row += time.strftime("%d/%m/%Y-%H:%M:%S", time.localtime()) + ";" + addr_results + "\n" 
			return row
		except: 
			handler = HandleError('54', 'error in data file conversion' )
			linear_modbus.error("Error : {0} - {1}".format(handler.code, handler.str))


	def ModCreateFile(self, rjson, port_num):
		# read the Modbus data for the specified addresses
		read_value = self.modRead(rjson, port_num)
		# convert the data read from modbus in a particular format
		value = self.ModFileConversion(read_value, rjson)
		#print(value)
		# get port address
		self.mod_file_port_addr = "COM" + str(port_num) + "_"
		# print(self.mod_file_port_addr)
		# Increment the file counter, when file is sent
		self.mod_data_file_timestamp = time.strftime("%Y%m%d-%H%M%S")

		# create the file name
		self.mod_data_file = self.mod_data_file_path +'/'+ self.mod_file_port_addr +\
							 rjson.mod_data_file_initial + self.mod_data_file_timestamp +\
							  self.mod_data_file_ext
		# write the data into the file
		try:
			with open(self.mod_data_file, 'w') as f: 
				f.write(value)	
		except:
			handler = HandleError('55', 'error in writing in file, Data successfully created' )
			linear_modbus.error("Error : {0} - {1}".format(handler.code, handler.str))