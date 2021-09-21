from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "IKNOWTHISISNTSECRETOK"
db = SQLAlchemy(app)

from models import *

@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

import auth
app.register_blueprint(auth.bp)

# NOTE: see api.py for the api blueprint
import api
app.register_blueprint(api.bp)

if __name__ == '__main__':
    app.run()
