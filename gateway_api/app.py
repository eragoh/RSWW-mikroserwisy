from flask import Flask, jsonify, Response, request
from flask_pymongo import PyMongo, ObjectId
from bson import json_util
from datetime import datetime
import requests

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@travel-mongo:27017/TravelDB"

mongo = PyMongo(app)

reservations = {}

def get_seasonal_factor(month):
    if month in [6, 7, 8]:  # Summer
        return 1.2
    elif month in [12, 1, 2]: # Winter
        return 1.1
    return 1.0

def get_price(offer):
    base_price = offer.get('price', 4500)
    start_date = datetime.strptime(offer['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(offer['end_date'], "%Y-%m-%d")
    start_month = start_date.month
    end_month = end_date.month

    # Define a helper function to get seasonal factors
    def get_seasonal_factor(month):
        if month in [6, 7, 8]:  # Summer
            return 1.2
        elif month in [12, 1, 2]: # Winter
            return 1.1
        return 1.0

    # Average the seasonal factors of start and end months
    seasonal_factor = (get_seasonal_factor(start_month) + get_seasonal_factor(end_month)) / 2

    config_adjustment = 0
    if offer['room']['is_family']:
        config_adjustment += 200
    elif offer['room']['is_standard']:
        config_adjustment += 400
    elif offer['room']['is_apartment']:
        config_adjustment += 900

    score_factor = offer['score']/5 * 0.89

    total_price = (base_price + config_adjustment) * seasonal_factor * score_factor
    total_price = round(total_price) + 0.99
    return total_price


@app.route('/')
def hello_world():
    return 'Hello, Gateway!'

@app.route('/getprice/')
def getprice():
    sum = 0
    room = request.args.get('room')
    price = float(request.args.get('price'))
    if room == 'Apartament':
        price += 900
    elif room == 'Rodzinny':
        price += 200
    elif room == 'Standardowy':
        price += 400
    elif room == 'Studio':
        price += 0

    data = {}
    for arg in ('adults', 'ch3', 'ch10', 'ch18'):
        data[arg] = int(request.args.get(arg))

    sum += data['adults'] * price
    sum += data['ch3'] * price * 0.5
    sum += data['ch10'] * price * 0.7
    sum += data['ch18'] * price * 0.8   
    return jsonify({'price' : sum})

@app.route('/data/countries')
def get_countries():
    some_data = mongo.db.travelOffers.distinct("country")
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/data/tours/<tour>')
def get_data_tour(tour):
    try:
        some_data = mongo.db.travelOffers.find_one({"_id": ObjectId(tour)})
        some_data['price'] = get_price(some_data)
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/clock/<tour>')
def get_tour_clock(tour):
    if tour in reservations.keys():
        clock = (datetime.now() - reservations[tour]).seconds
        if clock > 60:
           reservations[tour] = datetime.now()
           clock = 60
        else:
            clock = 60 - clock
    else:
        reservations[tour] = datetime.now()
        clock = 60

    return jsonify({'clock': clock})

@app.route('/data/<page>')
def get_data_page(page):
    try:
        some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(mongo.db.travelOffers.find().skip(int(page) * 10).limit(10))
        ]
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/data/tours/parameters')
def get_parametrized_data():
    country = request.args.get('country')
    start_date  = request.args.get('start_date')
    return_date = request.args.get('return_date')
    adults      = request.args.get('adults')
    children3   = request.args.get('children3')
    children10  = request.args.get('children10')
    children18  = request.args.get('children18')
    departue    = request.args.get('departue')
    search_dict = {}
    

    try:
        if country:
            search_dict['country'] = country
        if departue:
            search_dict['departure_location'] = departue
        if start_date:
            search_dict['start_date'] = {'$gte': start_date}
        if return_date:
            search_dict['end_date'] = {'$lte': return_date}
        if adults:
            search_dict['adults'] = {'$gte': int(adults)}
        if children3:
            search_dict['children_under_3'] = {'$gte': int(children3)}
        if children10:
            search_dict['children_under_10'] = {'$gte': int(children10)}
        if children18:
            search_dict['children_under_18'] = {'$gte': int(children18)}
        some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(mongo.db.travelOffers.find(search_dict))
        ]
    except:
        return jsonify({"error": "No data found"}), 404
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')


@app.route('/data/')
def get_data():
    some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(mongo.db.travelOffers.find().limit(10))
        ]
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')
 

@app.route('/payment/process/')
def process_payment():
    payment_data = {"XD3": "XD3"}
    response = requests.post("http://payment-service:6544/process/", json=payment_data)
    if response.status_code != 200:
        return jsonify({"error": "Payment processing failed"}), response.status_code
    return jsonify(response.json()), 200




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')