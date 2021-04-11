from dynaconf import FlaskDynaconf
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()


def init_app(app):
    FlaskDynaconf(app)
    db.init_app(app)
    mail.init_app(app)
    JWTManager(app)
    CORS(app)
    Migrate(app, db)

    from app.models import User, Product, Category

    @app.shell_context_processor
    def content_processor():
        return dict(app=app, db=db, User=User, Product=Product, Category=Category)

