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
    current_weight = db.Column(db.Float)
    goal_weight = db.Column(db.Float)




class UserExercise(db.Model):
    __tablename__ = 'UserExercises'
    ID = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer)
    intensity = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    date_completed = db.Column(db.Integer)
    # one-to-many relationship
    exercises = db.relationship('WorkoutExercise', backref='parent', lazy=True)


class WorkoutExercise(db.Model):
    __tablename__ = 'WorkoutExercises'
    ID = db.Column(db.Integer, primary_key=True)
    user_exercise_id = db.Column(db.Integer, db.ForeignKey('UserExercises.ID'))
    name = db.Column(db.String)
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    unit = db.Column(db.String)



class Exercise(db.Model):
    __tablename__ = 'Exercises Table'
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String)
    difficulty_level = db.Column(db.String)
