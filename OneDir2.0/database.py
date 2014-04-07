
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapper
import os
from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


db = SQLAlchemy()
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)

metadata = MetaData()

user = Table('user', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50), unique=True),
            Column('password', String(12))
        )

class User(object):
    def __init__(self, name, password):
        self.username = name
        self.password = password

mapper(User, user)

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
