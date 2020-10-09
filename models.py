from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

class User(db.Model):
    """info about users"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(75), nullable=True)
    screen_name = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String(15), nullable=False)
    name =  db.Column(db.String(30), nullable=True)

    def __repr__(self):
        """provide info about user"""

        return f"User id: {self.user_id} User name: {self.name}"

    # look into other methods needed
    # get user id
    # update password
    # log out?

def connect_to_db(app, db_uri="postgresql:///herbal"):
    """ Connect database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

if __name__ == "__main__":

    from app import app
    connect_to_db(app)
    print("Connected to DB.")