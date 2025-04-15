import os
from flask import Flask, request, render_template, flash, redirect, url_for, abort
from datetime import datetime

from helpers.generic import create_table
from models import db, Article, Video
import json



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_filepath = 'my_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, db_filepath)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def main():
    articles = Article.query.all()
    return render_template('main.html', articles=articles)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return 'Login successful!'
    return render_template('login.html')


#@app.route('/register', methods=['GET', 'POST'])
#def register():
#    if request.method == 'POST':
#        return 'Register successful!'
#    return render_template('register.html')


@app.route('/video/<string:slug>')
def video_detail(slug):
    from models import Video
    video = Video.query.filter_by(title_original=slug).first()
    if not video:
        abort(404)
    #genres = json.loads(video.genre) if video.genre else []
    return render_template('video.html', video=video)


@app.errorhandler(404)
def _404(e):
    return render_template('404.html')


if __name__ == '__main__':
    if not os.path.exists(db_filepath):
        with open(db_filepath, 'w') as f:
            create_table(db_filepath)

    app.run(host='0.0.0.0', port=8000, debug=True)
