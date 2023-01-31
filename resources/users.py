from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists")
        user = UserModel(
            username=user_data["username"],
            password=sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first() # Tells us if the user exists
        if user and sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True) #fresh=True means that the token is only valid for 15 minutes
            refresh_token = create_refresh_token(identity=user.id) # This token is valid for 30 days
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        else:
            abort(401, message="Invalid credentials!")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True) # This means that the user must have a refresh token to access this route
    def post(self):
        current_user = get_jwt_identity() # Get the user id from the refresh token
        new_token = create_access_token(identity=current_user, fresh=False) # Create a new access token
        return {"access_token": new_token}, 200

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"] # jti is "JWT ID", a unique identifier for a JWT.
        BLOCKLIST.add(jti) # Add the jti to the blocklist
        return {"message": "Successfully logged out."}, 200

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200
