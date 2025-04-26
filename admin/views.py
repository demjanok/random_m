import os

from flask import session, redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField

from werkzeug.utils import secure_filename
from PIL import Image

from models import Video, Article, Users
from helpers.generic import transliterate_to_snake


# 🔒 Index view with session check
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if 'user' not in session:
            return redirect(url_for('login'))

        video_count = Video.query.count()
        user_count = Users.query.count()
        article_count = Article.query.count()
        latest_videos = Video.query.order_by(Video.date_posted.desc()).limit(5).all()

        return super().render('admin/index.html',
                              video_count=video_count,
                              user_count=user_count,
                              article_count=article_count,
                              latest_videos=latest_videos)


# 🔒 Base model view with session check
class SecureModelView(ModelView):
    def is_accessible(self):
        return 'user' in session


# 🎥 Custom Video admin
class VideoAdminView(SecureModelView):
    form_excluded_columns = ('date_posted', 'video_present', 'url')
    #form_columns = ('id', 'title', 'title_original', 'year', 'genre', 'date_posted', 'video_present')

    form_widget_args = {
        'url': {'readonly': True},
        'date_posted': {'readonly': True},
        'video_present': {'readonly': True}
    }

    poster_path = os.path.join('static', 'posters')
    form_extra_fields = {
        'poster': FileUploadField(
            'Poster',
            base_path=poster_path,
            namegen=lambda obj, file_data: secure_filename(obj.url + '.webp')
        )
    }

    def on_model_change(self, form, model, is_created):
        # generate URL from original title
        if not model.url:
            model.url = transliterate_to_snake(model.title_original)

        # 🖼️ Save poster if uploaded
        poster_file = form.poster.data
        if poster_file:
            filename = secure_filename(model.url + ".webp")
            filepath = os.path.join(self.poster_path, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            img = Image.open(poster_file)
            img.convert("RGB").save(filepath, "WEBP", quality=85)
            model.video_present = True


# 🛠️ Admin setup
def init_admin(app, db):
    admin = Admin(app, name='Video Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())
    admin.add_view(VideoAdminView(Video, db.session))
    admin.add_view(SecureModelView(Article, db.session))
    admin.add_view(SecureModelView(Users, db.session))
