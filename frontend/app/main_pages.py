from flask import Blueprint, request, render_template
import asyncio
    

async def arender(html, data):
    task = asyncio.to_thread(render_template, html, data=data)
    return await task

mainpages = Blueprint('mainpages', __name__)

@mainpages.route('/')
async def index():
    return await arender('index.html', {})

@mainpages.route('/operations/')
async def operations():
    return await arender('operations.html', {})

@mainpages.route('/tours/')
async def tours():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    data = {
        'page' : page
    }
    return await arender('tours.html', data=data)

@mainpages.route('/tours/<tourname>/')
async def tours_detail(tourname):
    return await arender('tour_detail.html', {})

@mainpages.route('/', defaults={'path': ''})
@mainpages.route('/<path:path>')
async def catch_all(path):
    return await arender('404.html', {})