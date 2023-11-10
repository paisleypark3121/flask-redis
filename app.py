import os
from dotenv import load_dotenv

import redis
from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta

app = Flask(__name__)

app.secret_key = 'flask-redis'
app.template_folder = 'templates'
app.static_folder = 'static'

_redis=None

def init():
    print("INIT")
    load_dotenv()    

    try:
        r = redis.Redis(
            host=os.getenv('REDIS_URL'),
            port=16795,
            password=os.getenv('REDIS_KEY')
        )
        print('Connection to Redis is OK')
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=2)
    #app.SESSION_REFRESH_EACH_REQUEST=True

@app.route('/')
def home():
    #return render_template('test.html')
    return "HELLO WORLD"


@app.route('/get_session')
def get_session():

    if 'session_id' in session:
        session_id = session['session_id']
        key = f'session:{session_id}'

        # Retrieve the session data from Redis
        session_data = _redis.get(key)

        if session_data is not None:
            return session_data.decode('utf-8')  # Decode from bytes to string

    return 'Session data not found'


@app.route('/set_session')
def set_session():

    session_id = request.args.get('session_id')
    value = request.args.get('value')

    if session_id and value:
        session['session_id'] = session_id
        
        key = f'session:{session_id}'
        _redis.set(key, value)
        _redis.expire(key, 120)

        return 'Session data set successfully'

    return 'Invalid parameters provided'

_redis=init()
app.run(debug=True)

#http://127.0.0.1:5000/set_session?session_id=1234&value=ciao
#http://127.0.0.1:5000/get_session