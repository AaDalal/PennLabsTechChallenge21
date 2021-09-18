from app import db

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

# Tag-club join table
tag_to_club = db.Table('tag_club_association',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key = True, nullable = False),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key = True, nullable = False) # NOTE: club.id is a valid identifier because SQLite table names are case-insensitive
    )

# User-club join table
user_to_club = db.Table('user_club_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True, nullable = False),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key = True, nullable = False) # NOTE: club.id is a valid identifier because SQLite table names are case-insensitive
    )
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    username = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text)
    clubs = db.relationship("Club", secondary = user_to_club, lazy = 'subquery', back_populates = "members")

class Club(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False) 
    code = db.Column(db.String(100), nullable = False)
    name = db.Column(db.String(200), nullable = False)
    description = db.Column(db.Text)
    members = db.relationship("User", secondary = user_to_club, lazy = 'subquery', back_populates = "clubs")
    tags = db.relationship("Tag", secondary = tag_to_club, lazy = 'subquery', back_populates = "clubs")


class Tag(db.model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(100), nullable = False, unique = True)
    clubs =  db.relationship("Club", secondary = tag_to_club, lazy = 'subquery', back_populates = "tags") 