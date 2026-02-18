import csv
from flask import render_template, Blueprint, session, url_for, current_app, request, redirect
import os
from .db import get_db
from .auth import login_required
import json, csv
from datetime import datetime
main = Blueprint(
    'main',
    __name__,
    template_folder='templates/main',
    url_prefix='/'
)


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')

@main.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    db = get_db()
    users = db.execute('SELECT username, points FROM user WHERE participating = 1 ORDER BY points DESC;').fetchall()
    return render_template('main/leaderboard.html', users=users)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        code = request.form['code']
        with open(os.path.join(current_app.static_folder, 'codes.csv'), 'r') as file:
            codes = list(csv.reader(file))
        for row in codes:
            if row[0] == code:
                db = get_db()
                db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (row[1], session['user_id']))
                db.commit()
                break
        return redirect(url_for('main.profile'))
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
        challenges = json.load(f)

    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/profile.html', user=user, challenges=challenges['list'], datetime=datetime )
