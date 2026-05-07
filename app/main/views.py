import csv
import random
from flask import render_template, Blueprint, session, url_for, current_app, request, redirect, flash
import os

from app.main.functions import set_challenge_completed
from .db import get_db
from .auth import login_required, check_takeover
import json, csv
from datetime import datetime, timezone, timedelta
from urllib import parse

from werkzeug.security import generate_password_hash
main = Blueprint(
    'main',
    __name__,
    template_folder='templates/main',
    url_prefix='/'
)


def parse_release_datetime(release_str, default_tz):
    if not release_str:
        return datetime.max.replace(tzinfo=default_tz)

    normalized = release_str.strip()
    if normalized.endswith('Z'):
        normalized = normalized[:-1] + '+00:00'

    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=default_tz)

    return parsed.astimezone(default_tz)


@main.route('/', methods=['GET', 'POST'])
@check_takeover
def index():
    return render_template('main/index.html', datetime=datetime)

@main.route('/leaderboard', methods=['GET', 'POST'])
@check_takeover
def leaderboard():
    db = get_db()
    users = db.execute('SELECT username, points, pfp FROM user WHERE participating = 1 ORDER BY points DESC;').fetchall()
    if session.get('user_id'):
        current_user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/leaderboard.html', users=users, datetime=datetime, parse=parse, json=json, current_user=current_user if session.get('user_id') else None)

