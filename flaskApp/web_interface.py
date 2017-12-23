from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
# from json_read import ReadConfig
import redis 
import os
import sys
import json

active_user = ""

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

@app.route('/rtu_create', methods=['GET','POST'])
def rtu_create():
	if request.method == 'POST':
		filename = request.form['filename']
		device = request.form['device']
		endian = request.form['endian']
		retry = request.form['retry']
		status = request.form['status']
		start_addr = request.form.getlist('start_addr[]')
		datatype = request.form.getlist('datatype[]')
		length = request.form.getlist('length[]')
		createJson(filename, device, retry, status, endian, start_addr, length, datatype)
	return render_template('rtu_create.html', active_user=active_user) 

@app.route('/modbus_settings')
def modbus_settings():
	return render_template('modbus_settings.html', active_user=active_user) 

@app.route('/data_files')
def data_files():
	return render_template('data_files.html', active_user=active_user) 

@app.route('/ftp_settings')
def ftp_settings():
	return render_template('ftp_settings.html', active_user=active_user) 

@app.route('/log')
def log():
	return render_template('log.html', active_user=active_user) 

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

# @app.route('/login', methods=['POST'])
# def do_admin_login():
# 	if request.form['password'] == 'pes' and request.form['username'] == 'pes':
# 		session['logged_in'] = True
# 	else:
# 		flash('wrong password!')
# 	return home()

# @app.route("/configure", methods=['GET', 'POST'])
# def configure():
# 	cred_file = sys.path[0] + "/../config/config.json"
# 	RJSON = ReadConfig()
# 	RJSON.ReadJson(cred_file)
# 	print request.method
# 	if request.method == "POST":
# 		if request.form['action'] == 'General Settings':
# 			return render_template('gen_set.html', rjson = RJSON)
# 		elif request.form['action'] == 'FTP Settings':
# 			return render_template('ftp_set.html', rjson = RJSON)
# 		elif request.form['action'] == 'MODBUS Settings':
# 			return render_template('mod_set.html', rjson = RJSON)
# 		elif request.form['action'] == 'Log files':
# 			return render_template('log_files.html')
# 	else:
# 		pass

# @app.route("/read_file", methods=['POST'])
# def read_file():
# 	file_number = request.form['log_number']
# 	log_file_path = sys.path[0] + "/../Log_files/test" + str(file_number) + ".html"
# 	data_file_path = sys.path[0] + "/../Data/"
# 	with open(log_file_path, "r") as f:
# 		content = f.read()
# 	return render_template('show_file_content.html', content = content)

# @app.route("/update_general", methods=['POST'])
# def update_general():
# 	cred_file = sys.path[0] + "/../config/config.json"

# 	with open(cred_file, "r") as jsonFile:
# 		data = json.load(jsonFile)

# 	data["Output_Filename"] = request.form['Output_Filename']

# 	with open(cred_file, "w") as jsonFile:
# 		json.dump(data, jsonFile, indent=4)
# 	return home()

# @app.route("/update_ftp", methods=['POST'])
# def update_ftp():
# 	cred_file = sys.path[0] + "/../config/config.json"

# 	with open(cred_file, "r") as jsonFile:
# 		data = json.load(jsonFile)

# 	data["Ftp_interval"] = request.form['Ftp_interval']

# 	with open(cred_file, "w") as jsonFile:
# 		json.dump(data, jsonFile, indent=4)
# 	return home()

# @app.route("/update_modbus", methods=['POST'])
# def update_modbus():
# 	cred_file = sys.path[0] + "/../config/config.json"

# 	with open(cred_file, "r") as jsonFile:
# 		data = json.load(jsonFile)

# 	data["Modbus_interval"] = request.form['Modbus_interval']

# 	with open(cred_file, "w") as jsonFile:
# 		json.dump(data, jsonFile, indent=4)
# 	return home()

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True)

