
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

db = SQLAlchemy()
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))

    def __init__(self, name, password):
        self.username = name
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

# engine = create_engine(SQLALCHEMY_DATABASE_URI)
# #db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False,bind=engine))
# Base = declarative_base()
# #Base.query = db_session.query_property()
# Session = sessionmaker(bind=engine)


def init_db(app):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    db.init_app(app)
    return app
