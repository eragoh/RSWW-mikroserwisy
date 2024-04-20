from flask import Flask, jsonify, Response, request
from flask_pymongo import PyMongo, ObjectId
from bson import json_util

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@travel-mongo:27017/TravelDB"

mongo = PyMongo(app)

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
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')

@app.route('/data/<page>')
def get_data_page(page):
    try:
        some_data = list(mongo.db.travelOffers.find().skip(int(page) * 10).limit(10))
    except:
        return get_data()
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')


@app.route('/data/')
def get_data():
    some_data = list(mongo.db.travelOffers.find().limit(10))
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    return Response(json_util.dumps(some_data), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
