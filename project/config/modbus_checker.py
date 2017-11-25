#!/usr/bin/env python

import pymodbus
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from pymodbus.transaction import ModbusRtuFramer

client= ModbusClient(method = "rtu", port="/dev/ttyUSB0",stopbits = 1,\
					 bytesize = 8, parity = 'E', baudrate= 9600)

#Connect to the serial modbus server
connection = client.connect()

#Starting add, num of reg to read, slave unit.
result= client.read_holding_registers(0x00,1,unit= 0xff)

print(result.registers[0])

#Closes the underlying socket connection
client.close()