import os

from flask import Flask, request, render_template, flash, redirect, url_for, abort, session

from admin import init_admin
from helpers.generic import hash_passwd
from models import db, Article, Video, Users

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
db_filepath = 'my_database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, db_filepath)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all() # only for debug purpose
    init_admin(app, db)

    if not Users.query.filter_by(user='admin').first():
        admin_user = Users(
            user='admin',
            passwd=hash_passwd('admin'),
            email='admin@example.com',
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()


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
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid login or password!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/video/<string:slug>')
def video_detail(slug):
    video = Video.query.filter_by(url=slug).first()
    if not video:
        abort(404)
    return render_template('video.html', video=video)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You are logged out')
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def _404(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
