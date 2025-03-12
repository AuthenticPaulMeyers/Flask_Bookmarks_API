from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants.http_status_code import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
import validators
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

# user register route
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
    if not username.isalnum() or " " in username:
        return jsonify({"Error": "Username should not be alphanumeric"}), HTTP_400_BAD_REQUEST
    
    # validating email
    if not validators.email(email):
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
        "user":{
            'username': username, 'email': email
        }
        }), HTTP_201_CREATED

# user login route
@auth.post("/login")
def login():
    email = request.json.get("email","")
    password = request.json.get("password","")

    # get the user from the database using the email
    user=User.query.filter_by(email=email).first()

    if user:
        # check password hash
        is_password_checked = check_password_hash(user.password, password)

        if is_password_checked:
            refresh=create_refresh_token(identity=user.id)
            access=create_access_token(identity=user.id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }}), HTTP_200_OK
        
    # if the user is not found
    return jsonify({"Error": 'Wrong username or password'}), HTTP_404_NOT_FOUND

        


@auth.get("/me")
def get_user():
    return ({'user': 'me'})