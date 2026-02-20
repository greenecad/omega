import csv
from flask import render_template, Blueprint, session, url_for, current_app, request, redirect, flash
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
    db = get_db()
    if request.method == 'POST':
        code = request.form['code']
        completed = json.loads(db.execute('SELECT completed FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0])
        with open(os.path.join(current_app.static_folder, 'codes.csv'), 'r') as file:
            codes = list(csv.reader(file))
        if code not in completed['codes']:
            flag=False
            for row in codes:
                if row[0] == code:
                    db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (row[1], session['user_id']))
                    completed['codes'].append(code)
                    db.execute('UPDATE user SET completed = ? WHERE id = ?;', (json.dumps(completed), session['user_id']))
                    db.commit()
                    flag=True
                    flash('Code accepted! Points awarded: ' + row[1])
                    break
            if not flag:
                flash('Invalid code!')
        else:
            flash('Code already submitted!')
        return redirect(url_for('main.profile'))
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
        challenges = json.load(f)

    
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/profile.html', user=user, challenges=challenges['list'], datetime=datetime, json=json )

@main.route('/submission/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
def submission(challenge_id):
    if request.method == 'POST':
        submission = request.files['submission']
        if submission:
            pass #temp
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
        challenge = json.load(f)['list'][challenge_id-1]

    return render_template('main/submission.html', challenge=challenge)
