from ma import ma
from models.user import UserModel

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)  # load -> 转换为python数据类型 dump -> 转换为json, 意味着password不会被展示
        dump_only = ("id", "activated")


