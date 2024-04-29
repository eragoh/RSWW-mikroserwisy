FROM rabbitmq:latest

RUN rabbitmq-plugins enable --offline rabbitmq_management

EXPOSE 5672 15672

ENV RABBITMQ_DEFAULT_USER=admin
ENV RABBITMQ_DEFAULT_PASS=password
