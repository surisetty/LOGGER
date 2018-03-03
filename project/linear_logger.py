#!/usr/bin/python

# import basic libraries
import os
import glob
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
from lib.exceptions import HandleError
from lib.ftpServer import FtpNode
from lib.mod_gen import ModbusNode

# exit flag for thread exit, initialized to 0
exitFlag = 0

def ModRead(threadName, delay, rjson, ports, port_num):
	while 1:
		#print("port : ", port_num)
		if exitFlag:
			# exit the thread when exit flag is set
			threadName.exit()
		# sleep for the required time 
		time.sleep(delay)
		# Read the required Addresses
		Modbus_Nodes_lists[ports].ModCreateFile(rjson, port_num)		
		# print (threadName)
		linear.info("Modbus Read Cycle completed, Data collected")
		
def FtpSendFile(threadName, delay, ports):
	while 1:
		try:
			#print(Modbus_Nodes_lists[0])
			data_files = glob.glob(Modbus_Nodes_lists[0].mod_data_file_path + '/*.csv')
			data_files = sorted(data_files, key=os.path.getmtime)
			if len(data_files) > 0:
				del data_files[-ports:]
			files_to_send = len(data_files)
			if files_to_send > 0:
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
						test = Ftp.FtpUpload(cred, data_files[loop])
						# remove the uploaded file when sent
						if Ftp.ftp_all_good:
							os.remove(data_files[loop])
							linear.info("Uploaded file removed from the location")
							Ftp.ftp_all_good = 0
					except ftplib.error_temp as e:
							linear.error("File Transfer error, Trying again ...({0})"\
											.format(e))
				# FTP connection close
				Ftp.FtpClose()
		except:
			handler = HandleError('103', 'can\'t find mod file path' )
			linear.error("Error : {0} - {1}".format(handler.code, handler.str))


rtu_file_path = os.path.dirname(os.path.abspath(__file__))
path, file = os.path.split(rtu_file_path)
#print(path)
rtu_file_path = os.path.join(path, 'project', 'config')
#print("relative path", rtu_file_path)
data_file_path = os.path.join(path, 'project', 'Data')
log_file_path = os.path.join(path, 'project', 'Log_files')
log_conf_path = os.path.join(path, 'project', 'config', 'linear_log_config.yaml')

log_dir = log_file_path
data_dir = data_file_path

if not os.path.exists(log_dir):
    os.makedirs(log_dir)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

with open(log_conf_path, 'r') as f:
	conf = yaml.load(f)

logging.config.dictConfig(conf)
# Get the credential file as an input
cred_file = os.path.join(path, 'project', 'config', 'config.json')
linear = logging.getLogger('linear')


try:
	# call the Read Json node
	RJSON = ReadConfig()
	# Read the JSON file (config) 
	RJSON.ReadJson(cred_file)
except:
	handler = HandleError('101', 'Can\'t read config (JSON) file' )
	linear.error("Error : {0} - {1}".format(handler.code, handler.str))

# Get the modbus input file as an input
mod_files = []
port_num = []
for loop in range(len(RJSON.mod_slaves)):
	if RJSON.serial_port_status[loop] == 'enabled':
		linear.info("Active Port : %s", RJSON.mod_port_addr[loop])
		# for i in range(len(RJSON.mod_slaves[loop])):
		mod_files.append(RJSON.mod_slaves[loop])
		port_num.append(loop)
	else:
		linear.info("Inactive Port : %s", RJSON.mod_port_addr[loop])

# create Modbus node
Modbus_Nodes_lists = []
for ports in range(len(mod_files)):
	Modbus_Nodes_lists.append(ModbusNode())
	# read the input file to fetch the addresses to read
	Modbus_Nodes_lists[ports].ReadInputFile(mod_files[ports])
# create FTP node
Ftp = FtpNode()
#print("Mod files : ", mod_files)
try:
   # Start Modbus Read Thread
   linear.info("Running Thread for Modbus")
   for ports in range(len(mod_files)):
        _thread.start_new_thread( ModRead, ("MODBUS", float(RJSON.mod_fetch_time), RJSON,\
        						 ports, port_num[ports]) ,)
   
   # Start FTP file Upload Thread
   linear.info("Running Thread for FTP")
   _thread.start_new_thread( FtpSendFile, ("FTP", float(RJSON.ftp_server_upload_time), len(mod_files)) )
   
except:
   # print ("Error: unable to start _thread")
   handler = HandleError('102', 'Can\'t create Threads' )
   linear.error("Error : {0} - {1}".format(handler.code, handler.str))

while 1:
   pass
