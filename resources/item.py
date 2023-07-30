from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()  # request parsing
    parser.add_argument("price",
                        type=float,
                        required=True,
                        help="this field cannot be left blank"
                        )
    parser.add_argument("store_id",
                        type=int,
                        required=True,
                        help="every item needs a store id"
                        )

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {"message": f"item not {name} found"}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": f"An item with name {name} already exists."}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name, **data)  # data["price"], data["store_id"]

        try:
            item.save_to_db()
        except:
            return {"message": f"An error occurred inserting the item {name}"}, 500  # internal server error

        return item.json(), 201  # CREATED

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
        # connection = sqlite3.Connection("./data.db")
        # cursor = connection.cursor()
        #
        # query = "DELETE FROM items WHERE name=?"
        # cursor.execute(query, (name,))
        #
        # connection.commit()
        # connection.close()

        return {"message": f"item {name} deleted"}

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)  # data["price"], data["store_id"]
        else:
            item.price = data["price"]
        item.save_to_db()

        return item.json()


class ItemList(Resource):
    def get(self):
        return {"items": [item.json() for item in ItemModel.query.all()]}
