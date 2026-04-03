from datetime import datetime
import functools, os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if session.get('user_id'):
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['fname']+" "+request.form['lname']
        gift = request.form['gift']
        grade = int(request.form['grade'])
        email = request.form['email']


        
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, name, gift, grade, email) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, generate_password_hash(password), name, gift, grade, email),
                )
                upload_dir = os.path.join(current_app.root_path, "static", "img", "users", username)
                os.makedirs(upload_dir, exist_ok=True)
                id_image = request.files.get('id_image')
                if id_image and id_image.filename:
                    save_path = os.path.join(upload_dir, "id_" + username + "." + id_image.filename.split('.')[-1])
                    id_image.save(save_path)
                    db.execute(
                        "UPDATE user SET id_image = ? WHERE username = ?",
                        ("id_" + username + "." + id_image.filename.split('.')[-1], username),
                    )
                if gift=="knowledge":
                    db.execute(
                        "UPDATE user SET hint_count = hint_count + 5 WHERE username = ?",
                        (username,),
                    )
                if request.form['participate'] == "0":
                    db.execute(
                        "UPDATE user SET participate = -1 WHERE username = ?",
                        (username,),
                    )
                db.commit()

            except db.IntegrityError:
                error = f"Username or email is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html', datetime=datetime)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if session.get('user_id'):
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('main.profile'))

        flash(error)

    return render_template('auth/login.html', datetime=datetime)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@login_required
@bp.route('/upload_id', methods=('POST',))
def upload_id():
    if request.method=="POST":
        db=get_db()
        username = db.execute(
            "SELECT username FROM user WHERE id = ?", (session['user_id'],)
        ).fetchone()[0]
        
        
        id_image = request.files.get('id_image')
        if id_image and id_image.filename:
            try:
                upload_dir = os.path.join(current_app.root_path, "static", "img", "users", username)
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, "id_" + username + "." + id_image.filename.split('.')[-1])
                id_image.save(save_path)
                db.execute(
                    "UPDATE user SET id_image = ? WHERE username = ?",
                    ("id_" + username + "." + id_image.filename.split('.')[-1], username),
                )
                db.commit()
                flash('ID image uploaded successfully! Please wait while it is verified.')
            except Exception as e:
                flash('error uploading image. Please try again, or contact Omega if the problem persists: ')
                flash(e)
    return redirect(url_for('main.profile'))
    