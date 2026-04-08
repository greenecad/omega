

from app.main.db import get_db


def set_challenge_completed(challenge_id, taken_points=-1, submission_number=0, points_awarded=None, username=None):
    import json
    import os
    from flask import session, current_app
    try:
        db = get_db()
        key = str(challenge_id)
        with open(os.path.join(current_app.static_folder, 'challenges.json'), 'r') as f:
            challenges = json.load(f)['list']
            challenge_index = None
            for i in range(len(challenges)):
                if challenges[i]['id'] == challenge_id:
                    challenge_index = i
                    break

            if challenge_index is None:
                raise ValueError(f'Challenge with ID {challenge_id} not found in challenges.json')

            challenge = challenges[challenge_index]
        if username is None:
            user = db.execute('SELECT * FROM user WHERE id = ?;', (session['user_id'],)).fetchone()
            username = user['username']
        else:
            user = db.execute('SELECT * FROM user WHERE username = ?;', (username,)).fetchone()

        if user is None:
            raise ValueError(f'User not found: {username}')

        completed = json.loads(user['completed'])

        if 'challenges' not in completed or not isinstance(completed['challenges'], dict):
            completed['challenges'] = {}

        # Submission challenges store a list of [status, filename] entries.
        if challenge.get('type') == 'submission':
            challenge_entries = completed['challenges'].get(key)
            if not isinstance(challenge_entries, list) or len(challenge_entries) <= submission_number:
                raise ValueError(f'No submission entry found for challenge {challenge_id}, submission {submission_number}')
            completed['challenges'][key][submission_number][0] = 'completed'
        else:
            existing = completed['challenges'].get(key)
            existing_value = ''
            if isinstance(existing, list) and len(existing) > 1 and isinstance(existing[1], str):
                existing_value = existing[1]
            completed['challenges'][key] = ['completed', existing_value]

        db.execute('UPDATE user SET completed = ? WHERE username = ?;', (json.dumps(completed), username))
        if challenge['points'] == -1:
            if taken_points != -1:
                points_awarded = taken_points
            db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (points_awarded, username))
        else:
            db.execute('UPDATE user SET points = points + ? WHERE username = ?;', (challenge['points'], username))

        db.commit()

        return challenge
    except Exception as e:
        current_app.logger.exception('Error in set_challenge_completed for challenge_id=%s username=%s', challenge_id, username)
        return None