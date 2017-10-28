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
		config_str = "<a href='/configure'>Configure</a>"
		help_str = "<a href='/help'>help</a>"
		logout_str = "<a href='/logout'>Logout</a>"
		line_break = "</br>"
		login_success_string = "<b>Settings</b>" + line_break + line_break + config_str + line_break + help_str + \
								line_break + line_break + line_break + line_break + logout_str
		return login_success_string
 
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
	return render_template('configure.html', rjson = RJSON)

@app.route("/update", methods=['POST'])
def update():
	cred_file = sys.path[0] + "/../config/config.json"

	with open(cred_file, "r") as jsonFile:
		data = json.load(jsonFile)

	data["Output_Filename"] = request.form['Output_Filename']

	with open(cred_file, "w") as jsonFile:
		json.dump(data, jsonFile, indent=4)
	return home()

@app.route("/help")
def help():
	return render_template('help.html')
 
@app.route("/logout")
def logout():
	session['logged_in'] = False
	return home()

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True,host='0.0.0.0', port=4000)

