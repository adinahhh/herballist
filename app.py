from flask import Flask, url_for, redirect, session, request, render_template, flash
from authlib.integrations.flask_client import OAuth

from models import connect_to_db, db, User

import os
import bcrypt

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
    """this route shows homepage"""
    # email = dict(session).get('email', None)
    # screen_name = dict(session).get('screen_name', None)

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
    email = user_info['email']
    first_name = user_info['given_name']
    # check for existing user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        session["user_id"] = existing_user.user_id
        return redirect(f'/user/{existing_user.user_id}')
    else:
        # create a user in db
        new_user = User(first_name=first_name, email=email)
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.user_id
        return redirect(f'/user/{new_user.user_id}')

    # session.permanent = True this will make session permanent even after browser is closed
    return redirect('/')

@app.route('/authorize-twitter')
def authorize_twitter():
    twitter = oauth.create_client('twitter')
    token = twitter.authorize_access_token()
    resp = twitter.get('account/verify_credentials.json')
    user_info = resp.json()
    username = user_info['screen_name']
    first_name = user_info['name']

    # adding info to db
    # first see if username is in db already...
    existing_user = User.query.filter_by(screen_name=username).first()
    if existing_user:
        session["user_id"] = existing_user.user_id
        return redirect(f'/user/{existing_user.user_id}')
    else:
        # create a user in db
        new_user = User(screen_name=username, first_name=first_name)
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.user_id
        return redirect(f'/user/{new_user.user_id}')


# @app.route('/authorize-facebook')
# def authorize_facebook():
#     facebook = oauth.create_client('facebook')
#     token = facebook.authorize_access_token()
#     resp = facebook.get('account/verify_credentials.json')
#     user_info = resp.json()
#     print(user_info)
#
#     return redirect('/')


@app.route('/logout')
def logout():
    """logs out any user"""

    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/sign-up', methods=['POST'])
def signup():
    """manual user registration; redirects user to their profile page"""

    first_name = request.form.get('first_name')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # TODO add regex to form to ensure email and password fit parameters
    # error messages if password does not meet expectations?
    if hashed_password:
        new_user = User(first_name=first_name, email=email, password=hashed_password)
    else:
        return f"Please enter a valid password"
    # add to db here
    db.session.add(new_user)
    db.session.commit()

    # adding session
    user_id = new_user.user_id
    session["user_id"] = user_id

    return redirect(f'/user/{user_id}')


@app.route('/login', methods=['POST'])
def login():
    """logging in existing users who manually registered on app"""

    # get user email from form
    email = request.form.get('email')
    password = (request.form.get('password')).encode('utf-8')

    # search db for user
    existing_user = User.query.filter_by(email=email).first()
    existing_password = existing_user.password
    user_email = existing_user.email
    user_id = existing_user.user_id

    if not existing_user:
        flash('No user found with this email. Please try again')
        return redirect('/')

    # compare password entered with password from db
    if bcrypt.checkpw(password, existing_password):
        # flash(f'Welcome back, {user_email}!')
        session["user_id"] = user_id
        return redirect(f'/user/{user_id}')
    else:
        flash('Password does not match. Please try again.')
        return redirect('/')


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """logged in user's profile page"""
    # for now, only using user_id
    # with future functionality for saving herbs, will query db for that
    # and return onto page; one to many relationship
    first_name = (User.query.filter_by(user_id=user_id).first()).first_name
    return render_template('profile-page.html', first_name=first_name)


#############
# TODO check if i need to update token for google. search 'refresh_token' in docs
# TODO: login below
# on homepage.html, can have a form that offers different login options, if user clicks on google,
# will redirect them to route "/login-google", same for twitter
# TODO decide where I am collecting user's info for db-- in authorize routes?
# TODO decide if I need the session info in "authorize" routes?
# TODO: add in modules for each registry/route for fb/google/twitter -- this
# TODO: can consolidate how many routes i need to have in app; have a login module?
# TODO: create a function for adding a user to db (im reusing db.add/db.commit in routes)
#############


if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    #DebugToolbarExtension(app)
    app.run(host='0.0.0.0')