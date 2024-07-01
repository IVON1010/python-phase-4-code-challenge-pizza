#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask import Flask, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def restaurants():
    restaurants = Restaurant.query.all()
    restaurant_dict = [
        {'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address}
         for restaurant in restaurants]
    return jsonify(restaurant_dict)

@app.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def restaurants_by_id(restaurant_id):
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()

    if restaurant is None:
        return make_response({"message": "Restaurant not found"}, 404)

    restaurant_dict = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'restaurant_pizzas': []
    }

    for restaurant_pizza in restaurant.pizzas:  # Note: using 'pizzas' instead of 'restaurant_pizzas'
        pizza_to_dict = {
            'id': restaurant_pizza.id,
            'pizza': {
                'id': restaurant_pizza.pizza.id,
                'name': restaurant_pizza.pizza.name,
                'ingredients': restaurant_pizza.pizza.ingredients
            },
            'pizza_id': restaurant_pizza.pizza_id,
            'price': restaurant_pizza.price,
            'restaurant_id': restaurant_pizza.restaurant_id
        }
        restaurant_dict['restaurant_pizzas'].append(pizza_to_dict)
    
    return jsonify(restaurant_dict)

@app.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def restaurant_delete_by_id(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)

    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}, 404)

    restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=restaurant_id).all()
    for restaurant_pizza in restaurant_pizzas:
        db.session.delete(restaurant_pizza)

    db.session.delete(restaurant)

    db.session.commit()

    return f"Deleted restaurant {restaurant_id}"

@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_dict = [
        {'id': pizza.id, 'name': pizza.name, 'ingredients': pizza.ingredients} 
        for pizza in pizzas]
    return jsonify(pizza_dict)

@app.post('/restaurant_pizzas')
def restaurant_pizzas():
    restaurant_pizzas = RestaurantPizza(price=5, pizza_id=1, restaurant_id=3)

    if restaurant_pizzas is None:
        return make_response({"error": "Validation errors"}, 404)

    db.session.add(restaurant_pizzas)

    db.session.commit()

    return restaurant_pizzas.to_dict()


if __name__ == "__main__":
    app.run(port=5555, debug=True)
