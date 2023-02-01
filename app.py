import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST

import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.users import blp as UserBlueprint



def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True # Propagate any errors in flask to the main app
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app) # Connect SQLAlchemy to Flask App
    migrate = Migrate(app, db) # Connect Flask Migrate to Flask App. Has to be after db.init_app(app)

    api = Api(app) # Connect Flask Smorest extension to Flask App

    app.config["JWT_SECRET_KEY"] = "57876065647304421199322922514352063151"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader 
    def check_if_token_in_blocklist(jwt_header, jwt_payload): # This function is called when a token is revoked. Returns true if token is in blocklist
        return jwt_payload["jti"] in BLOCKLIST 

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload): # This function is called when a token is revoked. Lets user know what happened.
        return (jsonify({"description": "The token has been revoked", "error": "token_revoked"}), 401)

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload): # This function is called when a token is not fresh. Lets user know what happened.
        return (jsonify({"description": "The token is not fresh", "error": "fresh_token_required"}), 401)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload): # This function is called when a token is expired. Lets user know what happened.
        return (jsonify({"description": "The token has expired", "error": "token_expired"}), 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error): # This function is called when a token is invalid. Lets user know what happened.
        return (jsonify({"description": "Signature verification failed", "error": "invalid_token"}), 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error): # This function is called when a token is missing. Lets user know what happened.
        return (jsonify({"description": "Request does not contain an access token", "error": "authorization_required"}), 401)

    with app.app_context():
        db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
