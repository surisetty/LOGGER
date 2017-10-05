#!/usr/bin/python

# import basic libraries
import os
import _thread
import threading
import time
import sys
import logging
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
		# print (threadName)
		logging.info("Modbus Read Cycle completed, Data collected")
		
#***********************************************************#
#******    Thread function to send modbus file    **********#
#***********************************************************#
def send_file(threadName, delay):
	while 1:
		data_files = sorted(os.listdir(Modbus.mod_data_file_path))
		del data_files[-1]
		files_to_send = len(data_files)
		if files_to_send >= 1:
			cred = Ftp.FTP_connect(RJSON.ftp_user_id, RJSON.ftp_password, RJSON.ftp_ip_addr,\
										 RJSON.ftp_port_num, RJSON.ftp_path)
			# continue reading the data until exit flag is set high
			if exitFlag:
				# exit the thread when exit flag is set
				threadName.exit()
			# sleep for the required time
			time.sleep(delay)
			for loop in range(files_to_send):
				# Upload the required file
				test = Ftp.FTP_upload(cred, Modbus.mod_data_file_path + data_files[loop])
				# remove the uploaded file when sent
				os.remove(Modbus.mod_data_file_path + data_files[loop])
			# FTP connection close
			Ftp.FTP_Close()
			logging.info("Uploaded file removed from the location")
		else:
			logging.info("No files to send")

# Get the credential file as an input
cred_file = sys.path[0] + "/config/config.json"
# call the Read Json node
RJSON = Read_Config()
# Read the JSON file (config) 
RJSON.Read_JSON(cred_file)

# Initializing the logging settings
logging.basicConfig(level=RJSON.logging_level,
                    format='%(levelname)s %(message)s',
                    filename='./project/Log_files/test.log',
                    filemode='w')	
# Get the modbus input file as an input
mod_file = []
for loop in range(len(RJSON.mod_input_file)):
	mod_file.append(sys.path[0] + "/config/" + RJSON.mod_input_file[loop])

# create Modbus node
Modbus = MODBUS_node()
# read the input file to fetch the addresses to read
Modbus.Read_input_file(mod_file)
# create FTP node
Ftp = FTP_node()
try:
   # Start Modbus Read Thread
   logging.info("Running Thread for Modbus")
   _thread.start_new_thread( mod_read, ("MODBUS", float(RJSON.mod_fetch_time), RJSON, ) )
   
   # Start FTP file Upload Thread
   logging.info("Running Thread for FTP")
   _thread.start_new_thread( send_file, ("FTP", float(RJSON.ftp_server_upload_time),) )
   
except:
   # print ("Error: unable to start _thread")
   logging.error("Unable to start thread")

while 1:
   pass