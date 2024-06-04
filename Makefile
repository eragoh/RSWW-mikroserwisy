.PHONY: all build

all: build

build:
	docker build travelDB-mongoDB/ -t travel-mongo &
	docker build gateway_api/ -t gateway-api &
	docker build frontend/ -t frontend-api &
	docker build rabbitmq-gateway/ -t rabbitmq-gateway &
	docker build api-gateway/ -t api-gateway &
	docker build microservices/payment/ -t payment-service &
	docker build microservices/reservation/ -t reservation-service &
	docker build microservices/activities/ -t activities-service &
	docker build reservations-postgres/ -t postgres-db-reservations &
	docker build tour-operator-changes/postgress-toc/ -t toc-postgres &
	docker build tour-operator-changes/toc-service/ -t toc-service &
	docker build redis/ -t redis-service &
	wait

.DEFAULT_GOAL := all
