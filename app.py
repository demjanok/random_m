import os

from flask import Flask, request, render_template, flash, redirect, url_for, abort, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_admin.form import FileUploadField
from PIL import Image
from werkzeug.utils import secure_filename

from helpers.generic import hash_passwd
from models import db, Article, Video, Users

# Constants here
UPLOAD_FOLDER = 'static/video/'

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_filepath = 'my_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, db_filepath)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all() # only for debug purpose


# Check access
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if 'user' not in session:
            return redirect(url_for('login'))
        return super().index()

class SecureModelView(ModelView):
    def is_accessible(self):
        return 'user' in session

class VideoAdminView(ModelView):
    form_excluded_columns = ('date_posted', 'video_present', 'url')

    poster_path = os.path.join(os.path.dirname(__file__), 'static', 'posters')
    form_extra_fields = {
        'poster': FileUploadField(
            'Poster',
            base_path=poster_path,
            namegen=lambda obj, file_data: secure_filename(obj.url + '.webp')
        )
    }

    def on_model_change(self, form, model, is_created):
        from helpers.generic import transliterate_to_snake

        # generate url
        if not model.url:
            model.url = transliterate_to_snake(model.title_original)

        # load poster
        poster_file = form.poster.data
        if poster_file:
            filename = secure_filename(model.url + ".webp")
            filepath = os.path.join('static', 'posters', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # convert and save
            img = Image.open(poster_file)
            img.convert("RGB").save(filepath, "WEBP", quality=85)



# Initialize
admin = Admin(app, name='Video Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(VideoAdminView(Video, db.session))
admin.add_view(SecureModelView(Article, db.session))
admin.add_view(SecureModelView(Users, db.session))


def save_poster(file, folder_name):
    if file and file.filename:
        filename = secure_filename('poster.webp')
        save_path = os.path.join(UPLOAD_FOLDER, folder_name)
        os.makedirs(save_path, exist_ok=True)
        full_path = os.path.join(save_path, filename)

        # Convert to webp
        image = Image.open(file.stream)
        image.save(full_path, format='WEBP', quality=85)


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


@app.route('/admin_custom', methods=['GET', 'POST'])
def admin():
    if 'user' not in session:
        flash("Login required")
        return redirect(url_for('login'))

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
            poster_file = request.files.get('poster')
            if poster_file:
                save_poster(poster_file, new_video.url)

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
                poster_file = request.files.get('poster')
                if poster_file and selected_video:
                    save_poster(poster_file, selected_video.url)

                message = '✅ Зміни збережено!'
        else:
            selected_id = request.form.get('video_id')
            selected_video = Video.query.get(selected_id)

    return render_template('admin.html', videos=videos, selected_video=selected_video, message=message)


@app.route('/video/<string:slug>')
def video_detail(slug):
    video = Video.query.filter_by(url=slug).first()
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
