import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import jwt_required

from db import db

from schemas import StoreSchema
from models import StoreModel # Remember to have this in the __init__.py file


blp = Blueprint("Stores", __name__, description="Operations on stores")

@blp.route("/store")
class StoreList(MethodView):
    @jwt_required(fresh=True) # Only fresh tokens can access this endpoint
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required(fresh=False) # Fresh or non-fresh tokens can access this endpoint
    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit() # The id is only assigned after the item is added to the database.
        except IntegrityError:
            abort(500, message="A store with that name already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the store")

        return store, 201

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}
