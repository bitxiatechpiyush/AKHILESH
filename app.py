from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from functools import wraps
from models import db, User
from bson import ObjectId
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

# MongoDB connection
app.config['MONGO_URI'] = 'mongodb://localhost:27017/drivertest_db'
db.init_app(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeated_password = request.form['repeated_password']
        user_type = request.form['user_type']

        if password != repeated_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        existing_user = User.find_one({'username': username})
        if existing_user:
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password, user_type=user_type)
        new_user.save()

        flash('Account created successfully', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_type'] = user['user_type']
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('dashboard.html', user=user)

@app.route('/g2_page', methods=['GET', 'POST'])
@login_required
def g2_page():
    if session['user_type'] != 'Driver':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    user = User.find_one({'_id': ObjectId(session['user_id'])})

    if request.method == 'POST':
        # Update user information
        user['firstname'] = request.form['firstname']
        user['lastname'] = request.form['lastname']
        user['license_no'] = request.form['license_no']
        user['age'] = int(request.form['age'])
        user['car_details']['make'] = request.form['car_make']
        user['car_details']['model'] = request.form['car_model']
        user['car_details']['year'] = int(request.form['car_year'])
        user['car_details']['platno'] = request.form['car_platno']

        User.update_one({'_id': ObjectId(session['user_id'])}, {'$set': user})
        flash('Information updated successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('g2_page.html', user=user)

@app.route('/g_page')
@login_required
def g_page():
    if session['user_type'] != 'Driver':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    user = User.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('g_page.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)