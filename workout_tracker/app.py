#cd C:\Users\tobyf\Desktop\91896\workout_tracker
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database_models import db, User, UserExercise
from werkzeug.security import generate_password_hash, check_password_hash

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'super_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../a.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.template_filter('datetimeformat')
def datetimeformat(value):
    return datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M')

@app.route('/')
def index():
    return redirect(url_for('login'))

# This route handles the login process for the user.
# If the method is POST, it checks the submitted username and password
# against the database. If valid, the user is logged in via session
# and redirected to the home page. If not, an error is flashed.
# On GET, it shows the login form.

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

        session['user_id'] = new_user.ID
        return redirect(url_for('profile_setup'))


    return render_template('create_account.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    workouts = (
        UserExercise.query
        .filter_by(user_id=user.ID)
        .order_by(UserExercise.date_completed.desc())
        .all()
    )

    # Group by date_completed to reduce repetition
    grouped = {}
    for w in workouts:
        key = w.date_completed
        grouped.setdefault(key, {"exercises": [], "meta": w})["exercises"].append(w.exercise)

    return render_template('home_page.html', user=user, grouped_workouts=grouped)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 🏋️‍♀️ This route allows a logged-in user to log a workout.
# It collects multiple exercises with weight, sets, and reps,
# as well as the workout's intensity, duration, and notes.
# The workout is saved to the database with a timestamp and
# the user is redirected back to the home page.

@app.route('/log_workout', methods=['GET', 'POST'])
def log_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        exercise_names = request.form.getlist('exercise_name[]')
        sets = request.form.getlist('sets[]')
        reps = request.form.getlist('reps[]')
        weights = request.form.getlist('weights[]')
        weight_units = request.form.getlist('weight_units[]')
        intensity = int(request.form['intensity'])
        duration = int(request.form['duration'])
        notes = request.form['notes']
        timestamp = int(datetime.now().timestamp())

        for i in range(len(exercise_names)):
            name = exercise_names[i]
            weight_str = f"{weights[i]} {weight_units[i]}"
            full_name = f"{name} ({weight_str})"

            total_calories = intensity * duration  # simplistic

            log = UserExercise(
                user_id=user_id,
                exercise=full_name,
                duration=duration,
                intensity=intensity,
                date_completed=timestamp,
                calories_burned=total_calories
            )
            db.session.add(log)

        db.session.commit()
        flash('Workout logged successfully!')
        return redirect(url_for('home'))

    return render_template('log_workout.html')
@app.route('/profile_setup', methods=['GET', 'POST'])
def profile_setup():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.current_weight = request.form.get('current_weight')
        user.goal_weight = request.form.get('goal_weight')
        # profile_picture = request.files['profile_picture'] (optional upload handling)
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('home'))

    return render_template('profile_setup.html', user=user)


if __name__ == '__main__':
    print("\n🔥 Flask is running at http://127.0.0.1:5000")
    app.run(debug=True)
