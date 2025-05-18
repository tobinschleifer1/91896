# workout_tracker/database_models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users Table'  # EXACT table name!

    ID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    Join_date = db.Column(db.String)
    instructions = db.Column(db.Text)
    description = db.Column(db.Text)
