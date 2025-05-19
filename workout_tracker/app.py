# File: workout_tracker/app.py
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

        session['user_id'] = new_user.ID
        return redirect(url_for('home'))

    return render_template('create_account.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])

    try:
        from exercise_data import Exercise
        exercises = Exercise.query.all()
    except Exception:
        exercises = []

    try:
        from database_models import Exercise
        logs = (
            db.session.query(UserExercise, Exercise)
            .join(Exercise, UserExercise.exercise_id == Exercise.ID)
            .filter(UserExercise.user_id == user.ID)
            .order_by(UserExercise.date_completed.desc())
            .all()
        )
    except Exception:
        logs = []

    return render_template('home_page.html', user=user, exercises=exercises, logs=logs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/log_workout', methods=['GET', 'POST'])
def log_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        exercise_names = request.form.getlist('exercise_name[]')
        sets = request.form.getlist('sets[]')
        reps = request.form.getlist('reps[]')
        intensity = request.form['intensity']
        duration = request.form['duration']
        notes = request.form['notes']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

        from database_models import Exercise

        for i in range(len(exercise_names)):
            name = exercise_names[i]
            exercise = Exercise.query.filter_by(name=name).first()
            if not exercise:
                flash(f'Exercise not found: {name}')
                continue

            log = UserExercise(
                user_id=user_id,
                exercise_id=exercise.ID,
                duration=duration,
                intensity=intensity,
                date_completed=timestamp,
                calories_burned="0"
            )
            db.session.add(log)

        db.session.commit()
        flash('Workout logged successfully!')
        return redirect(url_for('home'))

    return render_template('log_workout.html')

if __name__ == '__main__':
    print("\n🔥 Flask is running at http://127.0.0.1:5000")
    app.run(debug=True)
