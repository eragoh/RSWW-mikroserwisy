import pika
from pymongo import MongoClient
from bson import ObjectId
import json

credentials = pika.PlainCredentials('admin', 'password')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq-gateway', credentials=credentials))

db = MongoClient("mongodb://user:password@travel-mongo:27017/TravelDB").TravelDB

def get_price(old_price):
    # jakis algorytm wyliczajacy cene, na podstawie
    # ceny, aktualnej daty, itp. itd.
    return 1200

def send(ch, method, props, some_data):
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(some_data))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def get_countries(ch, method, props, body):
    some_data = db.travelOffers.distinct("country")
    send(ch, method, props, json.dumps(some_data))

def get_data_tour(ch, method, props, body):
    try:
        tour = body.decode()
        some_data = db.travelOffers.find_one({"_id": ObjectId(tour)})
        some_data['price'] = 1200
    except:
        some_data = None
    send(ch, method, props, json.dumps(some_data))

def get_data_page(ch, method, props, body):
    try:
        page = int(body.decode())
        some_data = [
            {**offer, 'price': get_price(offer)} 
            for offer in 
            list(db.travelOffers.find().skip(int(page) * 10).limit(10))
        ]
    except:
        some_data = None
    send(ch, method, props, json.dumps(some_data))
  
channels = (
    (connection.channel(), 'data_tour', get_data_tour),
    (connection.channel(), 'countries', get_countries),
    (connection.channel(), 'data_page', get_data_page),
)

for channel, qname, func in channels:
    channel.queue_declare(queue=qname, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=qname, on_message_callback=func)
    
for channel, _, _ in channels:
    channel.start_consuming()