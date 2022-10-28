import json
from flask import Blueprint
from flask_login import current_user, login_required
from gascalc import db
from gascalc.forms import General_Settings
from gascalc.models import User
from flask import (render_template, url_for, 
					flash, redirect, request, abort, send_file, make_response)

settings = Blueprint('settings', __name__, template_folder='templates')

@settings.route('/settings/', methods=['GET', 'POST'])
@login_required
def change():

	form = General_Settings()

	if form.validate_on_submit():

		# load settings
		settings = json.loads(current_user.settings)

		settings['org_name'] = form.org_name.data
		settings['org_address'] = form.org_addr.data
		settings['OGRN'] = form.OGRN.data
		settings['INN'] = form.INN.data
		settings['accountant'] = form.accountant.data

		current_user.settings = json.dumps(settings)

		db.session.commit()

		return redirect(url_for('.change'))

	elif request.method == 'GET':

		settings = json.loads(current_user.settings)

		form.org_name.data = settings['org_name']
		form.org_addr.data = settings['org_address']
		form.OGRN.data = settings['OGRN']
		form.INN.data = settings['INN']
		form.accountant.data = settings['accountant']
		
		return render_template('settings.html',
								form = form)