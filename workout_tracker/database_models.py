from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users Table'
    ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    Join_date = db.Column(db.String)
    instructions = db.Column(db.Text)
    description = db.Column(db.Text)
    bench_goal = db.Column(db.Integer)
    squat_goal = db.Column(db.Integer)
    deadlift_goal = db.Column(db.Integer)
    bench_current = db.Column(db.Integer)
    squat_current = db.Column(db.Integer)
    deadlift_current = db.Column(db.Integer)
    recovery_phrase = db.Column(db.Text)
    weight_updated = db.Column(db.String)



class UserExercise(db.Model):
    __tablename__ = 'UserExercises'
    ID = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    exercise = db.Column(db.String, nullable=False)  # 🔄 was exercise_id
    duration = db.Column(db.Integer)
    intensity = db.Column(db.Integer)
    date_completed = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)  # Add this line inside the class



class Exercise(db.Model):
    __tablename__ = 'Exercises Table'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String)
    difficulty_level = db.Column(db.String)
