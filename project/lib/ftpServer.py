		#!/usr/bin/env python

from ftplib import FTP
import json
import sys
import os
import logging

class FTP_node(object):
	
	def __init__(self):
		logging.basicConfig(level=10,
                    format='%(levelname)s %(asctime)s %(threadName)s %(message)s',
                    filename='./project/Log_files/test.log',
                    filemode='a')
		# Timeout for FTP Failure
		self.timeOut = 10
		logging.info("FTP node Initialized")
		# print("FTP Node Initialized...")
	
	def FTP_connect(self, user_id, password, ip_addr, port_num, path):
		# print ("Connecting to FTP Server...")
		logging.info("Connecting to FTP Server...")
		# set initialize as True
		retry = True
		# continue the loop until retry is true
		while (retry):
			try:
				# Create FTP Node with the existing Credentials
				ftp = FTP(ip_addr, user_id, password, self.timeOut)
				ftp.cwd(path)
				# Print the Welcome Message
				# print ( ftp.getwelcome() )
				# If Connection is made, make, retry as false
				retry = False
				logging.info('FTP Connection Successful')

			# Handle all kinds of existing errors while making the connection
			except IOError as e:
				logging.error("I/O error({0}): {1}".format(e.errno, e.strerror))
				# print ("I/O error({0}): {1}".format(e.errno, e.strerror))
				# Run the loop until connection is a Success
				retry = True
				logging.debug("Still trying to connect to FTP Server...")
		return ftp

	
	def FTP_Close(self):
		ftp = FTP()
		ftp.close()
		# print ("Closing the FTP Connection...")
		logging.info("Closing the FTP Connection...")

	
	def FTP_upload(self, cred, file_path):
		try:
			# Fetch the File name
			final_file_name=os.path.basename(file_path)
			# print('Uploading ' + final_file_name + '...')
			logging.info('Uploading ' + final_file_name + '...')
			# Fetch the File extension
			ext = os.path.splitext(final_file_name)[1]

			if ext in (".csv"):
				cred.storbinary('STOR '+ final_file_name, open(file_path, 'rb'))
				# print('Upload finished.')
				logging.info('Upload finished')
			else:
				# print('File Format other than csv')
				logging.info("File Format other than csv")
		
		# Handle all the exceptions while File upload
		except IOError:
			logging.error("No such file or directory... passing to next file")
			# print ("No such file or directory... passing to next file")
