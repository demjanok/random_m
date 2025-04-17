from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import event

from helpers.generic import transliterate_to_snake

db = SQLAlchemy()


class Article(db.Model):
    __tablename__ = 'Article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"Article('{self.title}', '{self.date_posted}')"


class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    title_original = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer)
    genre = db.Column(db.Text, default='[]')
    imdb_url = db.Column(db.String(120), nullable=False)
    imdb_rating = db.Column(db.String(3), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(150), nullable=False)

# Automatic generate url from title
@event.listens_for(Video, 'before_insert')
def generate_url(mapper, connection, target):
    if not target.url:
        target.url = transliterate_to_snake(target.title)

# Update url when title
@event.listens_for(Video, 'before_update')
def update_url(mapper, connection, target):
    target.url = transliterate_to_snake(target.title)


class Users(db.Model):
    __tablename__ = 'users'
    user = db.Column(db.String(20), primary_key=True)
    passwd = db.Column(db.String(128))
