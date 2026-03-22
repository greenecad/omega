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
        if 'challenge_id' in request.form:
            challenge_id = int(request.form.get('challenge_id'))
            with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
                challenge = json.load(f)['list'][challenge_id-1]
            if challenge['type'] != 'challenge':
                flash('This challenge cannot be completed in this way.')
                return redirect(url_for('main.profile'))
            db = get_db()
            user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
            completed = json.loads(user['completed'])
            key = str(challenge_id)
            if key in completed['challenges'] and completed['challenges'][key][0] == 'completed':
                flash('Challenge already completed!')
                return redirect(url_for('main.profile'))
            completed['challenges'][key] = ['completed', '']
            db.execute('UPDATE user SET completed = ? WHERE id = ?;', (json.dumps(completed), session['user_id']))
            db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (challenge['points'], session['user_id']))
            db.commit()
            flash('Challenge completed! Points awarded: ' + str(challenge['points']))
            return redirect(url_for('main.profile'))
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
                    if int(row[1])>0:
                        flash('Code accepted! Points awarded: ' + row[1])
                    if len(row) > 2:
                        flash(row[2])
                    break
            if not flag:
                flash('Invalid code!')
        else:
            flash('Code already submitted!')
        return redirect(url_for('main.profile'))
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    notifications = json.loads(user['notifications'])
    popups=[]

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

@main.route('/use_hint/<int:challenge_id>', methods=['POST'])
@login_required
def use_hint(challenge_id):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    completed = json.loads(user['completed'])
    hints_used = json.loads(user['hints_used'])
    if user['hint_count'] <= 0:
        flash('No hints remaining!')
        return redirect(url_for('main.profile'))
    if challenge_id in hints_used['list']:
        flash('Hint already used for this challenge!')
        return redirect(url_for('main.profile'))
    hints_used['list'].append(challenge_id)
    db.execute('UPDATE user SET hints_used = ? WHERE id = ?;', (json.dumps(hints_used), session['user_id']))
    db.execute('UPDATE user SET hint_count = hint_count - 1 WHERE id = ?;', (session['user_id'],))
    db.commit()
    flash('Hint used! Check the challenge description for your hint.')
    return redirect(url_for('main.profile'))



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
        if action == "crash":
            raise Exception('Intentional Crash Triggered by Admin')
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
            hint_count = 3
            if db.execute('SELECT gift FROM user WHERE username = ?;', (username,)).fetchone()[0] == 'knowledge':
                hint_count = 8
            db.execute('UPDATE user SET hint_count = ?, points = 0, completed = ?, hints_used = ? WHERE username = ?;', (hint_count, json.dumps({'challenges': {}, 'codes': []}), json.dumps({'list': []}), username))
            db.commit()
            flash(f'Reset user {username}')
        elif action == 'update_challenge':
            try:
                username = request.form.get('username')
                edited_user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
                notifications = json.loads(edited_user['notifications'])
                challenge_id = int(request.form.get('challenge_id'))
                completed = json.loads(db.execute('SELECT completed FROM user WHERE username = ?;', (username,)).fetchone()[0])
                key = str(challenge_id)
                completed['challenges'][key] = ['completed', completed['challenges'][key][1] if key in completed['challenges'] else '']
                with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
                    challenges = json.load(f)['list']
                    for i in range(len(challenges)):
                        if challenges[i]['id']==challenge_id:
                            challenge_id = i
                            break

                    challenge = challenges[challenge_id]
                challenge_name = challenge['name'] if 'name' in challenge else f'ID {challenge_id}'
                if challenge['points'] == -1:
                    points_awarded = request.form.get('points_awarded')
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {points_awarded} points.', 1])
                    else:
                        notifications.append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {points_awarded} points.', 1])
                    db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (points_awarded, username))
                else:
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {challenge["points"]} points.', 1])
                    else:
                        notifications.append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {challenge["points"]} points.', 1])
                    db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (challenge['points'], username))
                db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
                db.execute('UPDATE user SET notifications = ? WHERE username = ?;', (json.dumps(notifications), username))
                db.commit()
                flash(f'Updated challenge status for user {username}')
            except Exception as e:
                flash('Error updating challenge status: ' + str(e))
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
        if request.form.get('type') == 'challenge':
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
                if challenge['points']==-1:
                    points_awarded = request.form.get('points_awarded')
                    db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (points_awarded, username))
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Your submission for challenge {challenge_id}: "{challenge["name"]}" has been approved! You have been awarded {points_awarded} points.', 1])
                    else:
                        notifications.append([f'Your submission for challenge {challenge_id}: "{challenge["name"]}" has been approved! You have been awarded {points_awarded} points.', 1])
                else:
                    db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (challenge['points'], username))
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Your submission for challenge {challenge_id} has been approved! You have been awarded {challenge['points']} points.', 1])
                    else:
                        notifications.append([f'Your submission for challenge {challenge_id} has been approved! You have been awarded {challenge['points']} points.', 1])

                db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
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
                
        elif request.form.get('type') == 'account':
            username = request.form.get('username')
            action = request.form.get('action')
            user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
            notifications = json.loads(user['notifications'])
            if action == 'approve':
                db.execute('UPDATE user SET participating = 1 WHERE username = ?;', (username,))
                if isinstance(notifications, dict) and "list" in notifications:
                    notifications["list"].append([f'Your account has been approved! You can now participate in the Omega Games.', 1])
                else:
                    notifications.append([f'Your account has been approved! You can now participate in the Omega Games.', 0])
                db.execute('UPDATE user SET notifications = ? WHERE username = ?;', (json.dumps(notifications), username))
                db.commit()
                flash(f'Approved account for user {user["username"]}')
            elif action == 'reject':
                db.execute('DELETE FROM user WHERE username = ?;', (username,))
                if isinstance(notifications, dict) and "list" in notifications:
                    notifications["list"].append([f'Your student ID verification has been rejected. You are not currently participating in the Omega Games. If you believe this is a mistake, please contact OMEGA.', 1])
                else:
                    notifications.append([f'Your student ID verification has been rejected. You are not currently participating in the Omega Games. If you believe this is a mistake, please contact OMEGA.', 1])
                db.commit()
                flash(f'Rejected account for user {user["username"]}')

    #image display is broken??
    users = db.execute('SELECT * FROM user;').fetchall()
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
        challenges = json.load(f)['list']
    return render_template('main/admin_pending.html', users=users, os=os, current_app=current_app, json=json, url_for=url_for, challenges=challenges)




