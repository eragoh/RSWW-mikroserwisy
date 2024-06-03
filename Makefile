.PHONY: all build

REPO_PREFIX ?= 10.40.71.55:5000/

all: build

build:
	docker build travelDB-mongoDB/ -t $(REPO_PREFIX)180140_mongo &
	docker build gateway-api/ -t $(REPO_PREFIX)180140_gateway-api &
	docker build frontend/ -t $(REPO_PREFIX)180140_frontend-api &
	docker build rabbitmq-gateway/ -t $(REPO_PREFIX)180140_rabbitmq-gateway &
	docker build api-gateway/ -t $(REPO_PREFIX)180140_api-gateway &
	docker build microservices/payment/ -t $(REPO_PREFIX)180140_payment-service &
	docker build microservices/reservation/ -t $(REPO_PREFIX)180140_reservation-service &
	docker build microservices/activities/ -t $(REPO_PREFIX)180140_activities-service &
	docker build reservations-postgres/ -t $(REPO_PREFIX)180140_postgres-db-reservations &
	wait

.DEFAULT_GOAL := all