from datetime import datetime
import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, Column

from helpers.generic import transliterate_to_snake

db = SQLAlchemy()


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Article('{self.title}', '{self.date_posted}')"


class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    title_original = db.Column(db.String(120))
    country = db.Column(db.Text)
    year = db.Column(db.Integer)
    lists = db.Column(db.Integer)
    genre = db.Column(db.Text)
    director = db.Column(db.String(120))
    actors = db.Column(db.Text)
    imdb_url = db.Column(db.String(120))
    imdb_rating = db.Column(db.String(3))
    description = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    video_present = db.Column(db.Boolean, nullable=False, default=False)
    PEGI = db.Column(db.Integer)
    url = db.Column(db.String(150)) # event will create this row automatically


# Automatic generate url from title
@event.listens_for(Video, 'before_insert')
def generate_url(mapper, connection, target):
    if not target.url:
        target.url = transliterate_to_snake(target.title_original)

# Update url when title
@event.listens_for(Video, 'before_update')
def update_url(mapper, connection, target):
    target.url = transliterate_to_snake(target.title_original)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = db.Column(db.String(20), unique=True)
    passwd = db.Column(db.String(128))
    email = db.Column(db.String(254), unique=True)
    role = db.Column(db.String(20), default='user')
    date_of_registration = db.Column(db.DateTime, default=datetime.now)


