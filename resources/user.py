from flask_restful import Resource
from flask import request, make_response, render_template
from models.user import UserModel
from schemas.user import UserSchema
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                get_jwt_identity,
                                jwt_required,
                                get_jwt)
from blacklist import BLACKLIST


USER_NOT_FOUND = "user not found."
USER_ALREADY_EXISTS = "the user {} already exists."
CREATED_SUCCESSFULLY = "user {} created successfully."
USER_DELETED = "user deleted."
INVALID_CREDENTIALS = "Invalid credentials."
USER_LOGGED_OUT = "User {} logged out successfully."
NOT_CONFIRMED_ERROR = "you have not confirm your email, please check your email {}."
USER_CONFIRMED = "User {} confirmed."

user_schema = UserSchema()

class UserRegister(Resource):
    def post(self):
        user_data = user_schema.load(request.get_json())

        if UserModel.find_by_username(user_data["username"]):
            return {"message": USER_ALREADY_EXISTS.format(user_data["username"])}, 400

        user = UserModel(**user_data)
        user.save_to_db()
        user.send_confirmation_email()

        return {"message": CREATED_SUCCESSFULLY.format(user_data["username"])}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        user_data = user_schema.load(request.get_json(), partial=("email",))
        user = UserModel.find_by_username(user_data["username"])

        if user and user.password == user_data["password"]:
            if user.activated:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}
        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)
        user_id = get_jwt_identity()
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access token": new_token}, 200


class UserConfirm(Resource):
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.activated = True
        user.save_to_db()
        headers = {"Content-Type": "text/html"}
        return make_response(render_template("confirmation_page.html", email=user.username), 200, headers)