@main.route('/profile', methods=['GET', 'POST'])
@check_takeover
@login_required
def profile():
    app_timezone = timezone(timedelta(hours=-6))
    db = get_db()
    if request.method == 'POST':
        if 'challenge_id' in request.form:
            taken_points = -1
            #remember to change these when challenges are reordered
            if request.form.get('challenge_id') == '15': #the button
                flash('Challenge currently unavailable. Stay tuned for updates!')
                return redirect(url_for('main.profile')) 
                user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
                click_points = user['click_points']
                print(request.form.to_dict(flat=False))
                new_click_points = request.form.get('clickPoints')
                print(new_click_points)
                if int(new_click_points) > click_points:
                    db.execute('UPDATE user SET click_points = ? WHERE id = ?;', (new_click_points, session['user_id']))
                    db.execute('UPDATE user SET points = points + ? WHERE id = ?;', ((int(new_click_points)-click_points) * 10, session['user_id']))
                    db.commit()
                    flash(f'You earned {(int(new_click_points)-click_points) * 10} points!')
                return redirect(url_for('main.profile'))
            elif request.form.get('challenge_id')=='24': #give points
                username = request.form.get('username')
                send_user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
                if send_user:
                    if send_user['id'] == session['user_id']:
                        flash('You cannot give points to yourself!')
                        return redirect(url_for('main.profile'))
                    if user['participating'] != 1:
                        flash('You must be an active participant to give points!')
                        return redirect(url_for('main.profile'))
                    if send_user['participating'] != 1:
                        flash('You cannot give points to a user who is not participating!')
                        return redirect(url_for('main.profile'))
                    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
                    db.execute('UPDATE user SET points = points + 150 WHERE id = ?;', (send_user['id'],))
                    db.commit()
                    flash(f'Sent 150 points to {username}!')
                else:
                    flash('User not found.')
                    return redirect(url_for('main.profile'))
            elif request.form.get('challenge_id')=='30': #steal points
                username = request.form.get('username')
                send_user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
                if send_user:
                    if send_user['id'] == session['user_id']:
                        flash('You cannot take points from yourself!')
                        return redirect(url_for('main.profile'))
                    if send_user['participating'] != 1:
                        flash('You cannot take points from a user who is not participating!')
                        return redirect(url_for('main.profile'))
                    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
                    friends = json.loads(send_user['friends'])['list']
                    if user['username'] not in friends:
                        flash('You can only take points from your friends! Sorry, it has to be done...')
                        return redirect(url_for('main.profile'))
                    taken_points = 100
                    if send_user['gift'] == 'vigilance':
                        taken_points -= 50
                    if user['gift'] == 'competitiveness':
                        taken_points += 50
                    taken_points = min(taken_points, send_user['points'])
                    db.execute('UPDATE user SET points = points - ? WHERE id = ?;', (taken_points, send_user['id']))
                    db.commit()
                    flash(f'Took {taken_points} points from {username}!')
                else:
                    flash('User not found.')
                    return redirect(url_for('main.profile'))
            elif request.form.get('challenge_id') == '18':  #Assassination
                try:
                    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
                    if user is None:
                        flash('User not found.')
                        return redirect(url_for('main.profile'))
                    if user['participating'] != 1:
                        flash('This challenge is only available to active participants. Verify your account first.')
                        return redirect(url_for('main.profile'))
                    if user['target'] is None:
                        with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
                            challenge_list = json.load(f)['list']

                        school_spirit = next((c for c in challenge_list if c.get('name') == 'School spirit'), None)
                        if school_spirit is None:
                            current_app.logger.error('Assassination target assignment failed: School spirit challenge not found')
                            flash('Challenge configuration error. Please contact an admin.')
                            return redirect(url_for('main.profile'))

                        school_spirit_id = str(school_spirit['id'])
                        all_users = db.execute('SELECT * FROM user WHERE participating = 1;').fetchall()
                        all_users = [u for u in all_users if u['id'] != user['id']]
                        all_users = [u for u in all_users if u['targeted_by'] is None]
                        all_users = [u for u in all_users if user['targeted_by'] != u['username']]
                        all_users = [u for u in all_users if abs(u['grade'] - user['grade']) <= 1]
                        all_users = [u for u in all_users if u['grade'] != 9 or user['grade']==u['grade']]
                        friends_list = json.loads(user['friends'])['list']
                        all_users = [u for u in all_users if u['username'] not in friends_list]
                        
                        # Filter users who have completed school spirit challenge with nested error handling
                        filtered_users = []
                        for u in all_users:
                            try:
                                completed = json.loads(u['completed'])
                                try:
                                    challenge_data = completed['challenges'].get(school_spirit_id, [['incomplete']])
                                    try:
                                        if challenge_data[0][0] == 'completed':
                                            filtered_users.append(u)
                                    except (IndexError, TypeError):
                                        # Data structure doesn't match expected format, skip user
                                        pass
                                except (KeyError, TypeError):
                                    # 'challenges' key missing or not dict, skip user
                                    pass
                            except (json.JSONDecodeError, ValueError):
                                # Invalid JSON in completed field, skip user
                                pass
                        all_users = filtered_users

                        if len(all_users) == 0:
                            flash('No valid targets available at this time. Try again later!')
                            return redirect(url_for('main.profile'))

                        import random
                        target = random.choice(all_users)
                        target_completed_entry = json.loads(target['completed'])['challenges'].get(school_spirit_id, [['incomplete', '']])
                        target_pic = target_completed_entry[0][1] if len(target_completed_entry[0]) > 1 else ''
                        db.execute('UPDATE user SET target = ?, target_pic = ? WHERE id = ?;', (target['username'], target_pic, user['id']))
                        u_notes = json.loads(user['notifications'])
                        u_notes["list"].append([f'Your target is {target["username"]}. A picture of them has been provided in the challenge description. Find them.', 1])
                        db.execute('UPDATE user SET notifications = ? WHERE id = ?;', (json.dumps(u_notes), user['id']))
                        db.execute('UPDATE user SET targeted_by = ? WHERE id = ?;', (user['username'], target['id']))
                        t_notes = json.loads(target['notifications'])
                        if target['gift'] == 'vigilance':
                            t_notes["list"].append([f'You\'re overtaken by a terrible feeling... Someone is hunting you. Don\'t let them catch you.\n Vigilance: the name of your pursuer is {user["username"]}', 1])
                        else:
                            t_notes["list"].append([f'A terrible feeling comes over you... Someone is hunting you. Don\'t let them catch you.', 1])
                        db.execute('UPDATE user SET notifications = ? WHERE id = ?;', (json.dumps(t_notes), target['id']))
                        db.commit()
                    return redirect(url_for('main.profile'))
                except Exception:
                    current_app.logger.exception('Error handling assassination challenge for user_id=%s', session.get('user_id'))
                    flash('An error occurred while assigning your target. Please try again.')
                    return redirect(url_for('main.profile'))

            challenge_id = int(request.form.get('challenge_id'))
            task_completed = request.form.get('completed')
            with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
                challenge_list = json.load(f)['list']
                challenge = next((item for item in challenge_list if item.get('id') == challenge_id), None)
            if challenge is None:
                current_app.logger.error('Profile POST requested unknown challenge_id=%s by user_id=%s', challenge_id, session.get('user_id'))
                flash('Invalid challenge selected.')
                return redirect(url_for('main.profile'))
            if challenge['type'] != 'challenge':
                flash('This challenge cannot be completed in this way.')
                return redirect(url_for('main.profile'))
            db = get_db()
            user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
            completed = json.loads(user['completed'])
            key = str(challenge_id)
            if challenge_id == 999 and task_completed == '0':
                return redirect(url_for('main.sans'))
            if challenge_id == 32 and task_completed == '0':
                return redirect(url_for('main.messages'))
            if challenge_id == 13 and task_completed == '0':
                return redirect(url_for('main.platforming'))
            if challenge_id == 27 and task_completed == '0':
                return redirect(url_for('main.target_practice'))
            if challenge_id == 29 and task_completed == '0':
                return redirect(url_for('main.gambling'))
            if key in completed['challenges'] and completed['challenges'][key][0] == 'completed':
                flash('Challenge already completed!')
                return redirect(url_for('main.profile'))
            if task_completed == '1':
                challenge = set_challenge_completed(challenge_id, taken_points=taken_points)
                if challenge is None:
                    flash('An error occurred while completing the challenge. Please try again.')
                    return redirect(url_for('main.profile'))
                ##completed['challenges'][key] = ['completed', '']
                ##db.execute('UPDATE user SET completed = ? WHERE id = ?;', (json.dumps(completed), session['user_id']))
                if taken_points != -1:
                    ##db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (taken_points, session['user_id']))
                    flash('Challenge completed! Points awarded: ' + str(taken_points))
                else:
                    ##db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (challenge['points'], session['user_id']))
                    flash('Challenge completed! Points awarded: ' + str(challenge['points']))
                db.commit()
            
            if task_completed == '0':
                flash('Challenge not completed. Try again!')

            return redirect(url_for('main.profile'))
        code = request.form['code']
        completed = json.loads(db.execute('SELECT completed FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0])
        with open(os.path.join(current_app.static_folder, 'codes.csv'), 'r', encoding='utf-8') as file:
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
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
        challenges = json.load(f)

    for challenge in challenges['list']:
        challenge['release_dt'] = parse_release_datetime(challenge.get('release'), app_timezone)
    
    return render_template('main/profile.html', user=user, challenges=challenges['list'], datetime=datetime, json=json, popups=popups, timezone=app_timezone, current_time=datetime.now(app_timezone)) 

@main.route('/profile/<username>', methods=['GET'])
def view_profile(username):
    app_timezone = timezone(timedelta(hours=-5))
    username = parse.unquote(username)
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
    if not user:
        flash('User not found!')
        return redirect(url_for('main.profile'))
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
        challenges = json.load(f)

    for challenge in challenges['list']:
        challenge['release_dt'] = parse_release_datetime(challenge.get('release'), app_timezone)
    current_user = None
    if session.get('user_id'):
        current_user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/view_profile.html', user=user, challenges=challenges['list'], datetime=datetime, json=json, timezone=app_timezone, current_time=datetime.now(app_timezone), current_user=current_user)

@main.route('/submission/<int:challenge_id>', methods=['GET', 'POST'])
@login_required
def submission(challenge_id):
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
        challenge = next((item for item in json.load(f)['list'] if item.get('id') == challenge_id), None)
    if challenge['type'] != 'submission':
        flash('This challenge does not require a submission.')
        return redirect(url_for('main.profile'))
    db=get_db()
    username = db.execute('SELECT username FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0]
    completed = json.loads(db.execute('SELECT completed FROM user WHERE id = ?;', (session['user_id'],)).fetchone()[0])
    key = str(challenge_id)
    if key in completed['challenges'] and (("repeats" not in challenge or not challenge["repeats"]) and (len(completed['challenges'][key])>1) and (completed['challenges'][key][0][0] == 'completed' or completed['challenges'][key][0][0] == 'pending') or (challenge.get('submissions', 1) == len(completed['challenges'][key]))):
        flash('Challenge already completed!')
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        submission = request.files['submission']
        if submission:
            try:
                upload_dir = os.path.join(current_app.root_path, "static", "img", "users", username, "submissions")
                os.makedirs(upload_dir, exist_ok=True)
                i = 0
                while os.path.exists(os.path.join(upload_dir, "challenge_" + str(challenge_id) + "_" + username + "_" + str(i) + "." + submission.filename.split('.')[-1])):
                    i += 1
                save_path = os.path.join(upload_dir, "challenge_" + str(challenge_id) + "_" + username + "_" + str(i) + "." + submission.filename.split('.')[-1])
                submission.save(save_path)
                if not completed['challenges'].get(key):
                    completed['challenges'][key] = []
                allows_repeats = challenge.get('repeats', False)
                max_submissions = challenge.get('submissions', 1)
                if len(completed['challenges'][key]) > 0 and (not allows_repeats) or (max_submissions == len(completed['challenges'][key])):
                    flash('You have already submitted for this challenge the maximum number of times!')
                    return redirect(url_for('main.profile'))
                completed['challenges'][key].append(['pending', "challenge_" + str(challenge_id) + "_" + username + "_" + str(i) + "." + submission.filename.split('.')[-1]])
                db.execute('UPDATE user SET completed = ? WHERE id = ?;', (json.dumps(completed), session['user_id']))
                db.commit()
                flash('Submission received! It will be reviewed by OMEGA soon.')
                return redirect(url_for('main.profile'))
            except Exception as e:
                flash('Error saving submission: ' + str(e))
                return redirect(url_for('main.profile'))
    

    return render_template('main/submission.html', challenge=challenge, datetime=datetime)

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


#admin routes
#probably shouldve put these in a separate blueprint but oh well

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
        elif action == 'reset_target':
            try:
                target_username = request.form.get('target_username')
                target_user = db.execute('SELECT * FROM user WHERE username = ?;', (target_username,)).fetchone()
                if target_user is None:
                    flash('Target user not found!')
                    return redirect(url_for('main.profile'))
                target= db.execute('SELECT target FROM user WHERE username = ?;', (target_username,)).fetchone()[0]
                if target:
                    db.execute('UPDATE user SET targeted_by = NULL WHERE username = ?;', (target,))
                db.execute('UPDATE user SET target = NULL, target_pic = NULL WHERE username = ?;', (target_username,))
                db.commit()
                flash(f'Assassination target reset for {target_username}.')
            except Exception as e:
                flash('Error resetting target: ' + str(e))
        elif action == 'reset_targets':
            try:
                db.execute('UPDATE user SET target = NULL, target_pic = NULL, targeted_by = NULL;')
                db.commit()
                flash('All assassination targets have been reset.')
            except Exception as e:
                flash('Error resetting targets: ' + str(e))
        elif action == 'update_user':
            try:
                username = request.form.get('username')
                column = request.form.get('column')
                value = request.form.get('points')
                pvalue = None
                if column == "password":
                    pvalue = value
                    value = generate_password_hash(value)

                db.execute(f'UPDATE user SET {column} = ? WHERE username = ?;', (value, username))
                db.commit()
                flash(f'Updated {column} for user {username} to {pvalue if pvalue is not None else value}')
            except Exception as e:
                flash('Error updating user: ' + str(e))
        elif action == 'add_column':
            try:
                column_name = request.form.get('column_name')
                column_type = request.form.get('column_type')
                if request.form.get('column_default') is None or request.form.get('column_default').strip() == '':
                    db.execute(f'ALTER TABLE user ADD COLUMN {column_name} {column_type};')
                    flash(f'Added column {column_name} of type {column_type} to user table.')

                if column_default := request.form.get('column_default'):
                    escaped = column_default.replace("'", "''")
                    db.execute(
                        f"ALTER TABLE user ADD COLUMN {column_name} {column_type} DEFAULT '{escaped}';"
                    )
                    flash(f'Added column {column_name} of type {column_type} to user table with default {column_default}.')

                db.commit()
            except Exception as e:
                flash('Error adding column: ' + str(e))
        elif action == 'reset_user':
            try:
                username = (request.form.get('username') or '').strip()
                if not username:
                    flash('Please provide a username to reset.')
                    return redirect(url_for('main.admin'))

                target_user = db.execute('SELECT gift FROM user WHERE username = ?;', (username,)).fetchone()
                if target_user is None:
                    flash('User not found!')
                    return redirect(url_for('main.admin'))

                hint_count = 10 if target_user['gift'] == 'knowledge' else 5
                target = db.execute('SELECT target FROM user WHERE username = ?;', (username,)).fetchone()[0]
                if target:
                    db.execute('UPDATE user SET targeted_by = NULL WHERE username = ?;', (target,))
                targeted_by = db.execute('SELECT targeted_by FROM user WHERE username = ?;', (username,)).fetchone()[0]
                if targeted_by:
                    db.execute('UPDATE user SET target = NULL WHERE username = ?;', (targeted_by,))
                db.execute(
                    "UPDATE user SET hint_count = ?, points = 0, completed = ?, hints_used = ?, target= NULL, targeted_by = NULL, target_pic = NULL, click_points = 0, percentage = NULL, artifact_pieces = '{\"list\": []}', friends = '{\"list\": []}', friend_requests = '{\"list\": []}', hints_used = '{\"list\": []}', tapes = '{\"list\": []}', platform_hi = 0, target_hi = 0 WHERE username = ?;",
                    (hint_count, json.dumps({'challenges': {}, 'codes': []}), json.dumps({'list': []}), username),
                )
                db.commit()
                flash(f'Reset user {username}')
            except Exception as e:
                current_app.logger.exception('Error resetting user: %s', username if 'username' in locals() else 'unknown')
                flash('Error resetting user: ' + str(e))
        elif action == 'delete_user':
            username = request.form.get('username')
            if(db.execute('SELECT username FROM user WHERE username = ?;', (username,)).fetchone() is None):
                flash('User not found!')
                return redirect(url_for('main.admin'))
            db.execute('DELETE FROM user WHERE username = ?;', (username,))
            user_dir = os.path.join(current_app.root_path, "static", "img", "users", username)
            if os.path.exists(user_dir):
                for root, dirs, files in os.walk(user_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.removedirs(user_dir)
            db.commit()
            flash(f'Deleted user {username}')
        elif action == 'activate_live':
            try:
                challenge_id = int(request.form.get('challenge_id'))
                with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
                    challenge_json = json.load(f)
                    challenges = challenge_json['list']
                    for i in range(len(challenges)):
                        if challenges[i]['id']==challenge_id:
                            challenge_id = i
                            break

                    challenge = challenges[challenge_id]
                if challenge['type'] != 'live':
                    flash('Challenge is not a live event!')
                    return redirect(url_for('main.admin'))
                challenge_json['list'][challenge_id]['event_code'] = request.form.get('event_code')
                with open(os.path.join(current_app.static_folder, 'challenges.json'), 'w', encoding='utf-8') as f:
                    f.write(json.dumps(challenge_json, indent=4))
                flash(f'Activated live event for challenge {challenge["name"]} (ID {challenge["id"]}) with code: {challenge_json["list"][challenge_id]["event_code"]}')
            except Exception as e:
                flash('Error activating live event: ' + str(e))
        elif action == 'global_notification':
            try:
                message = request.form.get('message')
                users = db.execute('SELECT * FROM user;').fetchall()
                for user in users:
                    notifications = json.loads(user['notifications'])
                    notifications["list"].append([message, 1])
                    db.execute('UPDATE user SET notifications = ? WHERE id = ?;', (json.dumps(notifications), user['id']))
                db.commit()
                flash('Sent global notification: ' + message)
            except Exception as e:
                flash('Error sending global notification: ' + str(e))
        elif action == 'individual_notification':
            try:
                username = request.form.get('username')
                message = request.form.get('message')
                user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
                if user:
                    notifications = json.loads(user['notifications'])
                    notifications["list"].append([message, 1])
                    db.execute('UPDATE user SET notifications = ? WHERE id = ?;', (json.dumps(notifications), user['id']))
                db.commit()
                flash('Sent individual notification: ' + message)
            except Exception as e:
                flash('Error sending individual notification: ' + str(e))
        elif action == 'update_challenge':
            try:
                username = request.form.get('username')
                edited_user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()
                notifications = json.loads(edited_user['notifications'])
                challenge_id = int(request.form.get('challenge_id'))
                completed = json.loads(db.execute('SELECT completed FROM user WHERE username = ?;', (username,)).fetchone()[0])
                key = str(challenge_id)
                points_awarded = None
                with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
                    challenge_list = json.load(f)['list']
                    challenge = next((item for item in challenge_list if item.get('id') == challenge_id), None)
                if challenge is None:
                    flash('Challenge not found!')
                    return redirect(url_for('main.admin'))
                if challenge['points'] == -1:
                    points_awarded_raw = (request.form.get('points_awarded') or '').strip()
                    try:
                        points_awarded = int(points_awarded_raw)
                    except ValueError:
                        flash('Invalid points awarded value.')
                        return redirect(url_for('main.admin'))

                challenge = set_challenge_completed(
                    challenge_id,
                    submission_number=0,
                    username=username,
                    taken_points=points_awarded if points_awarded is not None else -1,
                )
                if challenge is None:
                    flash('Failed to update challenge status. Check logs for details.')
                    return redirect(url_for('main.admin'))
                completed['challenges'][key] = ['completed', completed['challenges'][key][1] if key in completed['challenges'] else '']
                challenge_name = challenge['name'] if 'name' in challenge else f'ID {challenge_id}'
                if challenge['points'] == -1:
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {points_awarded} points.', 1])
                    else:
                        notifications.append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {points_awarded} points.', 1])
                    ##db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (points_awarded, username))
                else:
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {challenge["points"]} points.', 1])
                    else:
                        notifications.append([f'Challenge: {challenge_name} has been marked as completed by an admin. You have been awarded {challenge["points"]} points.', 1])
                    ##db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (challenge['points'], username))
                ##db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
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
            submission_number = int(request.form.get('submission_number'))-1

            if action == 'approve':
                with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
                    challenge_list = json.load(f)['list']
                    challenge = next((item for item in challenge_list if item.get('id') == challenge_id), None)
                if challenge is None:
                    flash(f'Challenge {challenge_id} not found.')
                    return redirect(url_for('main.admin_pending'))

                points_awarded = challenge['points']
                if challenge['name']=="Assassination" and user['gift']=="competitiveness":
                    points_awarded += 200
                if challenge['points'] == -1:
                    points_awarded_raw = (request.form.get('points_awarded') or '').strip()
                    try:
                        points_awarded = int(points_awarded_raw)
                    except ValueError:
                        flash('Invalid points awarded value.')
                        return redirect(url_for('main.admin_pending'))

                result = set_challenge_completed(
                    challenge_id,
                    taken_points=points_awarded,
                    submission_number=submission_number,
                    username=username,
                )
                if result is None:
                    flash('Failed to approve submission. Check logs for details.')
                    return redirect(url_for('main.admin_pending'))

                if challenge['points'] == -1:
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Your submission for challenge {challenge_id}: "{challenge["name"]}" has been approved! You have been awarded {points_awarded} points.', 1])
                    else:
                        notifications.append([f'Your submission for challenge {challenge_id}: "{challenge["name"]}" has been approved! You have been awarded {points_awarded} points.', 1])
                else:
                    ##db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (challenge['points'], username))
                    if isinstance(notifications, dict) and "list" in notifications:
                        notifications["list"].append([f'Your submission for challenge {challenge_id} has been approved! You have been awarded {challenge['points']} points.', 1])
                    else:
                        notifications.append([f'Your submission for challenge {challenge_id} has been approved! You have been awarded {challenge['points']} points.', 1])

                ##db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
                db.execute('UPDATE user SET notifications = ? WHERE username = ?;', (json.dumps(notifications), username))
                db.commit()
                flash(f'Approved submission for user {user["username"]} on challenge {challenge["name"]}')
            elif action == 'reject':
                if key in completed['challenges'] and submission_number < len(completed['challenges'][key]):
                    try:
                        submission_file = completed['challenges'][key][submission_number][1]
                        file_path = os.path.join(current_app.root_path, "static", "img", "users", username, "submissions", submission_file)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        del completed['challenges'][key][submission_number]
                    except Exception as e:
                        current_app.logger.exception('Error removing submission file for user %s challenge %d: %s', username, challenge_id, str(e))
                        flash(f'Warning: Could not delete submission file, but rejection recorded.')
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
                if isinstance(notifications, dict) and "list" in notifications:
                    notifications["list"].append([f'Your student ID verification has been rejected. You are not currently participating in the Omega Games. If you believe this is a mistake, please contact OMEGA.', 1])
                else:
                    notifications.append([f'Your student ID verification has been rejected. You are not currently participating in the Omega Games. If you believe this is a mistake, please contact OMEGA.', 1])
                db.execute("UPDATE user SET notifications = ?, participating = 0, id_image = NULL WHERE username = ?;", (json.dumps(notifications), username))
                db.commit()
                flash(f'Rejected id for user {user["username"]}')

    users = db.execute('SELECT * FROM user;').fetchall()
    with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r', encoding='utf-8') as f:
        challenges = json.load(f)['list']
    return render_template('main/admin_pending.html', users=users, os=os, current_app=current_app, json=json, url_for=url_for, challenges=challenges, datetime=datetime)

@main.route('/edit_pfp', methods=['GET', 'POST'])
@login_required
def edit_pfp():
    user = get_db().execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        pfp= request.files.get('pfp')
        if pfp and pfp.filename:
            try:
                upload_dir = os.path.join(current_app.root_path, "static", "img", "users", user['username'])
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, "pfp_" + user['username'] + "." + pfp.filename.split('.')[-1])
                pfp.save(save_path)
                db = get_db()
                db.execute(
                    "UPDATE user SET pfp = ? WHERE id = ?",
                    ("img/users/" + user['username'] + "/pfp_" + user['username'] + "." + pfp.filename.split('.')[-1], session['user_id']),
                )
                db.commit()
                flash('Profile picture updated successfully!')
                return redirect(url_for('main.profile'))
            except Exception as e:
                flash('Error saving profile picture: ' + str(e))
    return render_template('main/edit_pfp.html', user=user, datetime=datetime)

@main.route('/all_users', methods=['GET'])
@login_required
def all_users():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if not user or user['admin'] != 1:
        flash('What are you doing? OMEGA would not be proud of you.')
        return redirect(url_for('main.profile'))
    users = db.execute('SELECT * FROM user;').fetchall()
    return render_template('main/all_users.html', users=users, datetime=datetime, parse=parse)



#friend routes

@main.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    user=get_db().execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/friends.html', user=user, json = json, datetime=datetime)

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
        if len(friends['list']) >= 5 and not json.loads(user['completed'])['challenges'].get('6'):
            set_challenge_completed(6, points_awarded=0, username=user['username'])
        if len(friends['list'])<=5:
            db.execute('UPDATE user SET points = points + 40 where id = ?', (id,))
            flag1=True
        if len(requester_friends['list']) >= 5 and not json.loads(requester['completed'])['challenges'].get('6'):
            set_challenge_completed(6, points_awarded=0, username=requester_username)
        if len(requester_friends['list'])<=5:
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
        user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
        requester_username = request.form.get('requester')
        requester = db.execute('SELECT * FROM user WHERE username = ?;', (requester_username,)).fetchone()
        user_requests = json.loads(user['friend_requests'])
        user_requests['list'].remove(requester_username)
        db.execute('UPDATE user SET friend_requests = ? where id = ?', (json.dumps(user_requests), session['user_id']))
        db.commit()
        flash("Rejected friend request from "+requester_username+".")
    return redirect(url_for('main.friends'))

@main.route('/remove_friend', methods=['GET', 'POST'])
@login_required
def remove_friend():
    if request.method == "POST":
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
        friend_username = request.form.get('friend')
        friend = db.execute('SELECT * FROM user WHERE username = ?;', (friend_username,)).fetchone()
        friends = json.loads(user['friends'])
        if friend:
            friend_friends = json.loads(friend['friends'])
        friends['list'].remove(friend_username)
        if friend and user['username'] in friend_friends['list']:
            friend_friends['list'].remove(user['username'])
        if len(friends['list']) < 5:
            db.execute('UPDATE user SET points = points - 40 where id = ?', (session['user_id'],))
        if friend and len(friend_friends['list']) < 5:
            db.execute('UPDATE user SET points = points - 40 where username = ?', (friend_username,))
        db.execute('UPDATE user SET friends = ? where id = ?', (json.dumps(friends), session['user_id']))
        db.execute('UPDATE user SET friends = ? where username = ?', (json.dumps(friend_friends), friend_username))
        db.commit()
        flash("Removed friend "+friend_username+".")
    return redirect(url_for('main.friends'))

#misc routes

@main.route('/sans', methods=['GET', 'POST'])
@login_required
def sans():
    return render_template('main/bts/index.html')

@main.route('/gambling', methods=['GET', 'POST'])
@login_required
def gambling():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if user['percentage'] == 1:
        flash('You have already completed the gambling challenge and cannot gamble anymore! You only get one attempt!')
        return redirect(url_for('main.profile'))
    if request.method == 'POST':
        if request.form.get('action') == 'place_bet':
            bet_str = request.form.get('bet', '0').strip()
            if not bet_str.isdigit():
                flash('Invalid bet amount!')
                return redirect(url_for('main.gambling'))
            bet = int(bet_str)
            if bet <= 0:
                flash('Bet must be a positive integer!')
                return redirect(url_for('main.gambling'))
            if bet > user['points']:
                flash('You cannot bet more points than you have!')
                return redirect(url_for('main.gambling'))
            user_percentage = .05
            db.execute('UPDATE user SET percentage = ? WHERE id = ?;', (user_percentage, session['user_id']))
            db.commit()
            db.execute('UPDATE user SET points = points - ? WHERE id = ?;', (bet, session['user_id']))
            db.commit()
            flash(f'You placed a bet of {bet} points! The button has a {int(user_percentage*100)}% chance to break. If it breaks, you lose your bet. If it doesnt, you win points based on the current percentage and can choose to withdraw or risk it all again with a higher chance of losing everything. The points have been taken out of your total. If you go away from this page before finishing, you may completely lose your points, so be careful.')
            session['bet'] = bet
            user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
            return render_template('main/gambling.html', user=user, datetime=datetime, bet=bet)
        if request.form.get('withdraw') == '1':
            points = session.get('bet', 0)
            if points > 0:
                db.execute('UPDATE user SET points = points + ?, percentage = 1 WHERE id = ?;', (points, session['user_id']))
                db.commit()
                flash(f'You withdrew with {points} points! They have been added to your total points.')
                return redirect(url_for('main.profile'))
            pass
        if request.form.get('withdraw') == '0':
            percent = user['percentage']
            points = session.get('bet', 0)
            win = random.random() > percent
            if win:
                if user['gift'] == 'competitiveness':
                    points_won = int(points * ((percent)+1))
                else:
                    points_won = int(points * ((percent*.5)+1))
                points_won = points_won - points_won%10
                session['bet'] = points_won
                flash(f'The button didnt break. You are up to {points_won} points! You can choose to withdraw or risk it all again with a higher chance of losing everything.')
                if user['gift'] == 'determination':
                    percentage_increase = 0.025
                else:
                    percentage_increase = 0.05
                new_percentage = min(percent + percentage_increase, .6)
                db.execute('UPDATE user SET percentage = ? WHERE id = ?;', (new_percentage, session['user_id']))
                db.commit()
            else:
                if user['gift'] == 'vigilance':
                    points_retained = int(points * 0.2)
                    points_retained = points_retained - points_retained%10
                    db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (points_retained, session['user_id']))
                    flash(f'The button broke! However, due to your vigilance gift, you were able to retain {points_retained} of your points.')
                else:
                    flash('The button broke! You lost all the points you risked.')
                session['bet'] = None
                db.execute('UPDATE user SET percentage = 1 WHERE id = ?;', (session['user_id'],))
                db.commit()
                return redirect(url_for('main.profile'))
    if 'bet' not in session:
        session['bet'] = None
    return render_template('main/gambling.html', user=user, datetime=datetime, bet=session['bet'])

@main.route('/platforming', methods=['GET', 'POST'])
@login_required
def platforming():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/phaser/platforming/index.html', datetime=datetime, user=user, json=json)

@main.route('/target_practice', methods=['GET', 'POST'])
@login_required
def target_practice():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    return render_template('main/phaser/target_practice/index.html', datetime=datetime, user=user)
@main.route('/submit-score', methods=['POST'])
@login_required
def submit_score():
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    score_str = request.form.get('score', '0').strip()
    print(f"Received score submission: '{score_str}' from user {user['username']}")
    score = int(score_str) if score_str else 0
    game = request.form.get('game')
    if game == 'platforming':
        hi_score = int(user['platform_hi'])
        if hi_score is None or score > hi_score:
            db.execute('UPDATE user SET platform_hi = ? WHERE id = ?;', (score, session['user_id']))
            points_earned = score-hi_score
            db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (points_earned, session['user_id']))
            flash("New high score! Points earned: " + str(points_earned))
            db.commit()
        else:
            flash("You didn't beat your record. No new points earned. Current highest score: " + str(hi_score))
        return redirect(url_for('main.platforming'))
    elif game == 'target_practice':
        hi_score = int(user['target_hi'])
        if hi_score is None or score > hi_score:
            db.execute('UPDATE user SET target_hi = ? WHERE id = ?;', (score, session['user_id']))
            points_earned = score-hi_score
            db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (points_earned, session['user_id']))
            flash("New high score! Points earned: " + str(points_earned))
            db.commit()
        else:
            flash("You didn't beat your record. No new points earned. Current highest score: " + str(hi_score))
        return redirect(url_for('main.target_practice'))
    return redirect(url_for('main.profile'))



