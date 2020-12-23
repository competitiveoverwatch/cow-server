from flask import Blueprint, make_response, render_template, session, redirect, request, current_app
from redditflair.reddit import Reddit
from database import db, User, Flair, Database

user_verification = Blueprint('user_verification', __name__)


# user verification
@user_verification.route('/userverification')
def user_verification_page():
	response_params = dict()
	response_params['redditLink'] = Reddit.auth_link('userverification')

	# get verified users
	verified_users = Database.get_verified_users()

	# moderator check
	redditname = session.get('redditname')
	if redditname:
		if not Database.check_moderator(redditname):
			return redirect('/redditflair')

	response = make_response(
		render_template('userverification.html', **response_params, verifiedUsers=verified_users))

	return response


@user_verification.route('/userverification/verify')
def user_verification_verify():
	user_name = request.args.get('user', '')
	description = request.args.get('description', '')

	# moderator check
	redditname = session.get('redditname')
	if redditname:
		if not Database.check_moderator(redditname):
			return redirect('/redditflair')

	user = Database.get_or_add_user(user_name)
	current_app.logger.warning(f"u/{redditname} verified user u/{user.name} from {user.special_text} to {description}")
	user.special_id = 'verified'
	user.special_text = description
	user.flair1 = 'verified'
	Database.commit()

	Reddit.set_flair(user_name)

	return redirect('/userverification')
