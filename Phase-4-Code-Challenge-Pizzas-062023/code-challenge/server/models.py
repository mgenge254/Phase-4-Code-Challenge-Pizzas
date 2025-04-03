from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define metadata with naming convention for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy with the metadata
db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship to RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', lazy=True)

    # Serialization rules (exclude restaurant_pizzas to avoid circular references)
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship to RestaurantPizza
    pizza_restaurants = db.relationship('RestaurantPizza', backref='pizza', lazy=True)

    # Serialization rules (exclude pizza_restaurants to avoid circular references)
    serialize_rules = ('-pizza_restaurants.pizza',)

    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign key relationships
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)

    # Serialization rules (exclude backrefs to avoid circular references)
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.pizza_restaurants')

    # Validation for price
    @validates('price')
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'