from flask import Blueprint, request, render_template
import asyncio
from flask_login import login_required
from api import get_response

async def arender(html, data):
    task = asyncio.to_thread(render_template, html, data=data)
    return await task

reservations = Blueprint('reservations', __name__)

@reservations.route('/tours/<tourname>/buy/', methods=['GET', 'POST'])
@login_required
async def buy(tourname):
    if request.method == 'POST':
        # return await get_response('/payment/process')
        return await get_response(f'http://gateway-api:6543/payment/process')
    
    data = {
        'tourid': tourname
    }
    return await arender('buy.html', data)

@reservations.route('/reservations/')
@login_required
async def myreservations():
    return await arender('reservations.html', {})