@main.route('friends', methods=['GET', 'POST'])
@login_required
def friends():
    user=get_db().execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/friends.html', user=user, json = json)

@main.route('/submit_friend_request', methods=['GET', 'POST'])
@login_required
def submit_friend_request():
    if request.method == 'POST':
        db = get_db()
        sender_id = session['user_id']
        recipient_username = request.form.get('friend')
        recipient = db.execute('SELECT * FROM user WHERE username = ?;', (recipient_username,)).fetchone()
        username = db.execute('SELECT username FROM user WHERE id = ?;', (sender_id,)).fetchone()[0]
        if not recipient:
            flash('User not found!')
            return redirect(url_for('main.friends'))
        recipient_id = recipient['id']
        if recipient_id == sender_id:
            flash('You cannot send a friend request to yourself!')
            return redirect(url_for('main.friends'))
        existing_requests = json.loads(db.execute('SELECT friend_requests FROM user WHERE id = ?;', (recipient_id,)).fetchone()[0])
        if username in existing_requests['list']:
            flash('Friend request already sent!')
            return redirect(url_for('main.friends'))
        existing_friends = json.loads(db.execute('SELECT friends FROM user WHERE id = ?;', (recipient_id,)).fetchone()[0])
        if username in existing_friends['list']:
            flash('User is already your friend!')
            return redirect(url_for('main.friends'))
        existing_requests['list'].append(username)
        db.execute('UPDATE user SET friend_requests = ? WHERE id = ?;', (json.dumps(existing_requests), recipient_id))
        db.commit()
        flash('Friend request sent to '+recipient_username+'.')
    return redirect(url_for('main.friends'))

@main.route('/accept_friend_request', methods=['GET', 'POST'])
@login_required
def accept_friend_request():
    if request.method =='POST':
        db = get_db()
        id = session['user_id']
        user = db.execute('SELECT * FROM user WHERE id = ?;', (id,)).fetchone()
        requester_username = request.form.get('requester')
        requester = db.execute('SELECT * FROM user WHERE username = ?;', (requester_username,)).fetchone()
        friends = json.loads(user['friends'])
        requester_friends = json.loads(requester['friends'])
        friends['list'].append(requester_username)
        requester_friends['list'].append(user['username'])
        user_requests = json.loads(user['friend_requests'])
        user_requests['list'].remove(requester_username)
        db.execute('UPDATE user SET friends = ? where id = ?', (json.dumps(friends), id))
        db.execute('UPDATE user SET friend_requests = ? where id = ?', (json.dumps(user_requests), id))
        db.execute('UPDATE user SET friends = ? where username = ?', (json.dumps(requester_friends), requester_username))
        flag1=False
        flag2=False
        if len(friends)<=5:
            db.execute('UPDATE user SET points = points + 40 where id = ?', (id,))
            flag1=True
        if len(friends)<=5:
            db.execute('UPDATE user SET points = points + 40 where username = ?', (requester_username,))
            flag2=True
        requester_notifications = json.loads(requester['notifications'])
        if flag2:
            requester_notifications['list'].append(['Your friend request to '+user['username']+' has been accepted. You have earned 40 points.', 1])
        else:
            requester_notifications['list'].append(['Your friend request to '+user['username']+' has been accepted.', 1])
        db.execute('UPDATE user SET notifications = ? where username = ?', (json.dumps(requester_notifications), requester_username))
        db.commit()
        if flag1:
            flash('Friend request accepted from '+requester_username+'. You have earned 40 points.')
        else:
            flash('Friend request accepted from '+requester_username+'.')
        
    return redirect(url_for('main.friends'))

@main.route('/reject_friend_request', methods=["GET", "POST"])
@login_required
def reject_friend_request():
    if request.method == "POST":
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0]
        requester_username = request.form.get('requester')
        requester = db.execute('SELECT * FROM user WHERE username = ?;', (requester_username,))
        user_requests = json.loads(user['friend_requests'])
        user_requests['list'].remove(requester_username)
        db.execute('UPDATE user SET friend_requests = ? where id = ?', (json.dumps(user_requests), id))
        flash("Rejected friend request from "+requester_username+".")
    return redirect(url_for('main.friends'))