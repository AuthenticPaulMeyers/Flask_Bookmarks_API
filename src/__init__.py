from flask import Flask, redirect
import os 
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False
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
    
    # short url redirect route
    @app.get("/<string:short_url>")
    def get_short_url_redirect(short_url):
        bookmark=Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            # increment the visits count by 1
            bookmark.visits=bookmark.visits+1 
            db.session.commit()
        return redirect(bookmark.url)
    
    return app
