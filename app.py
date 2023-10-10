import secrets
import requests
import json
from flask import Flask, render_template, make_response, redirect, request, Response

app = Flask(__name__)

users = [] # horrible global, but it's just a demo

@app.route('/')
def index():
    state = secrets.token_urlsafe(32)
    return render_template('index.html', state=state)

@app.route('/redirect/')
def handle_redirect():
    state = request.args.get('state')
    code = request.args.get('code')
    redirect_uri = 'https://42test.ktano-studio.com/redirect'  # Replace with your actual redirect URI
    access_token = exchange_code_for_token(code, redirect_uri)
    if access_token is not None:
        # Store the access token in session or database for future use
        # For now, we'll just print it to the console
        print(f"Access token: {access_token}")
        # make a request to the 42 API for the user's email address
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            #user_data = json.dumps(user_data, indent=3, sort_keys=True)
            with open("campus_users.json", "r") as f:
                users = json.load(f)
            return render_template('online_students.html', data=users) 
        else:
            return('Failed to get user data')
    else:
        return 'Failed to exchange code for access token'

def exchange_code_for_token(code, redirect_uri):
    token_url = 'https://api.intra.42.fr/oauth/token'
    client_id = 'u-UID-OF-YOUR-APP'  
    client_secret = 's-SECRET-OF-YOUR-APP'
    grant_type = 'authorization_code'

    data = {
        'grant_type': grant_type,
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        return access_token
    else:
        return None

@app.route('/online_students/')
def handle_students():
    return render_template('online_students.html', users=users)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
