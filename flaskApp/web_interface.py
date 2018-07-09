# import Flask functions
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, escape
import redis 
import os
import sys
import glob
import json
import shutil
import subprocess

# Global Variables
active_user = ""
ip_type = None # dhcp or static
nw_type = None # Lan or GPRS
rtu_data = None # Rtu file content read
edit_en = False # Rtu file editing
rtu_names = [] # contains all rtu file names

ftp = {}
modbus = {}
network = {}
porta = {}
portb = {}

rtu_file_path = os.path.dirname(os.path.abspath(__file__))
path, file = os.path.split(rtu_file_path)
#print(path)
rtu_file_path = os.path.join(path, 'project', 'config')
#print("relative path", rtu_file_path)
data_file_path = os.path.join(path, 'project', 'Data')
log_file_path = os.path.join(path, 'project', 'Log_files')


# Activate Redis database for saving the login Password/username
r = redis.Redis(host='localhost', port=6379, db=0)
# Create Flask App
app = Flask(__name__)

# Route for Home page
@app.route('/')
def home():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		getRtuFileNames()
		readConfigFile()
		return render_template('welcome.html', active_user=active_user)

# Route for the Welcome page
@app.route('/welcome', methods=['GET','POST'])
def welcome():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		if request.method == 'POST':
			subprocess.call(['shutdown', '-r', '1'])
		return render_template('welcome.html', active_user=active_user) 

# Route for Ftp/Network Settings Page
@app.route('/ftp_settings', methods=['GET','POST'])
def ftp_settings():
	global ftp
	global modbus
	global network
	global porta
	global portb
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		global nw_type 
		global ip_type
		# if submit button is presses on ftp page
		if request.method == 'POST':
			nw_type = None
			ip_type = None
			# Read the required parameters for the ftp settings
			ip = request.form['ip']
			port = request.form['port']
			path = request.form['path']
			password = request.form['ftp_key']
			interval = request.form['interval']
			username = request.form['name_ftp']
			ftp['path'] = path
			ftp['password'] = password
			ftp['port'] = port
			ftp['server'] = ip
			ftp['name'] = username
			ftp['interval'] = interval
			createJsonConfig(ftp, network, modbus, porta, portb)
		return render_template('ftp_settings.html', active_user=active_user, nw_type=nw_type,\
								 ip_type=ip_type) 

# Route for selecting network type
@app.route('/nw_select', methods=['GET','POST'])
def nw_select():
	global ftp
	global modbus
	global network
	global porta
	global portb
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		global nw_type
		if request.method == 'POST':
			# check whether the network type selected is LAN/GPRS
			nw_type = request.form['nw_type']
			network['nw_type'] = nw_type
			createJsonConfig(ftp, network, modbus, porta, portb)
		return redirect(url_for('ftp_settings'))

# Route for selecting ip type
@app.route('/conn_type', methods=['GET','POST'])
def conn_type():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		global ip_type
		if request.method == 'POST':
			# check whether the IP type selected is DHCP/STATIC
			ip_type = request.form['ip_type']
		return redirect(url_for('ftp_settings'))

# Route for LAN Settings Page
@app.route('/lan_settings', methods=['GET','POST'])
def lan_settings():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		global nw_type
		global ip_type
		if request.method == 'POST':
			# Read the required parameters for the LAN settings
			nw_type = request.form['nw_type']
			ip_type = request.form['ip_type']
			ip = request.form['ip']
			subnet = request.form['subnet']
			gateway = request.form['gateway']
			dns = request.form['dns']
		return redirect(url_for('ftp_settings'))

# Route for GPRS Settings Page
@app.route('/gprs_settings', methods=['GET','POST'])
def gprs_settings():
	global ftp
	global modbus
	global network
	global porta
	global portb
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		if request.method == 'POST':
			# Read the required parameters for the GPRS settings
			apn_name = request.form['APN_name']
			apn_num = request.form['APN_num']
			username = request.form['gprs_user']
			password = request.form['pass']
			network['username'] = username
			network['password'] = password
			network['apn_name'] = apn_name
			network['apn_num'] = apn_num
			createJsonConfig(ftp, network, modbus, porta, portb)
			configureGprs(network)
		return redirect(url_for('ftp_settings'))

# Route for MODBUS Settings Page
@app.route('/modbus_settings', methods=['GET','POST'])
def modbus_settings():
	global ftp
	global modbus
	global network
	global porta
	global portb
	global rtu_names
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		if request.method == 'POST':
			# Read the required parameters for Modbus
			site = request.form['site']
			interval = request.form['interval']
			filename = request.form['filename']
			modbus['interval'] = interval
			modbus['output_filename'] = filename
			modbus['site_location'] = site
			createJsonConfig(ftp, network, modbus, porta, portb)
		return render_template('modbus_settings.html', active_user=active_user, rtu_names=rtu_names) 

