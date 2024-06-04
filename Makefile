.PHONY: all build

REPO_PREFIX ?= ''

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
	docker build tour-operator-changes/postgress-toc/ -t $(REPO_PREFIX)180140_toc-postgres &
	docker build tour-operator-changes/toc-service/ -t $(REPO_PREFIX)180140_toc-service &
	docker build redis/ -t redis-service &
	docker build tests/ -t $(REPO_PREFIX)180140_tests &
	wait

.DEFAULT_GOAL := all
