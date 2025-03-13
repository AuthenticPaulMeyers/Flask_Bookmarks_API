from flask import Flask, redirect, jsonify
import os 
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_405_METHOD_NOT_ALLOWED
from flasgger import swag_from, Swagger
from src.config.swagger import swagger_config, template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SWAGGER={
                'title': "Bookmarks API",
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    # initialise the database with the app
    db.app=app
    db.init_app(app)

    # initialise jwt for access tokens to the app
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, template=template, config=swagger_config)
    
    # short url redirect route
    @app.get("/<string:short_url>")
    @swag_from('./docs/short_url.yaml')
    def get_short_url_redirect(short_url):
        bookmark=Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            # increment the visits count by 1
            bookmark.visits=bookmark.visits+1 
            db.session.commit()
        return redirect(bookmark.url)
    
    # handle errors here
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': "Not found!"}), HTTP_404_NOT_FOUND
    
    # internal server error
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': "Something went wrong!"}), HTTP_500_INTERNAL_SERVER_ERROR
    
    # routing error - method not allowed error
    @app.errorhandler(HTTP_405_METHOD_NOT_ALLOWED)
    def handle_405(e):
        return jsonify({'error': "Wrong address. Make sure you type your URL correctly!"}), HTTP_405_METHOD_NOT_ALLOWED
    
    return app
