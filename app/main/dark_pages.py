from flask import render_template, Blueprint, session, url_for, current_app, request, redirect, flash

from .db import get_db
from .auth import login_required
import json, csv

dark = Blueprint(
    'dark',
    __name__,
    template_folder='templates/dark_pages',
    url_prefix='/dev/bin/72686F636F6E7461696E6572'
)

@dark.route('/', methods= ['GET', 'POST'])
@login_required
def dark_main():
    user= get_db().execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    artifact_pieces = json.loads(user['artifact_pieces']) if user['artifact_pieces'] else {"list": []}
    piece_count = str(len(artifact_pieces["list"]))
    return render_template("dark_pages/index.html", user = user, piece_count = piece_count)

@dark.route('/tapes', methods= ['GET', 'POST'])
@login_required
def tapes():
    db = get_db()
    user= db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if user["tapes"] == None:
        tapes = {"list": []}
        db.execute('UPDATE user SET tapes = ? WHERE id = ?;', (json.dumps(tapes), session['user_id']))
        db.commit()
    else:
        try:
            tapes = json.loads(user['tapes'])
        except json.JSONDecodeError:
            tapes = {"list": []}
            db.execute('UPDATE user SET tapes = ? WHERE id = ?;', (json.dumps(tapes), session['user_id']))
            db.commit()
    with open(current_app.static_folder + "/all_tapes.json", "r") as f:
        all_tapes = json.load(f)
    collected_tapes = []
    for tape in tapes["list"]:
        tape = all_tapes.get(tape, "error: tape not found")
        collected_tapes.append(tape)
    return render_template("dark_pages/tapes.html", tapes = collected_tapes)

@dark.route('/collect_tape', methods= ['POST', 'GET'])
@login_required
def collect_tape():
    if request.method == 'POST':
        tape_id = request.form.get('tape_id')
        db = get_db()
        user= db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
        if user["tapes"] == None:
            tapes = {"list": []}
        else:
            try:
                tapes = json.loads(user['tapes'])
            except json.JSONDecodeError:
                tapes = {"list": []}
        if tape_id not in tapes["list"]:
            tapes["list"].append(tape_id)
            db.execute('UPDATE user SET tapes = ? WHERE id = ?;', (json.dumps(tapes), session['user_id']))
            db.commit()
    return redirect(url_for('dark.tapes'))

@dark.route('/657965', methods= ['GET', 'POST'])
@login_required
def eye():
    return render_template("dark_pages/eye.html")

@dark.route('/6C6F7374', methods= ['GET', 'POST'])
@login_required
def maze():
    return render_template("dark_pages/maze.html")

@dark.route('/676F64', methods= ['GET', 'POST'])
@login_required
def god():
    return render_template("dark_pages/god.html")

@dark.route('/7468696E67', methods= ['GET', 'POST'])
@login_required
def thing():
    db = get_db()
    user= db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template("dark_pages/thing.html", user= user)

@dark.route('/collect_artifact_piece', methods= ['POST', 'GET'])
@login_required
def collect_artifact_piece():
    if request.method == 'POST':
        piece_id = request.form.get('piece_id')
        db = get_db()
        user= db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
        if user["artifact_pieces"] == None:
            pieces = {"list": []}
        else:
            try:
                pieces = json.loads(user['artifact_pieces'])
            except json.JSONDecodeError:
                pieces = {"list": []}
        if piece_id not in pieces["list"]:
            pieces["list"].append(piece_id)
            db.execute('UPDATE user SET artifact_pieces = ? WHERE id = ?;', (json.dumps(pieces), session['user_id']))
            db.commit()
            flash("You find a strange artifact piece. You put it somewhere safe for later.")
        return_url = request.form.get('return_url')
        if return_url:
            return redirect(url_for(return_url))
    return redirect(url_for('main.profile'))