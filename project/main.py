#!/usr/bin/python

# import basic libraries
import os
import _thread
import time
import sys
from lib.json_read import Read_Config
from lib.ftpServer import FTP_node
from lib.modbus import MODBUS_node

# exit flag for thread exit, initialized to 0
exitFlag = 0

#***********************************************************#
#******    Thread function to read modbus device    ********#
#***********************************************************#
def mod_read(threadName, delay, rjson):
	# continue reading the data until exit flag is set high
	while 1:
		if exitFlag:
			# exit the thread when exit flag is set
			threadName.exit()
		# sleep for the required time 
		time.sleep(delay)
		# Read the required Addresses
		Modbus.Mod_Create_file(rjson)
		
#***********************************************************#
#******    Thread function to send modbus file    **********#
#***********************************************************#
def send_file(threadName, delay):
	while 1:
		cred = Ftp.FTP_connect(RJSON.ftp_user_id, RJSON.ftp_password, RJSON.ftp_ip_addr,\
									 RJSON.ftp_port_num, RJSON.ftp_path)
		# continue reading the data until exit flag is set high
		if exitFlag:
			# exit the thread when exit flag is set
			threadName.exit()
		# sleep for the required time
		time.sleep(delay)
		# Upload the required file
		test = Ftp.FTP_upload(cred, Modbus.mod_data_file)
		# FTP connection close
		Ftp.FTP_Close()
		# remove the uploaded file when sent
		os.remove(Modbus.mod_data_file)
		# create file name
		timestr = time.strftime("%Y%m%d-%H%M%S")
		# Increment the file counter, when file is sent
		Modbus.mod_data_file_timestamp = timestr

# Get the credential file as an input
cred_file = sys.path[0] + "/config/config.json"
# call the Read Json node
RJSON = Read_Config()
# Read the JSON file (config) 
RJSON.Read_JSON(cred_file)
# Get the modbus input file as an input
mod_file = sys.path[0] + "/config/" + RJSON.mod_input_file
# create Modbus node
Modbus = MODBUS_node()
# read the input file to fetch the addresses to read
Modbus.Read_input_file(mod_file)
# create FTP node
Ftp = FTP_node()
try:
   # Start Modbus Read Thread
   _thread.start_new_thread( mod_read, ("Mod_read", float(RJSON.mod_fetch_time), RJSON, ) )
   # Start FTP file Upload Thread
   _thread.start_new_thread( send_file, ("Ftp_Send", float(RJSON.ftp_server_upload_time),) )
except:
   print ("Error: unable to start _thread")

while 1:
   pass