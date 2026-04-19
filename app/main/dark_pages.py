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
    return render_template("dark_pages/index.html", user = user)

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
        tapes = json.loads(user['tapes'])
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
            tapes = json.loads(user['tapes'])
        if tape_id not in tapes["list"]:
            tapes["list"].append(tape_id)
            db.execute('UPDATE user SET tapes = ? WHERE id = ?;', (json.dumps(tapes), session['user_id']))
            db.commit()
    return redirect(url_for('dark.tapes'))

@dark.route('/eye', methods= ['GET', 'POST'])
@login_required
def eye():
    return render_template("dark_pages/eye.html")

@dark.route('/maze', methods= ['GET', 'POST'])
@login_required
def maze():
    return render_template("dark_pages/maze.html")

@dark.route('/god', methods= ['GET', 'POST'])
@login_required
def god():
    return render_template("dark_pages/god.html")

@dark.route('/thing', methods= ['GET', 'POST'])
@login_required
def thing():
    return render_template("dark_pages/thing.html")