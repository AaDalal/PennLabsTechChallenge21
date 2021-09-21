from flask import (
    Blueprint, jsonify, redirect, request, url_for, abort, g, Response
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

from auth import login_required

bp = Blueprint('api', __name__, url_prefix='/api')

def dictify_user(user : object):
    user = user.__dict__
    user.pop('_sa_instance_state')
    
    # Remove password hash so it remains hidden
    user.pop('password')

    # Get the favorite clubs and return their hypermedia links
    favorites = user.pop('favorites')
    user['favorites'] = [url_for('api.get_specific_club', code = favorite.code) for favorite in favorites]

    # Get the associated clubs (ie, clubs in which this user is a member) and return their hypermedia links
    clubs = user.pop('clubs')
    user['clubs'] = [url_for('api.get_specific_club', code = club.code) for club in clubs]
    return user

def dictify_club(club : object):
    club = club.__dict__
    club.pop('_sa_instance_state')
    
    # Handle favorites by collecting the count
    favoriters = club.pop('favoriters')
    club['num_favoriters'] = len(favoriters)
    
    # Handle tags by collecting their names
    tags = club.pop('tags')
    club['tags'] = [tag.name for tag in tags]

    # Handle members by collecting their names
    members = club.pop('members')
    club['members'] = [member.username for member in members]

    return club

def jsonify_clubs(clubs):
    """Takes in a collection of Club objects, dictifies them, then returns a json"""
    dictified_clubs = []
    for club in clubs:
        dictified_clubs.append(dictify_club(club))
    return jsonify(dictified_clubs)

def clubs_search(search_string):
    from models import Club
    clubs = Club.query.filter(Club.name.contains(search_string))
    
    return jsonify_clubs(clubs)

@bp.route('/users/<username>', methods = ("GET",))
def users(username):
    # FIXME: circular imports mean I need to import from within a function
    from models import User
    if not username:
        return User.query.all()

    user = User.query.filter_by(username = username).first()
    user = dictify_user(user)
    return jsonify(user)

@bp.route('/users/<username>', methods = ("PUT",))
@login_required
def update_user(username):
    from models import User
    if not username:
        return User.query.all()

    user = User.query.filter_by(username = username).first()
    if g.user == user:
        # FIXME: This is kind of (very) inelegant. Replace with helper function or loop through each json values
        if request.json.get('first_name') is not None: 
            user.first_name = request.json.get('first_name')
        if request.json.get('last_name') is not None:
            user.last_name = request.json.get('last_name')
        if request.json.get('email') is not None:
            user.email = request.json.get('email')
        if request.json.get('curr_password') is not None and request.json.get('new_password'):
            if check_password_hash(user.password, request.json.get('curr_password')):
                user.password = generate_password_hash(request.json.get('new_password'))
            else:
                return Response('curr_password does not match your current password', status = 401)

        db.session.add(user)
        db.session.commit()
    else:
        return Response('You need to be logged in as the user you are trying to update', status = 401)

    return redirect(url_for('api.users', username = username))

@bp.route('/clubs', methods = ("GET",))
def get_clubs():
    search_string = request.args.get('query')
    if search_string:
        return clubs_search(search_string)

    from models import Club
    clubs = Club.query.all()
    return jsonify_clubs(clubs)

@bp.route('/clubs', methods = ("POST",))
def create_clubs():
    from utils import create_club
    if request.json:
        create_club(request.json)
    elif request.form:
        create_club(dict(request.form))
    else:
        abort(204) # No content if it is in neither form nor json request
    return redirect(url_for('api.get_clubs'), 201) # TODO: add header line with location to created item

@bp.route('/clubs/<code>', methods = ("GET",))
def get_specific_club(code):
    from models import Club
    club = Club.query.filter_by(code = code).first()
    if club is None:
        return abort(404)

    return jsonify(dictify_club(club))

@bp.route('/clubs/<code>', methods = ("PUT",))
@login_required
def update_specific_club(code):
    from models import Club
    club = Club.query.filter_by(code = code).first()

    if not request.json.get('code') == club.code:
        # If ID invalid (ie, not equal to current ID), 404
        return abort(404)

    # Can only update description, name and tags. Anything updated besides these fields will be ignored.
    if request.json.get('description'):
        club.description = request.json.get('description')

    if request.json.get('name'):
        club.name = request.json.get('name')

    if request.json.get('tags'):
        # Delete all existing tags
        club.tags[:] = []

        # Create any new tags or get existing ones and add to the club
        from utils import create_or_return_tag
        for tag_name in request.json.get('tags'):
            tag = create_or_return_tag(tag_name)
            club.append(tag) # NOTE: Check the behavior is valid if tag-club association already exists
    db.session.add(club)
    db.session.commit()

    return redirect(url_for('api.get_specific_club', code = club.code))

@bp.route('/tags', methods = ('GET',))
def tags():
    from models import Tag
    tags = Tag.query.all()
    
    tag_to_club_number = {} 
    for tag in tags:
        tag_to_club_number[tag.name] = len(tag.clubs)
    
    return jsonify(tag_to_club_number)

@bp.route('/users/<username>/favorites/<club_code>', methods = ('GET', 'PUT', 'DELETE'))
def favorites(username, club_code):
    from models import User, Club
    user = User.query.filter_by(username = username).first()
    club = Club.query.filter_by(code = club_code).first() 

    if request.method == 'PUT':
        user.favorites.append(club) # NOTE: users cannot "double-favorite" a club
        db.session.commit()
    elif request.method == 'DELETE':
        if club in user.favorites:
            user.favorites.remove(club)
        db.session.add(user)
        db.session.commit()

    return jsonify(club in user.favorites) # Jsonify a boolean representing if it has been favorited

@bp.route('/users/<username>/joins/<club_code>', methods = ('GET', 'PUT', 'DELETE'))
def joins(username, club_code):
    from models import User, Club
    user = User.query.filter_by(username = username).first()
    club = Club.query.filter_by(code = club_code).first() 

    if request.method == 'PUT':
        request.json.get('membership_type')
        user.clubs.append(club) # NOTE: users cannot "double-favorite" a club
        db.session.commit()
    elif request.method == 'DELETE':
        if club in user.favorites:
            user.clubs.remove(club)
        db.session.add(user)
        db.session.commit()

    return jsonify(club in user.favorites) # Jsonify a boolean representing if it has been favorited
