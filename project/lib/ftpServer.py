#!/usr/bin/env python

# Import necessary Libraries
from ftplib import FTP
import json
import sys
import os
# Variable definitions
true = 1
false = 0

#################################

Naveen:
add doc strings to all  functios 

############################### 



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
		# FTP Credentials initialization
		self.user_id = "Anonymous"
		self.password = "Anonymous"
		self.ip_addr = "xx.xx.xx.xx"
		self.port_num = 21
		self.server_upload_time = 100
		print("FTP Node Initialized...")

	#***********************************************************#
	#******    Function to Create the FTP Connection    ********#
	#***********************************************************#
	def FTP_connect(self, user_id, password, ip_addr, port_num):
		print ("Connecting to FTP Server...")
		# set initialize as True
		retry = true
		# continue the loop until retry is true
		while (retry):
			try:
				# Create FTP Node with the existing Credentials
				ftp = FTP(ip_addr, user_id, password, self.timeOut)
				ftp.cwd(self.path)
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

	#***********************************************************#
	#******    Function to Read the Credentials File    ********#
	#***********************************************************#
	def Read_JSON(self, cred_file_path):
		# Fetch the File name
		cred_file = os.path.basename(cred_file_path)
		# Fetch the file extension
		ext = os.path.splitext(cred_file)[1]
		# if file type is JSON
		if ext in (".json"):
			print ("Reading FTP Credentials")
			# Open and Load JSON File
			with open(cred_file_path) as data_file:    
				data = json.load(data_file)

			# Fetch all the credentials
			self.user_id = data["ftp"]["name"]
			self.password = data["ftp"]["password"]
			self.ip_addr = data["ftp"]["server"]
			self.port_num = data["ftp"]["port"]
			self.path = data["ftp"]["path"]
			self.server_upload_time = data["Ftp_interval"]
		# if file type is not JSON
		else:
			print ("File not in JSON Format")

# # Main Loop starts here
# if __name__ == '__main__':
# 	# take the fisrt file from the passed argument
# 	cred_file = sys.argv[1]
# 	# take the second file from the passed argument
# 	file = sys.argv[2]
	
# 	# Call FTP NODE
# 	Ftp = FTP_node()
# 	# Read JSON file
# 	Ftp.Read_JSON(cred_file)
# 	# Make Connection
# 	cred = Ftp.FTP_connect(Ftp.user_id, Ftp.password, Ftp.ip_addr, Ftp.port_num)
# 	# Upload the required file
# 	Ftp.FTP_upload(cred, file)