# Route for COM PORT Settings Page
@app.route('/com_settings', methods=['GET','POST'])
def com_settings():
	global ftp
	global modbus
	global network
	global porta
	global portb
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		if request.method == 'POST':
			# Read the parameters for COM PORT A
			status_a = request.form['status_a']
			baudrate_a = request.form['baudrate_a']
			parity_a = request.form['parity_a']
			databits_a = request.form['databits_a']
			stopbits_a = request.form['stopbits_a']
			timeout_a = request.form['timeout_a']
			porta['baudrate'] = baudrate_a
			porta['parity'] = parity_a
			porta['databits'] = databits_a
			porta['stopbits'] = stopbits_a
			porta['timeout'] = timeout_a
			porta['status'] = status_a
			# Read the parameters for COM PORT B
			status_b = request.form['status_b']
			baudrate_b = request.form['baudrate_b']
			parity_b = request.form['parity_b']
			databits_b = request.form['databits_b']
			stopbits_b = request.form['stopbits_b']
			timeout_b = request.form['timeout_b']
			portb['baudrate'] = baudrate_b
			portb['parity'] = parity_b
			portb['databits'] = databits_b
			portb['stopbits'] = stopbits_b
			portb['timeout'] = timeout_b
			portb['status'] = status_b
			createJsonConfig(ftp, network, modbus, porta, portb)
		return render_template('modbus_settings.html', active_user=active_user, rtu_names=rtu_names) 

# Route for File mapping
@app.route('/file_mapping', methods=['GET','POST'])
def file_mapping():
	global ftp
	global modbus
	global network
	global porta
	global portb
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		if request.method == 'POST':
			files_portA = request.form.getlist('files_portA') 
			files_portB = request.form.getlist('files_portB') 
			porta['files'] = files_portA
			portb['files'] = files_portB
			createJsonConfig(ftp, network, modbus, porta, portb)
		return render_template('modbus_settings.html', active_user=active_user, rtu_names=rtu_names) 

# # Route for Zigbee Settings Page
# @app.route('/zigbee_settings')
# def zigbee_settings():
# 	if not 'username' in session:
# 		flash('You are Logged Out')
# 		return render_template('home.html')
# 	else:
# 		return render_template('zigbee_settings.html', active_user=active_user) 

# Route for General Settings Page (Date and time, Site location)
@app.route('/general_settings', methods=['GET','POST'])
def general_settings():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		if request.method == 'POST':
			# Read the date and time
			date = request.form['date']
			time = request.form['time']
			time = time + ":00"
			datetime = date + " " + time
			subprocess.call(['date', '-s', datetime])
			subprocess.call(['hwclock', '-w'])
		return render_template('general_settings.html', active_user=active_user) 

# Route for RTU file creation Page
@app.route('/rtu_create', methods=['GET','POST'])
def rtu_create():
	global rtu_names
	global rtu_data
	getRtuFileNames()
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		global edit_en
		# Take all the data from the user to create a new rtu file
		if request.method == 'POST':
			edit_en = False
			filename = request.form['filename']
			device = request.form['device']
			# endian = request.form['endian']
			retry = request.form['retry']
			status = request.form['status']
			start_addr = request.form.getlist('start_addr[]')
			datatype = request.form.getlist('datatype[]')
			length = request.form.getlist('length[]')
			endian = request.form.getlist('endian[]')
			fcode = request.form.getlist('func[]')
			# Create a JSON file from the data collected from the user
			createJsonRtu(filename, device, retry, status, endian, start_addr, length, datatype, fcode)
			return redirect(url_for('rtu_create'))
		return render_template('rtu_create.html', active_user=active_user, rtu_names=rtu_names,\
								rtu_data=rtu_data, edit_en=edit_en) 

# Route for RTU file edit Page
@app.route('/rtu_edit', methods=['GET','POST'])
def rtu_edit():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		global rtu_data
		global edit_en
		edit_en = False
		edit_file = ""
		# check if the editing is enabled for the RTU file
		if request.method == 'POST':
			edit_file = request.form['edit_btn']
			ext = edit_file.split('.')
			path = rtu_file_path + '/' + ext[0] + '.rtu'

			# check if the file needs to be deleted
			if ext[1] == 'del':
				os.remove(path)
			# check if the file needs to be edited
			if ext[1] == 'edit':
				edit_en = True
				rtu_data = getRtuData(path)
		return redirect(url_for('rtu_create'))

