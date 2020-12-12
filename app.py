from flask import Flask, url_for, redirect, session, render_template
from authlib.integrations.flask_client import OAuth
from models import connect_to_db, db, User
import os
from login.login_routes import login_blueprint


#running an instance of flask
app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
oauth = OAuth(app)
app.register_blueprint(login_blueprint)


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
# request_token_url is used to detect if client is OAuth 1 or OAuth 2 client.
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
        add_user_db(new_user)
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
        add_user_db(new_user)
        session["user_id"] = new_user.user_id
        return redirect(f'/user/{new_user.user_id}')


def add_user_db(new_user):
    """adds user to db"""

    db.session.add(new_user)
    db.session.commit()
    pass


@app.route('/user/<int:user_id>')
def user_profile(user_id):
    """logged in user's profile page"""
    # for now, only using user_id
    # with future functionality for saving herbs, will query db for that
    # and return onto page; one to many relationship
    # TODO: MAKE SURE USER IS LOGGED IN (another fxn?), DONT JUST QUERY FOR USER
    # todo: use .get_or_404()

    first_name = (User.query.filter_by(user_id=user_id).first()).first_name
    return render_template('profile-page.html', first_name=first_name)


#############
# TODO check if i need to update token for google. search 'refresh_token' in docs
# TODO: utilize ajax for google/twitter/fb buttons on homepage
# TODO: add in blueprint for each registry/route for fb/google/twitter
# TODO: have a delete function for user to delete their info from db
#############


if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    #DebugToolbarExtension(app)
    app.run(host='0.0.0.0')