from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.item import ItemModel
from schemas.item import ItemSchema


ITEM_NOT_FOUND = "item {} not found."
NAME_ALREADY_EXISTS = "the item {} already exists."
ERROR_INSERTING = "An error occurred while inserting the item {}."
ITEM_DELETED = "item {} deleted."

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

class Item(Resource):
    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": ITEM_NOT_FOUND.format(name)}, 404

    @jwt_required(refresh=True)  # TODO 无效果
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS.format(name)}, 400

        item_json = request.get_json()
        item_json["name"] = name
        item_data = item_schema.load(item_json)
        item = ItemModel(**item_data)

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING.format(name)}, 500  # internal server error

        return item_schema.dump(item), 201  # CREATED

    @jwt_required()
    def delete(self, name):
        claims = get_jwt()
        if not claims["is_admin"]:
            return {"message": "Admin privilege required"}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": ITEM_DELETED.format(name)}

        return {"message": ITEM_NOT_FOUND.format(name)}

    def put(self, name):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
            item.store_id = item_json["store_id"]
        else:
            item_json["name"] = name
            item_data = item_schema.load(item_json)
            item = ItemModel(**item_data)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        items = item_list_schema.dump(ItemModel.query.all())
        if user_id:
            return {"items": items}

        return {
            "items": [item["name"] for item in items],
            "message": "You need to log in to get more information"
        }, 200