# Route for data files Page
@app.route('/data_files')
def data_files():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		# Get all the files in the Data directory
		SRC_DIR = data_file_path
		# delete the existing folder
		deleteFolder('static/Data')
		# Copy the Data directory
		shutil.copytree(SRC_DIR, 'static/Data', symlinks=True, ignore=None)	

		# get all files in the Data directory
		files = os.listdir('static/Data')
		data_files = []
		for loop in range(len(files)):
			ext = files[loop].split('.')
			# check all the csv files in the folder to display on the webpage
			if ext[1] == 'csv':
				data_files.append(files[loop])
		return render_template('data_files.html', active_user=active_user, files=data_files) 

# Route for Log files Page
@app.route('/log')
def log():
	if not 'username' in session:
		flash('You are Logged Out')
		return render_template('home.html')
	else:
		# Get all the files in the Log directory
		SRC_DIR = log_file_path
		# delete the existing folder
		deleteFolder('static/Log_files')
		# copy the Log directory
		shutil.copytree(SRC_DIR, 'static/Log_files', symlinks=True, ignore=None)

		# get all files in the Log directory
		files = os.listdir('static/Log_files')
		log_files = []
		for loop in range(len(files)):
			ext = files[loop].split('.')
			# check all the log files in the folder to display on the webpage
			if ext[1] == 'log':
				log_files.append(files[loop])
		return render_template('log.html', active_user=active_user, files=log_files) 

# delete the required folder
def deleteFolder(directory):
    if os.path.exists(directory):
        try:
        	# check if the files if existing or not
            if os.path.isdir(directory):
                # delete folder
                shutil.rmtree(directory, ignore_errors=True)
            else:
                # delete file
                os.remove(directory)
        except:
            print("Exception")
    else:
        print("not found ",directory)

# Route for Signup Page
@app.route('/signup', methods=['GET','POST'])
def signup():
	error = None
	if request.method == 'POST':
		# check for password match, raise a warning in case of an error
		if request.form['password'] != request.form['confirm_password']:
			error = 'Password does not match. Please try again.'
		else:
			# Save the details of the user if the details are correct
			session['logged_in'] = True
			username = request.form['username']
			password = request.form['password']
			r.set(username, password)
			error = 'Sign up complete...'
			return redirect(url_for('home'))
	return render_template('signup.html', error=error)

# Route for Signin Page
@app.route('/signin', methods=['GET', 'POST'])
def signin():
	global active_user
	error = None
	if request.method == 'POST':
		session['username'] = request.form['username']
		username = request.form['username']
		saved_pass = ""
		try:
			saved_pass = r.get(username)
		except:
			pass
		# check if user is authentic, Raise error if not
		if request.form['password'] != 'admin' or request.form['username'] != 'admin' :
			error = 'Invalid Credentials. Please try again.'
		else:
			active_user = username
			return redirect(url_for('home'))
	return render_template('signin.html', error=error)

# Route for SignOut Page
@app.route('/signout')
def signout():
	global active_user
	active_user = ""
	session.pop('username', None)
	return redirect(url_for('home'))

# Read the default Config file
def readConfigFile():
	global ftp
	global modbus
	global network
	global porta
	global portb
	file_path = rtu_file_path + '/' + 'config.json'
	if os.path.exists(file_path):
		with open(file_path) as data_file:    
			data = json.load(data_file)
		ftp = {'path':data["ftp"]["path"], 'password':data["ftp"]["password"],\
			   'port':data["ftp"]["port"], 'server':data["ftp"]["server"],\
			   'name':data["ftp"]["name"], 'interval':data["Ftp_interval"]}
		modbus = {'interval':data["Modbus_interval"], 'output_filename':data["Output_Filename"],\
				  'site_location':data["Site_location"]}
		network = {'username':data["GPRS"]["user"], 'password':data["GPRS"]["password"],\
				   'apn_name':data["GPRS"]["apn"], 'apn_num':data["GPRS"]["num"], 'nw_type':data["NW_type"]}
		porta = {'parity':data["serial"][0]["parity"], 'databits':data["serial"][0]["databits"],\
				 'stopbits':data["serial"][0]["stopbits"], 'timeout':data["serial"][0]["timeout"],\
				 'status':data["serial"][0]["status"], 'baudrate':data["serial"][0]["baudrate"],\
				 'files':data["serial"][0]["slaves"]}
		portb = {'parity':data["serial"][1]["parity"], 'databits':data["serial"][1]["databits"],\
				 'stopbits':data["serial"][1]["stopbits"], 'timeout':data["serial"][1]["timeout"],\
				 'status':data["serial"][1]["status"], 'baudrate':data["serial"][1]["baudrate"],\
				 'files':data["serial"][1]["slaves"]}
	else:
		ftp = {'path':'', 'password':'', 'port':'', 'server':'', 'name':'', 'interval':''}
		modbus = {'interval':'', 'output_filename':'', 'site_location':''}
		network = {'username':'', 'password':'', 'apn_name':'', 'apn_num':'', 'nw_type':''}
		porta = {'parity':'', 'databits':'', 'stopbits':'', 'timeout':'', 'status':'', 'baudrate':'', 'files':''}
		portb = {'parity':'', 'databits':'', 'stopbits':'', 'timeout':'', 'status':'', 'baudrate':'', 'files':''}	

