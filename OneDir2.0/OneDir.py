from flask import *
from forms import RegistrationForm
from flask_sqlalchemy import SQLAlchemy
from database import init_db, User, db
from sqlalchemy.exc import IntegrityError
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_admin import Admin

app = Flask(__name__)
app.config.from_object('config')
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'flask-session-insecure-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_ECHO = True
CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'this-is-not-random-but-it-should-be'

app.config.from_object('database')

app = init_db(app)
@app.before_first_request
def init():
    db.create_all()

@app.before_request
def before_request():
    g.db = db

@app.teardown_request
def close_connection(exception):
    pass

# engine = create_engine(SQLALCHEMY_DATABASE_URI)
# db.Session = sessionmaker(bind=engine)


@app.route("/")
def index():
    registration_form = RegistrationForm()
    return render_template("index.html",
                           site_form=registration_form)


@app.route("/show_entries.html", methods=['GET', 'POST'])
def show_entries():
    return render_template("show_entries.html")


@app.route('/login.html', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'Admin':
            return redirect(url_for('login'))
        else:
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/register.html', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm']:
            error = 'Passwords do not match'
        else:
            try:
                u = User(request.form['username'], request.form['password'])
                db.session.add(u)
                db.session.commit()
            finally:
                return redirect(url_for('login'))
    return render_template('register.html', error=error)


class User:
    def __init__(self, name, password):
        self.username = name
        self.password = password

if __name__ == '__main__':
    app.run()
