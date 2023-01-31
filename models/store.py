from db import db

class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship('ItemModel', back_populates="store", lazy="dynamic", cascade="all, delete") # This is a relationship. It is a reference to the ItemModel class. This is how we can access the item objects from the store object. back_populates is the name of the relationship in the ItemModel class. lazy="dynamic" means that the items will not be loaded until we call the json() method. This is because we do not want to load all the items when we load the store. We only want to load the items when we call the json() method.
    tags = db.relationship('TagModel', back_populates="store", lazy="dynamic", cascade="all, delete")