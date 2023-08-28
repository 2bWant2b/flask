from flask_restful import Resource
from models.store import StoreModel
from schemas.store import StoreSchema

BLANK_ERROR = "'{}' cannot be left blank."
STORE_NOT_FOUND = "store {} not found."
NAME_ALREADY_EXISTS = "the store {} already exists."
ERROR_INSERTING = "An error occurred while inserting the store {}."
STORE_DELETED = "store {} deleted."

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)

class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200
        else:
            return {"message": STORE_NOT_FOUND.format(name)}, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS.format(name)}, 400
        store = StoreModel(name=name)
        try:
            store.save_to_db()
        except:
            return {"message": ERROR_INSERTING.format(name)}, 500

        return store_schema.dump(store), 201

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {"message": STORE_DELETED.format(name)}, 200

        return {"message": STORE_NOT_FOUND.format(name)}, 404


class StoreList(Resource):
    def get(self):
        return {"stores": store_list_schema.dump(StoreModel.query.all())}, 200