def getRtuFileNames():
	global rtu_names
	# Get all the created rtu files to display on the edit page 
	saved_rtus = os.listdir(rtu_file_path)#glob.glob('../project/config/*.rtu')
	rtu_names = []
	for loop in range(len(saved_rtus)):
		ext = os.path.splitext(saved_rtus[loop])
		# Save all the file only with rtu extension and discard others
		if ext[1] == '.rtu':
			rtu_names.append(ext[0])

# Read the RTU file to display the content for editing
def getRtuData(path):
	with open(path) as data_file: 
		base = os.path.basename(path)
		filename = os.path.splitext(base)[0] 
		data = json.load(data_file)
		active = data["active"]
		# endian = data["endian_type"]
		description = data["Description"]
		device = data["device_address"]
		retry = data["retry_count"]
		addr_len = data["address"]
		all_addr = []
		length = []
		datatypes = []
		func = []
		endian = []
		for i in range(len(addr_len)):
			all_addr.append(data["address"][i]["addr"])
			length.append(data["address"][i]["length"])
			endian.append(data["address"][i]["endian_type"])
			func.append(data["address"][i]["func"])
			datatypes.append(data["address"][i]["data_type"])
		return (filename, active, endian, device, retry, all_addr, length, datatypes, func)

# create a JSON file from the data collected from the user from RTU creation page
def createJsonRtu(filename, device_addr, retry_count, active, endian, addrlist, lenlist, dtypelist, fcode):
	val = ""
	address_value = ""
	for loop in range(len(addrlist) - 1): # last value of the list is garbage (hidden stream)
		address_value += "\t\t{\n" + \
			"\t\t\t\t\"addr\": " + str(addrlist[loop]) + ",\n" + \
			"\t\t\t\t\"length\" : "+ str(lenlist[loop]) + ",\n" + \
			"\t\t\t\t\"func\" : "+ str(fcode[loop]) + ",\n" + \
			"\t\t\t\t\"endian_type\" : \""+ str(endian[loop]) + "\",\n" + \
			"\t\t\t\t\"data_type\": \"" + str(dtypelist[loop]) + "\"\n" + \
		"\t\t},\n"\

			
				 # "\t\"endian_type\": \"" + endian + "\",\n" +\
	address_value = address_value[:-2] # Remove \n and , from the end
	val = "{\n\t" + "\"address\": [\n" + address_value + "\n\t],\n" +\
	 "\t\"retry_count\": " + str(retry_count) + ",\n" +\
	 "\t\"device_address\": " + str(device_addr) + ",\n" +\
	 "\t\"active\": \"" + active + "\",\n" +\
	 "\t\"Description\": \"This is " + filename + ".rtu file.\"" + "\n" +\
	 "}"
	path = rtu_file_path
	rtu_file_name = path + '/' + filename + ".rtu"
	with open(rtu_file_name, 'w') as file:  # Use file to refer to the file object
		file.write(val) 

