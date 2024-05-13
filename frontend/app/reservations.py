from flask import Blueprint, request, render_template, jsonify, redirect
import asyncio
import json
from flask_login import login_required, current_user
from api import get_response, post_response
from app import logger

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
        room = request.form.get('room')
        # maybe calculate price
        payment_data = {
            'trip_id': tourname,
            'card_number': card_number,
            'price': price,
            'room': room
        }
        
        response = await post_response(f'http://gateway-api:6543/reservation/pay/', payment_data)
        if response['result'] == 'failure':
            return await arender('failure.html', {})
        elif response['result'] == 'success':
            return redirect('/reservations/')
            return await arender('reservations.html', {})
        if "error" in response:
            return jsonify(response), 400
        
        return jsonify(response), 200

    # For GET requests

    #response = await get_response(f'http://gateway-api:6543/reservation/add/?username={current_user.username}&trip_id={tourname}&price={0}')
    #response = await get_response(f'http://gateway-api:6543/reservation/check/?trip_id={tourname}')
    # response = jsonify({'status': 'RESERVED', 'username': 'user3'})
    # dresponse = json.loads(response)
    # if not dresponse['status'] == 'RESERVED' and not dresponse['username'] == current_user.username:
    #     return await arender('buy2.html', {})
    
    # if "error" in response:
    #     return jsonify(response), 400

    data = {
        'tourid': tourname,
        'reserved': False#response['status'] == 'RESERVED' and current_user.username != response['username']
    }
    return await arender('buy.html', data)

@reservations.route('/reservations/')
@login_required
async def myreservations():
    return await arender('reservations.html', {})

@reservations.route('/makereservation/', methods=['POST'])
@login_required
async def makereservation():
    data = request.json


    # Extract the necessary fields
    tourid = data.get('tourid')
    room = data.get('room')
    price = data.get('price')
    adults = data.get('adults')
    ch3 = data.get('ch3')
    ch10 = data.get('ch10')
    ch18 = data.get('ch18')

    user = current_user.username
    response = await get_response(f'http://gateway-api:6543/reservation/add/?username={user}&trip_id={tourid}&price={price}&room={room}&adults={adults}&ch3={ch3}&ch10={ch10}&ch18={ch18}')
    logger.info(f'RESPONSE MAKE RESERVATION: {response}')
    return response
    return jsonify({'message': 'Reservation received successfully'})

@reservations.route('/getmytours/')
@login_required
async def getmytours():
    response = await get_response(f'http://gateway-api:6543/getmytours/?username={current_user.username}')
    logger.info(f'MY RESERVATIONS[{current_user.username}] - {response}')
    return response