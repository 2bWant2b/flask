from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh, UserConfirm
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST
from ma import ma

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["PROPAGATE_EXCEPTIONS"] = True  # 让JWT返回异常信息
app.secret_key = "joke"
api = Api(app)

@app.before_request
def create_tables():
    db.create_all()

@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


jwt = JWTManager(app)  # not create endpoint /auth

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in BLACKLIST


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "message": "the token has been revoked",
        "error": "token_revoked"
    }), 401


api.add_resource(Store, "/store/<string:name>")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(StoreList, "/stores")
api.add_resource(UserRegister, "/register")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")
api.add_resource(UserConfirm, "/user_confirm/<int:user_id>")

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    ma.init_app(app)
    app.run(port=4999, debug=True)
