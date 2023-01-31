from db import db

class ItemModel(db.Model):
    __tablename__ = "items" # Create a table called "items".

    id = db.Column(db.Integer, primary_key=True) # Defining a column in the items table.
    name = db.Column(db.String(80), unique=True, nullable=False) # Nullable basically makes it such that you cannot create an item without a name parameter.
    description = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2), nullable=False) # Precision is the number of decimal places.
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False, unique=False) # This is a foreign key. It is a reference to the id column in the stores table. "stores.id" is the name of the table and the column.
    store = db.relationship('StoreModel', back_populates="items") # This is a relationship. It is a reference to the StoreModel class. This is how we can access the store object from the item object. back_populates is the name of the relationship in the StoreModel class.
    tags = db.relationship('TagModel', back_populates="items", secondary="item_tags") 
