from flask import Blueprint, request, jsonify
from src.database import Bookmark, db
from src.constants.http_status_code import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
import validators
from flask_jwt_extended import jwt_required, get_jwt_identity

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

@bookmarks.route("/", methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    current_user_id=get_jwt_identity()

    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')
    
        # validate the url
        if not validators.url(url):
            return jsonify({
                'Error': "URL is not valid"
        }), HTTP_400_BAD_REQUEST
    
        # check if the url already exist
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'Error': "URL already exist"
            }), HTTP_409_CONFLICT

        # save the data into the database
        bookmark=Bookmark(body=body, url=url, user_id=current_user_id)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED
    else:
        bookmarks=Bookmark.query.filter_by(user_id=current_user_id)
        data = []
        for bookmark in bookmarks:
            data.append(
                {
                    'id': bookmark.id,
                    'body': bookmark.body,
                    'url': bookmark.url,
                    'short_url': bookmark.short_url,
                    'visits': bookmark.visits,
                    'created_at': bookmark.created_at,
                    'updated_at': bookmark.updated_at
                }
            )
        return jsonify({'data': data}), HTTP_200_OK
