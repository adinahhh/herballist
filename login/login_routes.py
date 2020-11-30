from flask import Blueprint, session, redirect, request, flash
from models import db, User
import bcrypt

login_blueprint = Blueprint('login_blueprint', __name__)


@login_blueprint.route('/sign-up', methods=['POST'])
def signup():
    """manual user registration; redirects user to their profile page"""

    first_name = request.form.get('first_name')
    email = request.form.get('email')
    password = request.form.get('password')
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    if hashed_password:
        new_user = User(first_name=first_name, email=email, password=hashed_password)
    else:
        return f"Please enter a valid password"

    # add to db here
    add_user_db(new_user)

    # adding session
    user_id = new_user.user_id
    session["user_id"] = user_id

    return redirect(f'/user/{user_id}')


@login_blueprint.route('/login', methods=['POST'])
def login():
    """logging in existing users who manually registered on app"""

    # get user email from form
    email = request.form.get('email')
    password = (request.form.get('password')).encode('utf-8')

    # search db for user
    existing_user = User.query.filter_by(email=email).first()
    existing_password = existing_user.password
    # user_email = existing_user.email
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
        # TODO: this doesnt work?
        flash('Password does not match. Please try again.')
        return redirect('/')


def add_user_db(new_user):
    """adds user to db"""

    db.session.add(new_user)
    db.session.commit()
    pass


@login_blueprint.route('/logout')
def logout():
    """logs out any user"""

    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

###########
# within sign up route:
# TODO add regex to form to ensure email and password fit parameters
# TODO: query db to see if email has been used before
# TODO: if existing user, then error out "email belongs to existing user; please login" message
###########
