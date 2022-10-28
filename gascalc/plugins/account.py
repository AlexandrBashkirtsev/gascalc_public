from gascalc import app, db, bcrypt
from flask import Blueprint
from flask_login import (login_user, current_user, 
						logout_user, login_required)
from flask import (render_template, url_for, 
					flash, redirect, request, abort, send_file, make_response)
from gascalc.forms import RegistrationForm, LoginForm
from gascalc.models import User

account = Blueprint('account', __name__, template_folder='templates')

@account.route('/login/', methods=['GET', 'POST'])
def login():

	if current_user.is_authenticated:

		return redirect(url_for('add_locations.home'))

	form = LoginForm()

	if form.validate_on_submit():

		user = User.query.filter_by(email=form.email.data).first()

		if user and bcrypt.check_password_hash(user.password, form.password.data):
			
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')

			return redirect(next_page) if next_page else redirect(url_for('add_locations.home'))
		
		else:

			flash('Login unsuccessfull. Please check email and password', 'danger')
	
	return render_template('landing/pay/login.html', 
							title='Log In', 
							form=form)

@account.route('/register/', methods=['GET', 'POST'])
def register():

	if current_user.is_authenticated:

		return redirect(url_for('add_locations.home'))

	form = RegistrationForm()

	if form.validate_on_submit():
		
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
		
		user = User(email=form.email.data,
					password=hashed_password)

		db.session.add(user)
		db.session.commit()
		login_user(user)
		flash('Your account has been created! You are now able to log in', 'success')
		
		return redirect(url_for('add_locations.home'))

	return render_template('landing/pay/register.html', 
							title='Register', 
							form=form)

@account.route('/logout/')
def logout():

	logout_user()

	return redirect(url_for('.login'))