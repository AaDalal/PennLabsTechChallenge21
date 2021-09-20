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
    with open('./clubs.json') as f:
        clubs = json.load(f)

    for club in clubs:
        create_club(club)

def create_tag(tag_name):
    """Create a tag if it does not already exist, otherwise return the tag"""
    from models import Tag
    # Check if tag does not already exist, create it; otherwise, get its row
    tag = Tag.query.filter_by(name = tag_name).first()
    if tag is None:
        tag = Tag(name = tag_name)

        db.session.add(tag)
        db.session.commit()
    return tag
        
def create_club(club : dict):
    """Creates a club from a dictionary of data"""   
    from models import Club
    
    tags = []
    if club.get('tags'):
        tags = club.pop('tags') # Remove tags from the club dictionary and store it seperately
    
    new_club = Club(**club) # Unpack club dictionary into ORM

    for tag_name in tags:
        # Create tag (if it does not exist)
        tag = create_tag(tag_name)

        # Create a mapping between club and tag
        new_club.tags.append(tag)
        db.session.add(new_club)
        db.session.commit()
    return new_club

# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
