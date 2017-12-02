#!/usr/bin/python

# import basic libraries
import os
import _thread
import threading
import time
import sys
import ftplib
import yaml
import logging
import logging.config
import logging.handlers
from lib.json_read import ReadConfig
from lib.ftpServer import FtpNode
from lib.mod_gen import ModbusNode

# exit flag for thread exit, initialized to 0
exitFlag = 0

def ModRead(threadName, delay, rjson, port_num):
	while 1:
		if exitFlag:
			# exit the thread when exit flag is set
			threadName.exit()
		# sleep for the required time 
		time.sleep(delay)
		# Read the required Addresses
		Modbus.ModCreateFile(rjson, port_num)
		# print (threadName)
		linear.info("Modbus Read Cycle completed, Data collected")
		
def FtpSendFile(threadName, delay):
	while 1:
		data_files = sorted(os.listdir(Modbus.mod_data_file_path))
		if len(data_files) > 0:
			del data_files[-1]
		files_to_send = len(data_files)
		if files_to_send >= 1:
			cred = Ftp.FtpConnect(RJSON.ftp_user_id, RJSON.ftp_password, RJSON.ftp_ip_addr,\
										 RJSON.ftp_port_num, RJSON.ftp_path)
			# continue reading the data until exit flag is set high
			if exitFlag:
				# exit the thread when exit flag is set
				threadName.exit()
			# sleep for the required time
			time.sleep(delay)
			for loop in range(files_to_send):
				# Upload the required file
				try: 
					test = Ftp.FtpUpload(cred, Modbus.mod_data_file_path + data_files[loop])
					# remove the uploaded file when sent
					if Ftp.ftp_all_good:
						os.remove(Modbus.mod_data_file_path + data_files[loop])
						linear.info("Uploaded file removed from the location")
						Ftp.ftp_all_good = 0
				except ftplib.error_temp as e:
						linear.error("File Transfer error, Trying again ...({0})"\
										.format(e))
			# FTP connection close
			Ftp.FtpClose()


log_conf_path = sys.path[0] + '/config/linear_log_config.yaml'
with open(log_conf_path, 'r') as f:
    conf = yaml.load(f)

logging.config.dictConfig(conf)
# Get the credential file as an input
cred_file = sys.path[0] + "/config/linear_config.json"
linear = logging.getLogger('linear')

# call the Read Json node
RJSON = ReadConfig()
# Read the JSON file (config) 
RJSON.ReadJson(cred_file)


# Get the modbus input file as an input
mod_files = []
for loop in range(len(RJSON.mod_slaves)):
	if RJSON.serial_port_status[loop] == 'enabled':
		linear.info("Active Port : %s", RJSON.mod_port_addr[loop])
		# for i in range(len(RJSON.mod_slaves[loop])):
		mod_files.append(RJSON.mod_slaves[loop])
	else:
		linear.info("Inactive Port : %s", RJSON.mod_port_addr[loop])
# create Modbus node
Modbus = ModbusNode()
Port_num = 0
# read the input file to fetch the addresses to read
Modbus.ReadInputFile(mod_files[Port_num])
# create FTP node
Ftp = FtpNode()

try:
   # Start Modbus Read Thread
   linear.info("Running Thread for Modbus")
   _thread.start_new_thread( ModRead, ("MODBUS", float(RJSON.mod_fetch_time), RJSON, Port_num, ) )
   
   # Start FTP file Upload Thread
   linear.info("Running Thread for FTP")
   _thread.start_new_thread( FtpSendFile, ("FTP", float(RJSON.ftp_server_upload_time),) )
   
except:
   # print ("Error: unable to start _thread")
   linear.error("Unable to start thread")

while 1:
   pass
