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
		self.timeOut = 20
		# FTP Credentials initialization
		self.user_id = "Anonymous"
		self.password = "Anonymous"
		self.ip_addr = "xx.xx.xx.xx"
		self.port_num = 21
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
				# ftp.cwd('/home/test')
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
			if ext in (".txt", ".htm", ".html"):
				# send the file in non-binary format if file type is txt
				cred.storlines("STOR " + final_file_name, open(final_file_name))
			else:
				# send the file in binary format if file type is not text
				cred.storbinary("STOR " + final_file_name, open(final_file_name, "rb"))
			print('Upload finished.')
		
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
			print ("Reading Credentials")
			# Open and Load JSON File
			with open(cred_file_path) as data_file:    
				data = json.load(data_file)
			# Fetch all the credentials
			self.user_id = data["credentials"][0]["user_id"]
			self.password = data["credentials"][1]["password"]
			self.ip_addr = data["credentials"][2]["ip_addr"]
			self.port_num = data["credentials"][3]["port_num"]
		# if file type is not JSON
		else:
			print ("File not in JSON Format")

# Main Loop starts here
if __name__ == '__main__':
	# take the fisrt file from the passed argument
	cred_file = sys.argv[1]
	# take the second file from the passed argument
	file = sys.argv[2]
	
	# Call FTP NODE
	Ftp = FTP_node()
	# Read JSON file
	Ftp.Read_JSON(cred_file)
	# Make Connection
	cred = Ftp.FTP_connect(Ftp.user_id, Ftp.password, Ftp.ip_addr, Ftp.port_num)
	# Upload the required file
	Ftp.FTP_upload(cred, file)