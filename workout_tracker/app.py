# cd C:\Users\tobyf\Desktop\91896\workout_tracker
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
        recovery_phrase = request.form['recovery_phrase']

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
        new_user = User(Username=username, password_hash=hashed_password, recovery_phrase=recovery_phrase)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.ID
        return redirect(url_for('profile_settings'))

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

    grouped = {}
    for w in workouts:
        key = w.date_completed
        grouped.setdefault(key, {"exercises": [], "meta": w})["exercises"].append(w.exercise)

    from database_models import WorkoutExercise

    logs = (
        UserExercise.query
        .filter_by(user_id=user.ID)
        .order_by(UserExercise.date_completed.desc())
        .all()
    )

    grouped = {}
    for log in logs:
        grouped[log.date_completed] = {
            "meta": log,
            "exercises": WorkoutExercise.query.filter_by(user_exercise_id=log.ID).all()
        }


    return render_template('home_page.html', user=user, grouped_workouts=grouped)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/log_workout', methods=['GET', 'POST'])
def log_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            user_id = session['user_id']
            exercise_names = request.form.getlist('exercise_name[]')
            sets = list(map(int, request.form.getlist('sets[]')))
            reps = list(map(int, request.form.getlist('reps[]')))
            weights = list(map(float, request.form.getlist('weights[]')))
            weight_units = request.form.getlist('weight_units[]')
            intensity = int(request.form['intensity'])
            duration = int(request.form['duration'])
            notes = request.form['notes']
            timestamp = int(datetime.now().timestamp())

            if not (1 <= duration <= 300):
                flash("Workout duration must be between 1 and 300 minutes.")
                return redirect(url_for('log_workout'))

            if not all(1 <= w <= 500 for w in weights):
                flash("Each weight must be between 1 and 500.")
                return redirect(url_for('log_workout'))

            from database_models import WorkoutExercise  # 👈 Import here to avoid circular issues

            log = UserExercise(
                user_id=user_id,
                duration=duration,
                intensity=intensity,
                date_completed=timestamp,
                calories_burned=intensity * duration,
                notes=notes
            )
            db.session.add(log)
            db.session.flush()  # get log.ID

            for i in range(len(exercise_names)):
                exercise = WorkoutExercise(
                    user_exercise_id=log.ID,
                    name=exercise_names[i],
                    sets=sets[i],
                    reps=reps[i],
                    weight=weights[i],
                    unit=weight_units[i]
                )
                db.session.add(exercise)

            db.session.commit()
            flash("Workout logged successfully!")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"Error: {str(e)}")
            return redirect(url_for('log_workout'))

    return render_template('log_workout.html')



@app.route('/profile_settings', methods=['GET', 'POST'])
def profile_settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        try:
            # Weight goals
            if request.form.get('current_weight'):
                user.current_weight = float(request.form['current_weight'])
            if request.form.get('goal_weight'):
                user.goal_weight = float(request.form['goal_weight'])
            user.weight_updated = datetime.now().strftime('%Y-%m-%d %H:%M')

            # Lift goals
            if request.form.get('bench_current'):
                user.bench_current = int(request.form['bench_current'])
            if request.form.get('bench_goal'):
                user.bench_goal = int(request.form['bench_goal'])

            if request.form.get('squat_current'):
                user.squat_current = int(request.form['squat_current'])
            if request.form.get('squat_goal'):
                user.squat_goal = int(request.form['squat_goal'])

            if request.form.get('deadlift_current'):
                user.deadlift_current = int(request.form['deadlift_current'])
            if request.form.get('deadlift_goal'):
                user.deadlift_goal = int(request.form['deadlift_goal'])

            # Password update
            new_pass = request.form.get('new_password')
            confirm_pass = request.form.get('confirm_password')
            if new_pass or confirm_pass:
                if new_pass != confirm_pass:
                    flash("Passwords do not match.")
                    return redirect(url_for('profile_settings'))
                if len(new_pass) < 6:
                    flash("Password must be at least 6 characters.")
                    return redirect(url_for('profile_settings'))
                user.password_hash = generate_password_hash(new_pass)

            db.session.commit()
            flash("Profile updated successfully!")

        except Exception as e:
            flash(f"Error updating profile: {str(e)}")

        return redirect(url_for('home'))

    return render_template('profile_settings.html', user=user)





@app.route('/profile_setup', methods=['GET', 'POST'])
def profile_setup():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        try:
            current = float(request.form.get('current_weight'))
            goal = float(request.form.get('goal_weight'))

            if not (0 < current <= 300 and 0 < goal <= 300):
                flash('Weight must be between 0 and 300 kg.')
                return redirect(url_for('profile_setup'))

            user.current_weight = current
            user.goal_weight = goal
            user.weight_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
            db.session.commit()
            flash("Profile updated successfully!")
            return redirect(url_for('home'))

        except ValueError:
            flash('Invalid number input.')
            return redirect(url_for('profile_setup'))

    return render_template('profile_setup.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    try:
        user.current_weight = float(request.form['current_weight'])
        user.goal_weight = float(request.form['goal_weight'])

        if not (0 < user.current_weight <= 300 and 0 < user.goal_weight <= 300):
            flash('Weight must be between 0 and 300 kg.')
            return redirect(url_for('home'))

        user.weight_updated = datetime.now().strftime('%Y-%m-%d %H:%M')
        db.session.commit()
        flash("Profile updated successfully!")
    except ValueError:
        flash("Invalid weight input.")
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("\n🔥 Flask is running at http://127.0.0.1:5000")
    app.run(debug=True)