@main.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    db= get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        action= request.form.get('action')
        if action == 'delete_message':
            user_id = request.form.get('user_id')
            notifications = json.loads(db.execute('SELECT notifications FROM user WHERE id = ?;', (user_id,)).fetchone()[0])
            notifications['list'].append(['Your message on the message board has been deleted by an admin. You have been deducted 100 points. If it happens again, you may face further consequences.', 1])
            db.execute('UPDATE user SET notifications = ? WHERE id = ?;', (json.dumps(notifications), user_id))
            db.execute('UPDATE user SET umessage = NULL WHERE id = ?;', (user_id,))
            db.execute('UPDATE user SET points = points - ? WHERE id = ?;', (100, user_id))
            db.commit()
            flash('Message deleted!')
            return redirect(url_for('main.messages'))
        message = request.form.get('message')
        if message:
            db.execute('UPDATE user SET umessage = ? WHERE id = ?;', (message, session['user_id']))
            completed = json.loads(user['completed'])
            completed['challenges']['32'] = ['completed', ''] #change id when challenges are reordered
            db.execute('UPDATE user SET completed = ? WHERE id = ?;', (json.dumps(completed), session['user_id']))
            db.execute('UPDATE user SET points = points + ? WHERE id = ?;', (100, session['user_id']))
            flash('Challenge completed! Points awarded: ' + str(100))
                
            db.commit()
            flash('Message posted!')
        else:
            flash('Message cannot be empty!')
        return redirect(url_for('main.messages'))
    users = db.execute('SELECT umessage, username, id FROM user;').fetchall()

    return render_template('main/messages.html', datetime=datetime, users=users, user=user)



@main.route('/last_challenge_video')
def last_video():
    return render_template('main/last.html')