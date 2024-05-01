from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

@app.route('/process/', methods=['POST'])
def process_payment():
    card_number = request.json.get('card_number')

    time.sleep(3)

    # Losowanie, czy płatność się udała
    payment_success = random.choice([True, False])

    if payment_success:
        return jsonify({"success": True, "message": "Płatność została pomyślnie zrealizowana."}), 200, {'Content-Type': 'application/json'}
    else:
        return jsonify({"success": False, "message": "Płatność nie została zrealizowana."}), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6544)
