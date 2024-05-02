from flask import Flask, request, jsonify
import psycopg2
import threading
import pika
import time

app = Flask(__name__)

def get_connection():
    connection = psycopg2.connect(
        dbname="travel",
        user="postgres",
        password="postgres",
        host="postgres-db-reservations"
    )
    return connection

# Timer function
def start_timer(trip_id, db_conn, time_to_wait=60):
    time.sleep(time_to_wait)
    cursor = db_conn.cursor()
    
    # If trip is still unpaid then delete Reservation
    cursor.execute("SELECT * FROM reservations WHERE trip_id = %s AND paid = false", (trip_id,))
    if cursor.rowcount > 0:
        cursor.execute("DELETE FROM reservations WHERE trip_id = %s", (trip_id,))
        db_conn.commit()

# # Payment processing function
# def process_payment(ch, method, properties, body):
#     payment_info = eval(body) # Assuming payment_info is a dict-like string
#     trip_id = payment_info.get('trip_id')
#     success = payment_info.get('success')
    
#     db_conn = get_connection()
#     cursor = db_conn.cursor()
    
#     if success:
#         cursor.execute("UPDATE reservations SET paid = true WHERE trip_id = %s", (trip_id,))
#         db_conn.commit()
    
#     cursor.close()
#     db_conn.close()

# def setup_rabbitmq_consumer():
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()
#     channel.queue_declare(queue='payments')
    
#     channel.basic_consume(queue='payments', on_message_callback=process_payment, auto_ack=True)
#     threading.Thread(target=channel.start_consuming).start()

def send_payment_to_rabbitmq(trip_id, card_number):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='payments')
    
    # Prepare message as a dictionary
    payment_info = {'trip_id': trip_id, 'card_number': card_number}
    
    # Publish message to the queue
    channel.basic_publish(
        exchange='',
        routing_key='payments',
        body=str(payment_info)  # Convert dictionary to string for transport
    )

    connection.close()

def listen_for_payment_response(trip_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    payment_success = None

    def payment_callback(ch, method, properties, body):
        nonlocal payment_success
        payment_info = eval(body)  # Assuming payment_info is a dict-like string
        if payment_info.get('trip_id') == trip_id:
            payment_success = payment_info.get('success')
            ch.stop_consuming()  # Stop after receiving relevant response

    channel.queue_declare(queue='payment_responses')
    channel.basic_consume(queue='payment_responses', on_message_callback=payment_callback, auto_ack=True)

    start_time = time.time()

    while True:
        # Check if timeout has been exceeded
        if time.time() - start_time >= 20:
            connection.close()
            return None  # Timeout occurred

        # Process RabbitMQ messages
        channel.connection.process_data_events(time_limit=1)  # Process messages for up to 1 second
        if payment_success is not None:
            connection.close()
            return payment_success

@app.route('/reservation/pay', methods=['POST'])
def pay_reservation():
    trip_id = request.form['trip_id']
    card_number = request.form['card_number']
    
    db_conn = get_connection()
    cursor = db_conn.cursor()
    
    cursor.execute("SELECT * FROM reservations WHERE trip_id = %s", (trip_id,))
    reservation = cursor.fetchone()

    if reservation is None:
        cursor.close()
        db_conn.close()
        return jsonify({"message": "Reservation not available."}), 404

    ## ?????????????????? == 'false' ???????????
    elif reservation[-1]: # Assuming 'paid' column is the last in the reservation record
        cursor.close()
        db_conn.close()
        return jsonify({"message": "Reservation already paid."}), 200

    else:
        # Send payment info to RabbitMQ
        send_payment_to_rabbitmq(trip_id, card_number)

        # Listen for payment response
        payment_result = listen_for_payment_response(trip_id)

        if payment_result is None:
            cursor.close()
            db_conn.close()
            return jsonify({"message": "Payment timed out."}), 408

        elif payment_result:
            cursor.execute("DELETE FROM reservations WHERE trip_id = %s", (trip_id,))
            cursor.execute(
                "INSERT INTO reservations (username, trip_id, price, paid) VALUES (%s, %s, %s, true)",
                (reservation[0], trip_id, reservation[2])  # Assuming columns are in order of username, trip_id, price
            )
            db_conn.commit()

            cursor.close()
            db_conn.close()
            return jsonify({"message": "Payment & Reservation successful."}), 200

        else:
            cursor.close()
            db_conn.close()
            return jsonify({"message": "Payment failed."}), 400

@app.route('/reservation/add', methods=['POST'])
def add_reservation():
    username = request.form['username']
    trip_id = request.form['trip_id']
    price = request.form['price']
    
    db_conn = get_connection()
    cursor = db_conn.cursor()
    
    # Add reservation entry
    cursor.execute(
        "INSERT INTO reservations (username, trip_id, price, paid) VALUES (%s, %s, %s, false)",
        (username, trip_id, price)
    )
    db_conn.commit()
    
    cursor.close()
    db_conn.close()
    
    # Start timer for trip_id
    threading.Thread(target=start_timer, args=(trip_id, db_conn)).start()

    return jsonify({"message": "Reservation added successfully!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
