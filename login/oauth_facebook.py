# from flask import Blueprint, redirect, url_for
# from models import db, User
#
# fb_blueprint = Blueprint('fb_blueprint', __name__)


# TODO: come back to trying out oauth for fb
# need to try using https on local host?
# havent done logic for adding user to db yet
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
#
# @app.route('/login-facebook')
# def login_facebook():
#     facebook = oauth.create_client('facebook')
#     redirect_uri = url_for('authorize_facebook', _external=True)
#     return facebook.authorize_redirect(redirect_uri)
#
# @app.route('/authorize-facebook')
# def authorize_facebook():
#     facebook = oauth.create_client('facebook')
#     token = facebook.authorize_access_token()
#     resp = facebook.get('account/verify_credentials.json')
#     user_info = resp.json()
#     print(user_info)
#
#     return redirect('/')
