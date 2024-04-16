from flask import(
    Flask,
    render_template,
    request
)
import requests

app = Flask(__name__)

@app.route('/')
def index():
    data = {
        'is_authenticated' : True
    }
    return render_template('index.html', data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('login', request)
    
    data = {

    }
    return render_template('login.html', data=data)
@app.route('/register')
def register():
    data = {

    }
    return render_template('register.html', data=data)

@app.route('/tours/')
def tours():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    data = {
        'is_authenticated' : False,
        'page' : page
    }
    return render_template('tours.html', data=data)

@app.route('/tours/<tourname>')
def tours_detail(tourname):
    data = {

    }
    return render_template('tour_detail.html', data=data)

@app.route('/gettoursss/')
def gettoursss():
    page_number = request.args.get('page')
    page = int(page_number) if (page_number and page_number.isdigit()) else 1
    try:
        response = requests.get(f'http://gateway-api:5000/data/{page - 1}')
        if response.status_code == 200:
            json_data = response.json()
            return json_data
    except requests.exceptions.RequestException as e:
        return None
    return None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    try:
        response = requests.get('http://gateway-api:5000/data')
        if response.status_code == 200:
            json_data = response.json()
        data = {
            'is_authenticated' : False,
            'response' : json_data
        }
    except requests.exceptions.RequestException as e:
        data = {
            'is_authenticated' : False,
            'response' : f'dupa {e}'
        }
    
    return render_template('404.html', data=data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
