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
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    notifications = json.loads(user['notifications'])
    popups=[]

    ## todo: fix modal popups not appearing at all
    for notification in notifications["list"]:
        if notification[1] == 0:
            flash(notification[0])
        elif notification[1] == 1:
            popups.append(notification[0])
    notifications["list"] = []
    db.execute('UPDATE user SET notifications = ? WHERE id = ?;', (json.dumps(notifications), session['user_id']))
    db.commit()
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
        challenges = json.load(f)
    
    return render_template('main/profile.html', user=user, challenges=challenges['list'], datetime=datetime, json=json, popups=popups) 

@main.route('/submission/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
def submission(challenge_id):
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
        challenge = json.load(f)['list'][challenge_id-1]
    if challenge['type'] != 'submission':
        flash('This challenge does not require a submission.')
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        submission = request.files['submission']
        db=get_db()
        username = db.execute('SELECT username FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0]
        if submission:
            completed = json.loads(db.execute('SELECT completed FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0])
            key = str(challenge_id)
            if key in completed['challenges'] and (completed['challenges'][key][0] == 'completed' or completed['challenges'][key][0] == 'pending') and ("repeats" not in challenge or not challenge["repeats"] == True):
                flash('Challenge already completed!')
                return redirect(url_for('main.profile'))
            try:
                upload_dir = os.path.join(current_app.root_path, "static", "img", "users", username, "submissions")
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, "challenge_" + str(challenge_id) + "_" + username + "." + submission.filename.split('.')[-1])
                submission.save(save_path)
                completed['challenges'][key] = ['pending', "challenge_" + str(challenge_id) + "_" + username + "." + submission.filename.split('.')[-1]]
                db.execute('UPDATE user SET completed = ? WHERE id = ?;', (json.dumps(completed), session['user_id']))
                db.commit()
                flash('Submission received! It will be reviewed by OMEGA soon.')
                return redirect(url_for('main.profile'))
            except Exception as e:
                flash('Error saving submission: ' + str(e))
                return redirect(url_for('main.profile'))
    

    return render_template('main/submission.html', challenge=challenge)

@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if not user or user['admin'] != 1:
        flash('What are you doing? OMEGA would not be proud of you.')
        return redirect(url_for('main.profile'))
    
    if request.method == 'POST':
        action = request.form.get('admin_action')
        if action == 'update_user':
            try:
                username = request.form.get('username')
                column = request.form.get('column')
                value = request.form.get('points')
                db.execute(f'UPDATE user SET {column} = ? WHERE username = ?;', (value, username))
                db.commit()
                flash(f'Updated {column} for user {username} to {value}')
            except Exception as e:
                flash('Error updating user: ' + str(e))
        elif action == 'reset_user':
            username = request.form.get('username')
            db.execute('UPDATE user SET points = 0, completed = ? WHERE username = ?;', (json.dumps({'challenges': {}, 'codes': []}), username))
            db.commit()
            flash(f'Reset user {username}')
    return redirect(url_for('main.profile'))

@main.route('/admin/pending', methods=['GET', 'POST'])
@login_required
def admin_pending():
    
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if not user or user['admin'] != 1:
        flash('What are you doing? OMEGA would not be proud of you.')
        return redirect(url_for('main.profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        challenge_id = int(request.form.get('challenge_id'))
        key = str(challenge_id)
        action = request.form.get('action')
        user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
        completed = json.loads(user['completed'])
        notifications = json.loads(user['notifications'])

        if action == 'approve':
            with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
                challenge = json.load(f)['list'][challenge_id-1]
            completed['challenges'][key][0] = 'completed'
            if isinstance(notifications, dict) and "list" in notifications:
                notifications["list"].append([f'Your submission for challenge {challenge_id} has been approved! You have been awarded {challenge["points"]} points.', 0])
            else:
                notifications.append([f'Your submission for challenge {challenge_id} has been approved! You have been awarded {challenge["points"]} points.', 0])
            db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
            db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (challenge['points'], username))
            db.execute('UPDATE user SET notifications = ? WHERE username = ?;', (json.dumps(notifications), username))
            db.commit()
            flash(f'Approved submission for user {user["username"]} on challenge {challenge["name"]}')
        elif action == 'reject':
            if key in completed['challenges']:
                del completed['challenges'][key]
            if isinstance(notifications, dict) and "list" in notifications:
                notifications["list"].append([f'Your submission for challenge {challenge_id} has been rejected. Please try again.', 0])
            else:
                notifications.append([f'Your submission for challenge {challenge_id} has been rejected. Please try again.', 0])
            db.execute('UPDATE user SET notifications = ? WHERE username = ?;', (json.dumps(notifications), username))
            db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
            db.commit()
            flash(f'Rejected submission for user {user["username"]} on challenge {challenge_id}')

    users = db.execute('SELECT username, completed FROM user;').fetchall()
    return render_template('main/admin_pending.html', users=users, os=os, current_app=current_app, json=json, url_for=url_for)