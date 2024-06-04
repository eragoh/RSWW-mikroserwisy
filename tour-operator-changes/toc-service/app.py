from flask import Flask, jsonify
import psycopg2
from random import randint as rint

app = Flask(__name__)

def get_connection():
    connection = psycopg2.connect(
        dbname="travel",
        user="postgres",
        password="postgres",
        host="toc-postgres"
    )
    return connection


def insert(trip, room):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO OPERATION (trip, room)
        VALUES (%s, %s)
        """,
        (trip, room)
    )
    connection.commit()

@app.route('/operations/')
def operations():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM OPERATION
        """
    )
    results = cursor.fetchall()
    results.reverse()

    return jsonify(results[:10])










#insert into operation(trip, room) values('222', '222');