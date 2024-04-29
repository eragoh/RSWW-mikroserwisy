from flask import Blueprint, request, render_template, redirect
import asyncio 
from flask_login import login_user, login_required, logout_user

from models import User

async def arender(html, data):
    task = asyncio.to_thread(render_template, html, data=data)
    return await task

auth = Blueprint('auth', __name__)

@auth.route('/login/', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect('/')
        return 'Błędne dane logowania xD.'
    
    return await arender('login.html', {})

@auth.route('/register/')
async def register():
    return await arender('register.html', {})

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/login/')