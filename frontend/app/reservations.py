from flask import Blueprint, request, render_template
import asyncio
from flask_login import login_required

async def arender(html, data):
    task = asyncio.to_thread(render_template, html, data=data)
    return await task

reservations = Blueprint('reservations', __name__)

@reservations.route('/tours/<tourname>/buy/')
@login_required
async def buy(tourname):
    return await arender('buy.html', {})
