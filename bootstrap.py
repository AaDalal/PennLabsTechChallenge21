import os
import json
from app import db, DB_FILE
from werkzeug.security import generate_password_hash

def create_user():
    from models import User
    josh = User(username = 'josh', first_name = 'josh', last_name = 'peck', email = 'joshpeck@goosgle.co', password =  generate_password_hash('password!'))
    db.session.add(josh)
    db.session.commit()

def load_data():
    from utils import create_club
    with open('./clubs.json') as f:
        clubs = json.load(f)

    for club in clubs:
        create_club(club)

# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
