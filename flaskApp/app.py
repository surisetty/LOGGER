from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
import redis 
import os

r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)

@app.route('/')
def basic():
	session['logged_in'] = False
	return render_template('basic.html')

@app.route('/home')
def home():
	if not session.get('logged_in'):
		return render_template('login.html')
	else:
		return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	session['logged_in'] = False
	error = None
	if request.method == 'POST':
		if request.form['password'] != request.form['con_password']:
			error = 'Password does not match. Please try again.'
		else:
			username = request.form['username']
			password = request.form['password']
			r.set(username, password)
			error = 'Sign up complete, Please Login'
			return redirect(url_for('home'))
	return render_template('signup.html', error=error)
 
 
@app.route('/login', methods=['GET', 'POST'])
def login():
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
			session['logged_in'] = True
			return redirect(url_for('home'))
	return render_template('login.html', error=error)

	
if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run(debug=True)