# create a JSON file from the data collected from the user from RTU creation page
def createJsonConfig(ftp, network, modbus, porta, portb):
	portA_files = ""
	portB_files = ""
	listA = porta['files']
	listB = portb['files']
	for loop in range(len(porta['files'])):
		portA_files += "\t\t\"" + listA[loop] + ".rtu\",\n"

	for loop in range(len(portb['files'])):
		portB_files += "\t\t\"" + listB[loop] + ".rtu\",\n"

	portA_files = portA_files[:-2] # Remove \n and , from the endian
	portB_files = portB_files[:-2] # Remove \n and , from the end
	val = "{\n"+\
  		  "\t\"GPRS\": {\n" + \
    	  "\t\"password\": \"" + network['password'] + "\",\n"+\
    	  "\t\"apn\": \"" + network['apn_name'] + "\",\n"+\
    	  "\t\"user\": \""+ network['username'] + "\",\n"+\
    	  "\t\"num\": \""+ network['apn_num'] + "\"\n"+\
  		  "\t},\n"+\
  		  "\t\"ftp\": {\n" + \
    	  "\t\"path\": \"" + ftp['path'] + "\",\n"+\
    	  "\t\"password\": \"" + ftp['password'] + "\",\n"+\
    	  "\t\"port\": \""+ ftp['port'] + "\",\n"+\
    	  "\t\"server\": \""+ ftp['server'] + "\",\n"+\
    	  "\t\"name\": \""+ ftp['name'] + "\"\n"+\
  		  "\t},\n"+\
  		  "\"product\": \"pes\",\n" + \
  	 	  "\"Ftp_interval\": \"" + ftp['interval'] + "\",\n"+\
  		  "\"Output_Filename\": \"" + modbus['output_filename'] + "\",\n"+\
  		  "\"Modbus_interval\": \"" + modbus['interval'] + "\",\n"+\
  		  "\"Site_location\": \"" + modbus['site_location'] + "\",\n"+\
  		  "\"releaseDate\": \"2017-09-15T00:00:00.000Z\",\n" + \
  		  "\"version\": 1,\n" + \
  		  "\"NW_type\": \"" + network['nw_type'] + "\",\n"+\
  		  "\"serial\": [\n" + \
  		  "\t{\n" + \
  		  "\t\"device\": \"/dev/ttyUSB0\",\n" + \
  		  "\t\"baudrate\": " + str(porta['baudrate']) + ",\n" + \
      	  "\t\"parity\": \"" + porta['parity'] + "\",\n" + \
      	  "\t\"databits\": " + str(porta['databits']) + ",\n" + \
      	  "\t\"stopbits\": " + str(porta['stopbits']) + ",\n" + \
      	  "\t\"timeout\": " + str(porta['timeout']) + ",\n" + \
      	  "\t\"slaves\": [\n" + \
      	  portA_files + "\n" + \
      	  "\t],\n" + \
      	  "\t\"status\": \"" + porta['status'] + "\"\n" + \
      	  "\t},\n" + \
      	  "\t{\n" + \
  		  "\t\"device\": \"/dev/ttyUSB1\",\n" + \
  		  "\t\"baudrate\": " + str(portb['baudrate']) + ",\n" + \
      	  "\t\"parity\": \"" + portb['parity'] + "\",\n" + \
      	  "\t\"databits\": " + str(portb['databits']) + ",\n" + \
      	  "\t\"stopbits\": " + str(portb['stopbits']) + ",\n" + \
      	  "\t\"timeout\": " + str(portb['timeout']) + ",\n" + \
      	  "\t\"slaves\": [\n" + \
      	  portB_files + "\n" + \
      	  "\t],\n" + \
      	  "\t\"status\": \"" + portb['status'] + "\"\n" + \
      	  "\t}\n" + \
      	  "],\n" + \
      	  "\"config_status\": false\n" + \
  		  "}\n"
	path = rtu_file_path
	config_file_name = path + '/' + "config.json"
	with open(config_file_name, 'w') as file:  # Use file to refer to the file object
		file.write(val) 

def configureGprs(network):
	# file1_path = rtu_file_path + '/' + 'testing_gprs1'
	# file2_path = rtu_file_path + '/' + 'testing_gprs2'
	file2_path = '/etc/ppp/peers/provider'
	file1_path = '/etc/ppp/chat-isp'

	if network['username'] == "":
  		test_name = '/0'
  	else:
  		test_name = network['username']

	data_file_chat = "\
	ABORT \"NO CARRIER\"\n\
	ABORT \"NO DIALTONE\"\n\
	ABORT \"ERROR\"\n\
	ABORT \"NO ANSWER\"\n\
	ABORT \"BUSY\"\n\
	\"\" \"atz\"\n\
	OK \"at&d0&c1\"\n\
	OK \"atdt8319000\"\n\
	\"CONNECT\"\n\
	ogin:\"{}\"\n\
	sword:\"{}\"\n".format(test_name, network['password'])

	with open(file1_path, 'w') as myfile:
  		myfile.write(data_file_chat)

  	data_file_provider = "\
  	user \"{}\"\n\
	connect \"/usr/sbin/chat -v -f /etc/chatscripts/pap -T {}\"\n\
	/dev/ttymxc1\n\
	115200\n\
	noipdefault\n\
	usepeerdns\n\
	defaultroute\n\
	persist\n\
	noauth\n".format(test_name, network['apn_num'])

	with open(file2_path, 'w') as myfile:
  		myfile.write(data_file_provider)


# main function calling
if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True, host='0.0.0.0')