#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict() for restaurant in restaurants], 200
    


class RestaurantResource(Resource):
    def get(self, id):
        session = db.session  # Get the active session
        restaurant = session.get(Restaurant, id) 

        if restaurant:
            return restaurant.to_dict(rules=('-restaurant_pizzas.restaurant',)), 200
        return {"error": "Restaurant not found"}, 404
    
    def delete(self, id):
        session = db.session
        restaurant = session.get(Restaurant, id) 
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        # First delete associated restaurant_pizzas
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        session.delete(restaurant)
        session.commit()
        return {}, 204
    


class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict() for pizza in pizzas], 200
    


class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            return new_restaurant_pizza.to_dict(), 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400


# register routes
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")



if __name__ == '__main__':
    app.run(port=5555, debug=True)