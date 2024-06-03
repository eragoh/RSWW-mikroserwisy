from flask import Blueprint, request, render_template, jsonify, redirect
from app import logger
from api import get_response

activities = Blueprint('activities', __name__)

@activities.route('/tours/<tourname>/watch/')
async def watch(tourname):
    response = await get_response(f'http://gateway-api:6543/watch/{tourname}')
    logger.info(f'WATCH {tourname}')
    return jsonify({'State': response})

@activities.route('/tours/<tourname>/watch_end/')
async def watch_end(tourname):
    response = await get_response(f'http://gateway-api:6543/watch_end/{tourname}')
    logger.info(f'WATCH END {tourname}')
    return jsonify({'State': 'Ok'})

@activities.route('/tours/<tourname>/watch_check/')
async def watch_check(tourname):
    response = await get_response(f'http://gateway-api:6543/watch_check/{tourname}')
    logger.info(f'WATCH CHECK {tourname}')
    return jsonify({'State': response})