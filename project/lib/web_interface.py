from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from json_read import ReadConfig
import os
import sys
import json
 
app = Flask(__name__)

@app.route('/')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('homepage.html')
 
@app.route('/login', methods=['POST'])
def do_admin_login():
	if request.form['password'] == 'pes' and request.form['username'] == 'pes':
		session['logged_in'] = True
	else:
		flash('wrong password!')
	return home()

@app.route("/configure", methods=['GET', 'POST'])
def configure():
	cred_file = sys.path[0] + "/../config/config.json"
	RJSON = ReadConfig()
	RJSON.ReadJson(cred_file)
	print request.method
	if request.method == "POST":
		if request.form['action'] == 'General Settings':
			return render_template('gen_set.html', rjson = RJSON)
		elif request.form['action'] == 'FTP Settings':
			return render_template('ftp_set.html', rjson = RJSON)
		elif request.form['action'] == 'MODBUS Settings':
			return render_template('mod_set.html', rjson = RJSON)
		elif request.form['action'] == 'Log files':
			return render_template('log_files.html')
	else:
		pass

@app.route("/read_file", methods=['POST'])
def read_file():
	file_number = request.form['log_number']
	log_file_path = sys.path[0] + "/../Log_files/test" + str(file_number) + ".html"
	data_file_path = sys.path[0] + "/../Data/"
	with open(log_file_path, "r") as f:
		content = f.read()
	return render_template('show_file_content.html', content = content)

@app.route("/update_general", methods=['POST'])
def update_general():
	cred_file = sys.path[0] + "/../config/config.json"

	with open(cred_file, "r") as jsonFile:
		data = json.load(jsonFile)

	data["Output_Filename"] = request.form['Output_Filename']

	with open(cred_file, "w") as jsonFile:
		json.dump(data, jsonFile, indent=4)
	return home()

@app.route("/update_ftp", methods=['POST'])
def update_ftp():
	cred_file = sys.path[0] + "/../config/config.json"

	with open(cred_file, "r") as jsonFile:
		data = json.load(jsonFile)

	data["Ftp_interval"] = request.form['Ftp_interval']

	with open(cred_file, "w") as jsonFile:
		json.dump(data, jsonFile, indent=4)
	return home()

@app.route("/update_modbus", methods=['POST'])
def update_modbus():
	cred_file = sys.path[0] + "/../config/config.json"

	with open(cred_file, "r") as jsonFile:
		data = json.load(jsonFile)

	data["Modbus_interval"] = request.form['Modbus_interval']

	with open(cred_file, "w") as jsonFile:
		json.dump(data, jsonFile, indent=4)
	return home()

@app.route("/logout")
def logout():
	session['logged_in'] = False
	return home()

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True,host='0.0.0.0', port=4000)

