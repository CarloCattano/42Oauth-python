# Simple debug flask app
import os
import json
from flask import Flask, render_template

app = Flask(__name__)

if not os.path.exists('campus_users.json'):
    print('campus_users.json not found. Please run python getUsers.py to generate it')
    exit(1)

@app.route('/')
def index():
    with open('campus_users.json') as f:
        data = json.load(f)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

