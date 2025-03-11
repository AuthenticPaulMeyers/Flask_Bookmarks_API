from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED
import validators
from src.database import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post("/register")
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    # validating password length
    if len(password) < 6:
        return jsonify({"Error": "Password is too short"}), HTTP_400_BAD_REQUEST
    
    # validating username length
    if len(username) < 3:
        return jsonify({"Error": "Username is too short"}), HTTP_400_BAD_REQUEST
    
    # validating username without spaces and if is alphanumneric
    if username.isalnum():
        return ({"Error": "Username should not be a number and should not have spaces"}), HTTP_400_BAD_REQUEST
    
    # validating email
    if validators.email(email):
        return jsonify({"Error": "Email is invalid"}), HTTP_400_BAD_REQUEST
    
    # check if the user email already exist to satisfy the unique constraint
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"Error": "Email already exit"}), HTTP_409_CONFLICT
    
    # check if the user username already exist to satisfy the unique constraint
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"Error": "Username already exit"}), HTTP_409_CONFLICT
    
    # generate a password hash before saving it into the datbase
    password_hash = generate_password_hash(password)

    # save the user in the database
    user=User(username=username, email=email, password=password_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created",
        'username': username, 'email': email
        }), HTTP_201_CREATED


@auth.get("/me")
def get_user():
    return ({'user': 'me'})