from flask import Flask, url_for, redirect, session, request, render_template
from authlib.integrations.flask_client import OAuth

from models import connect_to_db, db, User

import os
# import requests?

#running an instance of flask
app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
oauth = OAuth(app)

# register authentication
google = oauth.register(
    name ='google',
    client_id = os.environ['GOOGLE_CLIENT_ID'],
    client_secret = os.environ['GOOGLE_CLIENT_SECRET'],
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    client_kwargs = {'scope': 'openid profile email'},
)

# below is registering a remote app for twitter; twitter is an OAuth 1.0 service
# request_token_url is used to detect if client is OAuth 1 or OAuth 2 cient.
twitter = oauth.register(
    name = 'twitter',
    client_id = os.environ['TWITTER_CLIENT_ID'],
    client_secret = os.environ['TWITTER_CLIENT_SECRET'],
    request_token_url ='https://api.twitter.com/oauth/request_token',
    request_token_params = None,
    access_token_url = 'https://api.twitter.com/oauth/access_token',
    access_token_params = None,
    authorize_url = 'https://api.twitter.com/oauth/authenticate',
    authorize_params = None,
    api_base_url = 'https://api.twitter.com/1.1/',
    client_kwargs = None,
)

# TODO: come back to trying out oauth for fb
# facebook = oauth.register(
#     name = 'facebook',
#     client_id = os.environ['FACEBOOK_CLIENT_ID'],
#     client_secret = os.environ['FACEBOOK_CLIENT_SECRET'],
#     access_token_url = 'https://graph.facebook.com/v8.0/oauth/access_token',
#     access_token_params = None,
#     authorize_url = 'https://www.facebook.com/v8.0/dialog/oauth',
#     authorize_params = None,
#     api_base_url = 'https://www.graph.facebook.com/me',
#     client_kwargs = {'scope': 'name email'},
# )

@app.route('/')
def hello_world():
    # email = dict(session).get('email', None)
    # screen_name = dict(session).get('screen_name', None)
    # # TODO redo below: am I rerouting to user's profile page?
    # # with a message "welcome back, {screen_name} {email}"
    # if email is not None:
    #     return f"Hey, {email}!"
    # else:
    #     return f"Welcome to my page {screen_name}"
    return render_template('homepage.html')

# first route that gets hit
@app.route('/login-google')
def login_google():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login-twitter')
def login_twitter():
    twitter = oauth.create_client('twitter')
    redirect_uri = url_for('authorize_twitter', _external=True)
    return twitter.authorize_redirect(redirect_uri)

# @app.route('/login-facebook')
# def login_facebook():
#     facebook = oauth.create_client('facebook')
#     redirect_uri = url_for('authorize_facebook', _external=True)
#     return facebook.authorize_redirect(redirect_uri)


# route that user is redirected to if authentication is successful
@app.route('/authorize-google')
def authorize_google():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    print(user_info)
    # do something with the token and profile
    # can use print() to see user_info, dont need to pass around google info in session cookie
    # could alternatively get user_info to create and store login info in db, put that into the cookie
    session['email'] = user_info['email']

    # session.permanent = True this will make session permanent even after browser is closed
    return redirect('/')

@app.route('/authorize-twitter')
def authorize_twitter():
    twitter = oauth.create_client('twitter')
    token = twitter.authorize_access_token()
    resp = twitter.get('account/verify_credentials.json')
    user_info = resp.json()
    # can do something here with token and profile
    session['screen_name'] = user_info['screen_name']
    return redirect('/')

# @app.route('/authorize-facebook')
# def authorize_facebook():
#     facebook = oauth.create_client('facebook')
#     token = facebook.authorize_access_token()
#     resp = facebook.get('account/verify_credentials.json')
#     user_info = resp.json()
#     print(user_info)
#     # can do something here with token and profile
#     # session['email'] = user_info['email']
#     return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

# below is sign up route
@app.route('/sign-up', methods=['POST'])
def signup():
    """User registration; redirects user to their profile page"""

    if request.method == 'POST':
        first_name = request.form['first_name']
        email = request.form['email']
        password = request.form['password']

    # define user from db
    # check for password entered?
    # TODO add regex to form to ensure email and password fit parameters
    # error messages if password does not meet expectations?
        if len(password) > 0:
            new_user = User(first_name=first_name, email=email, password=password)
        else:
            return f"Please enter a valid password"
    # add to session here
        db.session.add(new_user)
        db.session.commit()
        print(new_user)

    # update this so we are redirecting to user's profile page?
    return f"Hello {email}, its nice to meet you"

#############
# TODO check if i need to update token for google. search 'refresh_token' in docs
# TODO: login below
# on homepage.html, can have a form that offers different login options, if user clicks on google,
# will redirect them to route "/login-google", same for twitter
# TODO decide where I am collecting user's info for db-- in authorize routes?
# TODO decide if I need the session info in "authorize" routes?
# TODO: add in modules for each registry/route for fb/google/twitter -- this
# TODO: can consolidate how many routes i need to have in project?
#############

if __name__ == '__main__':

    app.debug = True

    connect_to_db(app)

    #DebugToolbarExtension(app)

    app.run(host='0.0.0.0')