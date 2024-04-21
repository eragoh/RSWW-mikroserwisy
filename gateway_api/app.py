from flask import Flask, jsonify, Response, request
from flask_pymongo import PyMongo, ObjectId
from bson import json_util

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@travel-mongo:27017/TravelDB"

mongo = PyMongo(app)

def get_price(old_price):
    # jakis algorytm wyliczajacy cene, na podstawie
    # ceny, aktualnej daty, itp. itd.
    return 1200

@app.route('/')
def hello_world():
    return 'Hello, Gateway!'

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
    children    = request.args.get('children')
    search_dict = {}
    if country != 'None':
        search_dict['country'] = country
    if start_date: # nie dziala jeszcze
        search_dict['start_date'] = {'$gte': start_date}
    if return_date: # nie dziala jeszcze
        search_dict['end_date'] = {'$lte': return_date}

    try:
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
