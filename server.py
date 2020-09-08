from flask import FLask, render_template, request, flash, redirect

import os
import requests

app = Flask(_name_)
app.secret_key = "SECRETSECRETSECRET"

@app.route('/')
def homepage():
    """Homepage with search form."""

    return render_template('homepage.html')



if __name__ == '__main__':
    app.debug = True
    # connect_to_db(app)
    app.run(port=5000, host='0.0.0.0')