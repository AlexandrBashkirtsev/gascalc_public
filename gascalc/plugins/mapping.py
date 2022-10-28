import json
from flask import Blueprint
from gascalc.models import User, Location
from utils.nocache import nocache
from utils.maps import create_base_map, create_route_map
from flask import (render_template, url_for, 
					flash, redirect, request, abort, send_file, make_response)
from flask_login import (current_user, login_required)


mapping = Blueprint('mapping', __name__, template_folder='templates')

@mapping.route('/get_map')
@nocache
def get_map():

	locations = Location.query.filter_by(user=current_user)
	fmap = create_base_map(locations)

	return fmap._repr_html_()

@mapping.route('/get_route_map')
@nocache
def get_route_map():

	# load settings and summary if present
	settings = json.loads(current_user.settings)
	summary = json.loads(current_user.summary)

	if len(summary['locations']) > 0:

		fmap = create_route_map(summary['locations'])

		return fmap._repr_html_()

	else:

		return render_template('/elements/no_map.html')