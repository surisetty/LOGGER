#!/usr/bin/python

# import basic libraries
import os
import _thread
import time
import sys
from ftpServer import FTP_node
from modbus import MODBUS_node

# exit flag for thread exit, initialized to 0
exitFlag = 0

#***********************************************************#
#******    Thread function to read modbus device    ********#
#***********************************************************#
def mod_read(threadName, delay):
	# continue reading the data until exit flag is set high
	while 1:
		if exitFlag:
			# exit the thread when exit flag is set
			threadName.exit()
		# sleep for the required time 
		time.sleep(delay)
		# Read the required Addresses
		Modbus.Mod_Create_file()
		
#***********************************************************#
#******    Thread function to send modbus file    **********#
#***********************************************************#
def send_file(threadName, delay):
	cred = Ftp.FTP_connect(Ftp.user_id, Ftp.password, Ftp.ip_addr, Ftp.port_num)
	while 1:
		# continue reading the data until exit flag is set high
		if exitFlag:
			# exit the thread when exit flag is set
			threadName.exit()
		# sleep for the required time
		time.sleep(delay)
		# Upload the required file
		test = Ftp.FTP_upload(cred, Modbus.mod_created_file_name)
		# FTP connection close
		Ftp.FTP_Close()
		# remove the uploaded file when sent
		os.remove(Modbus.mod_created_file_name)
		# Increment the file counter, when file is sent
		Modbus.mod_file_counter += 1

# Get the credential file as an input
cred_file = sys.argv[1]
# Get the modbus input file as an input
mod_file = sys.argv[2]

# create Modbus node
Modbus = MODBUS_node()
# read the input file to fetch the addresses to read
Modbus.Read_ADDR_Input_file(mod_file)

Modbus.Read_JSON(cred_file)

# create FTP node
Ftp = FTP_node()
# read the JSON file to get the credentials of the FTP
Ftp.Read_JSON(cred_file)
# connect to FTP 
# cred = Ftp.FTP_connect(Ftp.user_id, Ftp.password, Ftp.ip_addr, Ftp.port_num)

try:
   # Start Modbus Read Thread
   _thread.start_new_thread( mod_read, ("Mod_read", float(Modbus.modbus_fetch_time), ) )
   # Start FTP file Upload Thread
   _thread.start_new_thread( send_file, ("Ftp_Send", float(Ftp.server_upload_time),) )
except:
   print ("Error: unable to start _thread")

while 1:
   pass

