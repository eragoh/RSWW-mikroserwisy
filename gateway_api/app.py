from flask import Flask, jsonify, Response
from flask_pymongo import PyMongo
from bson import json_util

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://user:password@travel-mongo:27017/TravelDB"

mongo = PyMongo(app)

@app.route('/')
def hello_world():
    return 'Hello, Gateway!'

@app.route('/data')
def get_data():
    some_data = mongo.db.travelOffers.find_one()  # Adjust this to your collection and query needs
    if not some_data:
        return jsonify({"error": "No data found"}), 404
    # Use bson.json_util.dumps to serialize the MongoDB object including ObjectId to JSON
    return Response(json_util.dumps(some_data), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
