#!/usr/bin/env python

# Import necessary Libraries
from ftplib import FTP
import json
import sys
import os
# Variable definitions
true = 1
false = 0

#***********************************************************#
#********************    FTP Class Node    *****************#
#***********************************************************#

class FTP_node(object):
	#***********************************************************#
	#***************    Class Initialization    ****************#
	#***********************************************************#
	def __init__(self):
		# Timeout for FTP Failure
		self.timeOut = 10
		print("FTP Node Initialized...")

	#***********************************************************#
	#******    Function to Create the FTP Connection    ********#
	#***********************************************************#
	def FTP_connect(self, user_id, password, ip_addr, port_num, path):
		print ("Connecting to FTP Server...")
		# set initialize as True
		retry = true
		# continue the loop until retry is true
		while (retry):
			try:
				# Create FTP Node with the existing Credentials
				ftp = FTP(ip_addr, user_id, password, self.timeOut)
				ftp.cwd(path)
				# Print the Welcome Message
				print ( ftp.getwelcome() )
				# If Connection is made, make, retry as false
				retry = false

			# Handle all kinds of existing errors while making the connection
			except IOError as e:
				print ("I/O error({0}): {1}".format(e.errno, e.strerror))
				print ("Retrying...")
				# Run the loop until connection is a Success
				retry = true
		return ftp

	#***********************************************************#
	#******    Function to Close the FTP Connection    *********#
	#***********************************************************#
	def FTP_Close(self):
		ftp = FTP()
		ftp.close()
		print ("Closing the FTP Connection...")

	#***********************************************************#
	#******    Function to Upload File on FTP Server    ********#
	#***********************************************************#
	def FTP_upload(self, cred, file_path):
		try:
			# Fetch the File name
			final_file_name=os.path.basename(file_path)
			print('Uploading ' + final_file_name + '...')
			# Fetch the File extension
			ext = os.path.splitext(final_file_name)[1]

			if ext in (".csv"):
				cred.storbinary('STOR '+ final_file_name, open(file_path, 'rb'))
				print('Upload finished.')
			else:
				print('File Format other than csv')
		
		# Handle all the exceptions while File upload
		except IOError:
			print ("No such file or directory... passing to next file")
