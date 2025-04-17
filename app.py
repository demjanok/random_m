import os
from flask import Flask, request, render_template, flash, redirect, url_for, abort, session

from helpers.generic import hash_passwd
from models import db, Article, Video

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_filepath = 'my_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, db_filepath)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all() # only for debug purpose


UPLOAD_FOLDER = os.path.join(app.static_folder, 'video')
ALLOWED_EXTENSIONS = {'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    articles = Article.query.all()
    return render_template('main.html', articles=articles)


@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import Users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = hash_passwd(password)

        user = Users.query.filter_by(user=username, passwd=hashed).first()

        if user:
            session['user'] = user.user
            flash('Login successful!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Invalid login or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session:
        flash("Login required")
        return redirect(url_for('login'))

    from models import Video

    videos = Video.query.all()
    selected_video = None
    message = ''

    if request.method == 'POST':
        if 'create' in request.form:
            # New video
            title_original = request.form.get('title_original')

            new_video = Video(
                title=request.form.get('title'),
                title_original=title_original,
                year=int(request.form.get('year') or 0),
                genre=request.form.get('genre'),
                imdb_url=request.form.get('imdb_url'),
                imdb_rating=request.form.get('imdb_rating'),
                description=request.form.get('description')
            )
            db.session.add(new_video)
            db.session.commit()

            # 🖼️ Save logo if uploaded
            logo_file = request.files.get('logo')
            if logo_file and allowed_file(logo_file.filename):
                folder_path = os.path.join(UPLOAD_FOLDER, title_original)
                os.makedirs(folder_path, exist_ok=True)
                logo_path = os.path.join(folder_path, 'poster.png')
                logo_file.save(logo_path)

            message = '✅ Нове відео створено!'
            videos = Video.query.all()

        elif 'save' in request.form:
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

                # 🖼️ Save logo if uploaded
                logo_file = request.files.get('logo')
                if logo_file and allowed_file(logo_file.filename):
                    folder_path = os.path.join(UPLOAD_FOLDER, selected_video.title_original)
                    os.makedirs(folder_path, exist_ok=True)
                    logo_path = os.path.join(folder_path, 'poster.png')
                    logo_file.save(logo_path)
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


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You are logged out')
    return redirect(url_for('login'))


@app.errorhandler(404)
def _404(e):
    return render_template('404.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
