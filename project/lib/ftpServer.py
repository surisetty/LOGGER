		#!/usr/bin/env python

# Import necessary Libraries
from ftplib import FTP
import json
import sys
import os
import logging
mylogger_ftp = logging.getLogger('mylogger.ftp')

class FtpNode(object):
	def __init__(self):
		# Timeout for FTP Failure
		self.timeOut = 10
		self.ftp_all_good = 0
		mylogger_ftp.info("FTP node Initialized")
		
	def FtpConnect(self, user_id, password, ip_addr, port_num, path):
		mylogger_ftp.info("Connecting to FTP Server...")
		# set initialize as True
		retry = True
		# continue the loop until retry is true
		while (retry):
			try:
				# Create FTP Node with the existing Credentials
				ftp = FTP(ip_addr, user_id, password, self.timeOut)
				ftp.set_pasv (1)
				ftp.cwd(path)
				# If Connection is made, make, retry as false
				retry = False

				mylogger_ftp.info('FTP Connection Successful')

			# Handle all kinds of existing errors while making the connection
			except IOError as e:
				mylogger_ftp.error("I/O error({0}): {1}".format(e.errno, e.strerror))
				# Run the loop until connection is a Success
				retry = True
				mylogger_ftp.info("Still trying to connect to FTP Server...")
		return ftp

	def FtpClose(self):
		ftp = FTP()
		ftp.close()
		mylogger_ftp.info("Closing the FTP Connection...")

	def FtpUpload(self, cred, file_path):
		try:
			# Fetch the File name
			final_file_name=os.path.basename(file_path)
			mylogger_ftp.info('Uploading ' + final_file_name + '...')
			# Fetch the File extension
			ext = os.path.splitext(final_file_name)[1]

			if ext in (".csv"):
				cred.storbinary('STOR '+ final_file_name, open(file_path, 'rb'))
				mylogger_ftp.info('Upload finished')
				self.ftp_all_good = 1
			else:
				mylogger_ftp.info("File Format other than csv")
		
		# Handle all the exceptions while File upload
		except Exception as e:
			mylogger_ftp.error("Error uploading file: " + str(e))
			self.ftp_all_good = 0
