from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mysecret')  # Use environment variable for secret key

# Users data
users = {
    "admin": "admin123",
    "user1": "password1",
    "user2": "password2"
}

# Logging setup
log_formatter = logging.Formatter('%(asctime)s - %(message)s')
log_file = 'honeypot_web.log'

file_handler = RotatingFileHandler(log_file, maxBytes=2000, backupCount=5)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Route
@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('login'))

    # Validate user credentials
    if username in users and users[username] == password:
        session['username'] = username
        app.logger.info(f'Successful login for user: {username}')
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        app.logger.warning(f'Failed login attempt for user: {username}')
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if 'username' in session:
        app.logger.info(f'User {session["username"]} logged out.')
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f'Page not found: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f'Server error: {request.url}')
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)