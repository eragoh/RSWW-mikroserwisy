.PHONY: all build

all: build

build:
	docker build travelDB-mongoDB/ -t mongo-rsww480 &
	docker build gateway_api/ -t gateway-api-rsww480 &
	docker build frontend/ -t frontend-api-rsww480 &
	docker build rabbitmq-gateway/ -t rabbitmq-gateway-rsww480 &
	docker build api-gateway/ -t api-gateway-rsww480 &
	docker build microservices/payment/ -t payment-service-rsww480 &
	docker build microservices/reservation/ -t reservation-service-rsww480 &
	docker build microservices/activities/ -t activities-service-rsww480 &
	docker build reservations-postgres/ -t postgres-db-reservations-rsww480 &
	wait

.DEFAULT_GOAL := all
