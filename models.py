import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from dotenv import load_dotenv
load_dotenv()


DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

database_path = 'postgresql://{}:{}@{}/{}'.format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)


"""
Students

"""


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String())
    email = db.Column(db.String(120), unique=True)
    gender = db.Column(db.String(120))
    school_name = db.Column(db.String())
    level = db.Column(db.String(120))
    rank = db.Column(db.String(120), default="0")
    completed_lessons = db.Column(
        db.ARRAY(db.String()), default=db.ARRAY(db.String))
    attempted_quizzes = db.Column(
        db.ARRAY(db.String()), default=db.ARRAY(db.String))

    def __init__(self, name, username, password, email, gender, school_name, level, rank, completed_lessons, attempted_quizzes):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.gender = gender
        self.school_name = school_name
        self.level = level
        self.rank = rank
        self.completed_lessons = completed_lessons
        self.attempted_quizzes = attempted_quizzes

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "gender": self.gender,
            "school_name": self.school_name,
            "level": self.level,
            "rank": self.rank,
            "completed_lessons": self.completed_lessons,
            "attempted_quizzes": self.attempted_quizzes,
        }

    def short(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "email": self.email,
        }

    def __repr__(self):
        return json.dumps(self.format())
