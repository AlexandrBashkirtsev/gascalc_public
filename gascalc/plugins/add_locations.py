import os
from flask import Blueprint
from flask_login import current_user, login_required
from gascalc import db, app
from gascalc.forms import Location_Form, Import_Location_Form
from gascalc.models import User, Location
from flask import (render_template, url_for, 
					flash, redirect, request, abort,
					send_file, make_response, send_from_directory,
					after_this_request)
from utils.load import get_geocode
from utils.import_export import import_locs_csv, export_locs_csv
from utils.nocache import nocache

add_locations = Blueprint('add_locations', __name__, template_folder='templates')

@add_locations.route('/home/', methods=['GET', 'POST'])
@login_required
def home():

	import_form = Import_Location_Form()
	form = Location_Form()

	if import_form.submit_import.data and import_form.validate_on_submit():

		csv = import_locs_csv(import_form.file.data)
		data = csv['data']
		errors = csv['errors']

		if len(list(data.itertuples())) > 0:
			locations = []
			for row in data.itertuples():

				location = Location(location = str(row.location),
									geocode=str(row.geocode),
									LAT=str(row.LAT),
									LON=str(row.LON),
									comment=str(row.organization),
									category=str(row.category),
									quota=int(row.quota),
									user=current_user)
				locations.append(location)

			db.session.add_all(locations)
			db.session.commit()

		else:

			flash('Не получилось импортировать ни одного адреса', 'danger')

		if len(list(errors.itertuples())) > 0:

			for row in errors.itertuples():

				flash(f'Не получается импортировать строку: {row.location}|{row.organization}.', 'danger')

		if len(list(errors.itertuples())) == 0 and len(list(data.itertuples())) > 0:

			flash(f'Адреса успешно добавлены', 'success')

		return redirect(url_for('.home'))
	
	if form.submit.data and form.validate_on_submit():

		if form.LAT.data and form.LON.data:

			location = Location(location = form.location.data,
								geocode=form.location.data,
								LAT=form.LAT.data,
								LON=form.LON.data,
								comment=form.comment.data,
								category=form.category.data,
								quota=form.quota.data,
								user=current_user)
		else:

			geocode = get_geocode(form.location.data)

			if geocode:
		
				# add new location to db
				location = Location(location = form.location.data,
								geocode=geocode.address,
								LAT=geocode.latitude,
								LON=geocode.longitude,
								comment=form.comment.data,
								category=form.category.data,
								quota=form.quota.data,
								user=current_user)

				db.session.add(location)
				db.session.commit()
				flash('Адрес успешно добавлен', 'success')

			else:

				flash('Не получается найти координаты для заданного адреса', 'danger')

		return redirect(url_for('.home'))

	locations = Location.query.filter_by(user=current_user)

	locations_number = Location.query.filter_by(user=current_user).count()

	if locations_number < 2:
		flash('Для дальнейших расчетов необходимо добавить хотя-бы два адреса', 'warning')

	base_locations_number = Location.query.filter_by(user=current_user)\
									.filter(Location.category == 'Собственная')\
									.count()

	if base_locations_number == 0:
		flash('Для дальнейших расчетов необходимо добавить хотя-бы один адрес с категорией "Собственная"', 'warning')

	return render_template('home.html',
							form = form,
							import_form=import_form,
							locations=locations)

@add_locations.route('/delete_row/', methods=['GET','POST'])
def delete_row():

	if request.method == 'POST':
		locationid = int(request.form['locationid'])
		print('Delete ID:',locationid)
		print(type(locationid))
		Location.query.filter_by(id=locationid).delete()
		db.session.commit()
	
	return redirect(url_for('.home'))

@add_locations.route('/base_map/', methods=['GET', 'POST'])
@login_required
def base_map():

	form = Location_Form()
	import_form = Import_Location_Form()

	if import_form.submit_import.data and form.validate_on_submit():

		csv = import_locs_csv(import_form.file.data)
		data = csv['data']
		errors = csv['errors']

		if len(list(data.itertuples())) > 0:
			locations = []
			for row in data.itertuples():

				location = Location(location = str(row.location),
									geocode=str(row.geocode),
									LAT=str(row.LAT),
									LON=str(row.LON),
									comment=str(row.organization),
									category=str(row.category),
									quota=int(row.quota),
									user=current_user)
				locations.append(location)

			db.session.add_all(locations)
			db.session.commit()

		else:

			flash('Не получилось импортировать ни одного адреса', 'danger')

		if len(list(errors.itertuples())) > 0:

			for row in errors.itertuples():

				flash(f'Не получается импортировать строку: {row.location}|{row.organization}.', 'danger')

		if len(list(errors.itertuples())) == 0 and len(list(data.itertuples())) > 0:

			flash(f'Адреса успешно добавлены', 'success')

		return redirect(url_for('.base_map'))

	if form.submit.data and form.validate_on_submit():

		if form.LAT.data and form.LON.data:

			location = Location(location = form.location.data,
								geocode=form.location.data,
								LAT=form.LAT.data,
								LON=form.LON.data,
								comment=form.comment.data,
								category=form.category.data,
								quota=form.quota.data,
								user=current_user)
		else:

			geocode = get_geocode(form.location.data)
		
			# add new location to db
			location = Location(location = form.location.data,
							geocode=geocode.address,
							LAT=geocode.latitude,
							LON=geocode.longitude,
							comment=form.comment.data,
							category=form.category.data,
							quota=form.quota.data,
							user=current_user)

		db.session.add(location)
		db.session.commit()
		return redirect(url_for('add_locations.base_map'))

	locations = Location.query.filter_by(user=current_user)

	return render_template('base_map.html',
							form = form,
							import_form=import_form,
							locations=locations)

@add_locations.route('/home/export/', methods=['GET', 'POST'])
@login_required
@nocache
def export():

	# get file
	filename = export_locs_csv()

	@after_this_request 
	def remove_file(response):
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
		return response 

	return	send_from_directory(app.config['UPLOAD_FOLDER'],
								filename,
								as_attachment=True,
								mimetype='application/xls',
								attachment_filename=(str(filename)))