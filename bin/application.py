#!/usr/bin/python

# Naveen : First declare os libraries then application libraries

from ftpServer import FTP_node
from modbus import MODBUS_node
import _thread
import time
import sys

exitFlag = 0

def mod_read(threadName, delay):
	while 1:
		if exitFlag:
			threadName.exit()
		time.sleep(delay)
		# Read the required Addresses
		Modbus.Mod_Create_file()

def send_file(threadName, delay, cred, filepath):
	while 1:
		if exitFlag:
			threadName.exit()
		time.sleep(delay)
		# Upload the required file
		Ftp.FTP_upload(cred, filepath)

# Take the credential file as the input
cred_file = sys.argv[1]
filepath = sys.argv[2]
mod_file = sys.argv[3]

Modbus = MODBUS_node()
Modbus.Read_ADDR_Input_file(mod_file)
Modbus.Read_JSON(cred_file)

Ftp = FTP_node()
Ftp.Read_JSON(cred_file)
cred = Ftp.FTP_connect(Ftp.user_id, Ftp.password, Ftp.ip_addr, Ftp.port_num)

try:
   _thread.start_new_thread( mod_read, ("Mod_read", float(Modbus.modbus_fetch_time), ) )
   _thread.start_new_thread( send_file, ("Ftp_Send", float(Ftp.server_upload_time), cred, filepath, ) )
except:
   print ("Error: unable to start _thread")
   # Naveen : Can we have exit value printed ? . also log error for each of the thread

while 1:
   pass

