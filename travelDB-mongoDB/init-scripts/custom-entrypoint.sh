#!/bin/bash

# Start MongoDB in the background
/usr/local/bin/docker-entrypoint.sh mongod &

# Wait for MongoDB to be ready
while ! mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    sleep 1
done

mongoimport --uri "mongodb://user:password@180140_travel-mongo:27017/TravelDB" --collection travelOffers --type json --file /var/my-db/travel-offers.json --jsonArray
wait
