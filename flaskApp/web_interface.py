from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
# from json_read import ReadConfig
import redis 
import os
import sys
import json
import glob

active_user = ""
rtu_data = None
edit_en = False

r = redis.Redis(host='localhost', port=6379, db=0)
app = Flask(__name__)

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('home.html')
	else:
		return render_template('welcome.html', active_user=active_user)


@app.route('/welcome')
def welcome():
	return render_template('welcome.html', active_user=active_user) 


@app.route('/ftp_settings', methods=['GET','POST'])
def ftp_settings():
	if request.method == 'POST':
		ip = request.form['ip']
		port = request.form['port']
		path = request.form['path']
		password = request.form['password']
		interval = request.form['interval']
		username = request.form['username']
	return render_template('ftp_settings.html', active_user=active_user) 


@app.route('/gprs_settings', methods=['GET','POST'])
def com_settings():
	return render_template('ftp_settings.html', active_user=active_user) 


@app.route('/modbus_settings', methods=['GET','POST'])
def modbus_settings():
	if request.method == 'POST':
		interval = request.form['interval']
		filename = request.form['filename']
	return render_template('modbus_settings.html', active_user=active_user) 


@app.route('/com_settings', methods=['GET','POST'])
def com_settings():
	if request.method == 'POST':
		status_a = request.form['status_a']
		baudrate_a = request.form['baudrate_a']
		parity_a = request.form['parity_a']
		databits_a = request.form['databits_a']
		stopbits_a = request.form['stopbits_a']
		timeout_a = request.form['timeout_a']

		status_b = request.form['status_b']
		baudrate_b = request.form['baudrate_b']
		parity_b = request.form['parity_b']
		databits_b = request.form['databits_b']
		stopbits_b = request.form['stopbits_b']
		timeout_b = request.form['timeout_b']
	return render_template('modbus_settings.html', active_user=active_user) 


@app.route('/zigbee_settings')
def zigbee_settings():
	return render_template('zigbee_settings.html', active_user=active_user) 


@app.route('/general_settings')
def general_settings():
	return render_template('general_settings.html', active_user=active_user) 


@app.route('/rtu_create', methods=['GET','POST'])
def rtu_create():
	global edit_en
	saved_rtus = os.listdir('../project/config/')#glob.glob('../project/config/*.rtu')
	rtu_names = []
	for loop in range(len(saved_rtus)):
		ext = os.path.splitext(saved_rtus[loop])
		if ext[1] == '.rtu':
			rtu_names.append(ext[0])

	if request.method == 'POST':
		edit_en = False
		filename = request.form['filename']
		device = request.form['device']
		endian = request.form['endian']
		retry = request.form['retry']
		status = request.form['status']
		start_addr = request.form.getlist('start_addr[]')
		datatype = request.form.getlist('datatype[]')
		length = request.form.getlist('length[]')
		createJson(filename, device, retry, status, endian, start_addr, length, datatype)
		return redirect(url_for('rtu_create'))
	return render_template('rtu_create.html', active_user=active_user, rtu_names=rtu_names, rtu_data=rtu_data, \
							edit_en=edit_en) 


@app.route('/rtu_edit', methods=['GET','POST'])
def rtu_edit():
	global rtu_data
	global edit_en
	edit_en = False
	edit_file = ""
	if request.method == 'POST':
		edit_file = request.form['edit_btn']
		ext = edit_file.split('.')
		path = '../project/config/' + ext[0] + '.rtu'

		if ext[1] == 'del':
			os.remove(path)
		if ext[1] == 'edit':
			edit_en = True
			rtu_data = getRtuData(path)
	return redirect(url_for('rtu_create'))


@app.route('/data_files')
def data_files():
	files = os.listdir('static/Data')
	data_files = []
	for loop in range(len(files)):
		ext = files[loop].split('.')
		if ext[1] == 'csv':
			data_files.append(files[loop])
	return render_template('data_files.html', active_user=active_user, files=data_files) 


@app.route('/log')
def log():
	files = os.listdir('static/Log_files')
	log_files = []
	for loop in range(len(files)):
		ext = files[loop].split('.')
		if ext[1] == 'log':
			log_files.append(files[loop])
	return render_template('log.html', active_user=active_user, files=log_files) 


@app.route('/signup', methods=['GET','POST'])
def signup():
	session['logged_in'] = False
	error = None
	if request.method == 'POST':
		if request.form['password'] != request.form['confirm_password']:
			error = 'Password does not match. Please try again.'
		else:
			session['logged_in'] = True
			username = request.form['username']
			password = request.form['password']
			r.set(username, password)
			error = 'Sign up complete...'
			return redirect(url_for('home'))
	return render_template('signup.html', error=error)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
	global active_user
	session['logged_in'] = False
	error = None
	if request.method == 'POST':
		username = request.form['username']
		saved_pass = ""
		try:
			saved_pass = r.get(username)
		except:
			pass
		if request.form['password'] != saved_pass:
			error = 'Invalid Credentials. Please try again.'
		else:
			active_user = username
			session['logged_in'] = True

			return redirect(url_for('home'))
	return render_template('signin.html', error=error)

@app.route('/signout')
def signout():
	global active_user
	active_user = ""
	session['logged_in'] = False
	return redirect(url_for('home'))


def getRtuData(path):
	with open(path) as data_file: 
		base = os.path.basename(path)
		filename = os.path.splitext(base)[0][7:]  
		data = json.load(data_file)
		active = data["active"]
		endian = data["endian_type"]
		description = data["Description"]
		device = data["device_address"]
		retry = data["retry_count"]
		addr_len = data["address"]
		all_addr = []
		length = []
		datatypes = []
		for i in range(len(addr_len)):
			all_addr.append(data["address"][i]["addr"])
			length.append(data["address"][i]["length"])
			datatypes.append(data["address"][i]["data_type"])
		return (filename, active, endian, device, retry, all_addr, length, datatypes)


def createJson(filename, device_addr, retry_count, active, endian, addrlist, lenlist, dtypelist):
	val = ""
	address_value = ""
	for loop in range(len(addrlist) - 1): # last value of the list is garbage (hidden stream)
		address_value += "\t\t{\n" + \
			"\t\t\t\t\"addr\": " + str(addrlist[loop]) + ",\n" + \
			"\t\t\t\t\"length\" : "+ str(lenlist[loop]) + ",\n" + \
			"\t\t\t\t\"data_type\": \"" + str(dtypelist[loop]) + "\"\n" + \
		"\t\t},\n"\

	address_value = address_value[:-2]
	val = "{\n\t" + "\"address\": [\n" + address_value + "\n\t],\n" +\
	 "\t\"retry_count\": " + str(retry_count) + ",\n" +\
	 "\t\"device_address\": " + str(device_addr) + ",\n" +\
	 "\t\"active\": \"" + active + "\",\n" +\
	 "\t\"endian_type\": \"" + endian + "\",\n" +\
	 "\t\"Description\": \"This is linear_" + filename + ".rtu file.\"" + "\n" +\
	 "}"
	path = "../project/config/"
	rtu_file_name = path + "linear_" + filename + ".rtu"
	with open(rtu_file_name, 'w') as file:  # Use file to refer to the file object
		file.write(val) 

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True)



# @app.route('/login', methods=['POST'])
# def do_admin_login():
# 	if request.form['password'] == 'pes' and request.form['username'] == 'pes':
# 		session['logged_in'] = True
# 	else:
# 		flash('wrong password!')
# 	return home()
