from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'MSG_the_best'

    app.config.from_pyfile('../config.py')
    app.config['SQLALCHEMY_ECHO'] = False

    database = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], encoding = 'utf-8')
    app.database = database
    db.init_app(app)
    migrate.init_app(app,db)

    from . import models
    from .views import main_views
    app.register_blueprint(main_views.bp)

    return app

