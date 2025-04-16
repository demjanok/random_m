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


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    from models import Video

    videos = Video.query.all()
    selected_video = None
    message = ''

    if request.method == 'POST':
        if 'create' in request.form:
            # Створити новий запис
            new_video = Video(
                title=request.form.get('title'),
                title_original=request.form.get('title_original'),
                year=int(request.form.get('year') or 0),
                genre=request.form.get('genre'),
                imdb_url=request.form.get('imdb_url'),
                imdb_rating=request.form.get('imdb_rating'),
                description=request.form.get('description')
            )
            db.session.add(new_video)
            db.session.commit()
            message = '✅ Нове відео створено!'
            videos = Video.query.all()  # оновити список
        elif 'save' in request.form:
            # Зберегти існуюче
            selected_id = request.form.get('video_id')
            selected_video = Video.query.get(selected_id)
            if selected_video:
                selected_video.title = request.form.get('title')
                selected_video.title_original = request.form.get('title_original')
                selected_video.year = int(request.form.get('year') or 0)
                selected_video.genre = request.form.get('genre')
                selected_video.imdb_url = request.form.get('imdb_url')
                selected_video.imdb_rating = request.form.get('imdb_rating')
                selected_video.description = request.form.get('description')
                db.session.commit()
                message = '✅ Зміни збережено!'
        else:
            selected_id = request.form.get('video_id')
            selected_video = Video.query.get(selected_id)

    return render_template('admin.html', videos=videos, selected_video=selected_video, message=message)



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
