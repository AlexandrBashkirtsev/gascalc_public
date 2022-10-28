from flask import Blueprint
from flask_login import current_user, login_required
from gascalc import db
from gascalc.forms import Location_Form, Import_Location_Form, ReviewForm
from gascalc.models import User, Review
from flask import (render_template, url_for, 
					flash, redirect, request, abort, send_file, make_response)
from utils.nocache import nocache

landing = Blueprint('landing', __name__, template_folder='templates')

@landing.route('/', methods=['GET', 'POST'])
@nocache
def land():

	form = ReviewForm()

	if form.submit.data and form.validate_on_submit():

		rev = Review(text=form.review.data)

		db.session.add(rev)
		db.session.commit()

		return redirect(url_for('.afterreview'))

	return render_template('landing/home.html',
							form=form)

@landing.route('/quickstart/', methods=['GET', 'POST'])
@nocache
def quickstart():

	return render_template('landing/quickstart.html')

@landing.route('/pay/', methods=['GET', 'POST'])
@nocache
def pay():

	return render_template('landing/pay.html')

@landing.route('/thankyou/', methods=['GET', 'POST'])
@nocache
def afterreview():

	return render_template('landing/thankyou.html')