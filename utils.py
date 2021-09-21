""" 
Utilities used across api.py and bootstrap.py primarily for creating database entries from data 
"""
from app import db

def create_club(club : dict):
    """Creates a club from a dictionary of data if it does not already exist. If it does exist, raise error.
    """   
    from models import Club

    tags = []
    if club.get('tags'):
        tags = club.pop('tags') # Remove tags from the club dictionary and store it seperately
    
    new_club = Club(**club) # Unpack club dictionary into ORM

    for tag_name in tags:
        # Create tag (if it does not exist)
        tag = create_or_return_tag(tag_name)
        # Create a mapping between club and tag
        new_club.tags.append(tag)

    # SQLalchemy raises error if already exists    
    db.session.add(new_club)
    db.session.commit()
    return new_club

def create_or_return_tag(tag_name):
    """Create a tag if it does not already exist, otherwise return the tag"""
    from models import Tag
    # Check if tag does not already exist, create it; otherwise, get its row
    tag = Tag.query.filter_by(name = tag_name).first()
    if tag is None:
        tag = Tag(name = tag_name)

        db.session.add(tag)
        db.session.commit()
    return tag