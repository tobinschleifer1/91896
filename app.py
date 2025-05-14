# File: workout_tracker/app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from workout_tracker.database_models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # TODO: Replace in production

# DB setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../a.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.ID
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')

    return render_template('login_page.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return redirect(url_for('create_account'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('create_account'))

        existing_user = User.query.filter_by(Username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('create_account'))

        hashed_password = generate_password_hash(password)
        new_user = User(Username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.ID  # ✅ store login session
        return redirect(url_for('home'))  # ✅ go to homepage

    return render_template('create_account.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # Import Exercise model here if you have it
    from workout_tracker.exercise_data import Exercise
    exercises = Exercise.query.all()

    return render_template('home_page.html', user=user, exercises=exercises)

