import functools
from logging import error

from flask import (
    Blueprint, g, redirect, request, session, url_for, abort, Response
)

from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

from app import db

@bp.route('/register', methods = ("GET", "POST"))
def register():
    from models import User

    if request.method == "POST":
        # Include this mapping because conventions for python var names are not same as for
        # HTML form fields names
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

        # Address errors
        if not username:
            return "Username is required"
        elif not password:
            return Response("Password is required", status = "")  
        elif User.query.filter_by(username = username).first() is not None:
            return f"User {username} is already registered"
        
        user = User(username = username,
                    password = generate_password_hash(password),
                    first_name = first_name,
                    last_name = last_name,
                    email = email) 
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    
    return "Send a post request with username, password, first_name, last_name, and email"

@bp.route('/login', methods = ("GET", "POST"))
def login():
    from models import User

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username = username).first()

        if user is None or not check_password_hash(user.password, password):
            return "Incorrect username or password"
        
        session.clear()
        session['user_id'] = user.id
    
        return redirect(url_for('main'))    

    return f'Visit {url_for("auth.login")} and send POST request with a form data body (hint: "username" is "josh" and "password" is "password!"'


@bp.before_app_request
def load_logged_in_user():
    from models import User
    
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id = user_id).first()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return Response(f'You need to login. Visit {url_for("auth.login")} and send POST request with a form data body (hint: "username" is "josh" and "password" is "password!"', status = 401)
        return view(**kwargs)
    return wrapped_view