from flask import Blueprint, request, render_template, jsonify
import asyncio
import json
from flask_login import login_required, current_user
from api import get_response, post_response

async def arender(html, data):
    task = asyncio.to_thread(render_template, html, data=data)
    return await task

reservations = Blueprint('reservations', __name__)


@reservations.route('/tours/<tourname>/buy/', methods=['GET', 'POST'])
@login_required
async def buy(tourname):
    if request.method == 'POST':
        card_number = request.form.get('card_number')
        price = request.form.get('price')
        
        payment_data = {
            'trip_id': tourname,
            'card_number': card_number,
            'price': price
        }
        
        response = await post_response(f'http://gateway-api:6543/reservation/pay/', payment_data)
        
        if "error" in response:
            return jsonify(response), 400
        
        return jsonify(response), 200

    # For GET requests

    response = await get_response(f'http://gateway-api:6543/reservation/add/?username={current_user.username}&trip_id={tourname}&price={0}')
    
    if "error" in response:
        return jsonify(response), 400

    data = {
        'tourid': tourname,
        'reserved': response['status'] == 'RESERVED' and current_user.username != response['username']
    }
    return await arender('buy.html', data)

@reservations.route('/reservations/')
@login_required
async def myreservations():
    return await arender('reservations.html', {})
