import os
from flask import Blueprint
from flask_login import current_user, login_required
from gascalc import db, app
from gascalc.forms import Car_Form, Import_Car_Form
from gascalc.models import User, Car
from flask import (render_template, url_for, 
					flash, redirect, request, abort,
					send_file, make_response,
					send_from_directory, after_this_request)
from utils.import_export import import_cars_csv, export_cars_csv
from utils.nocache import nocache

add_cars = Blueprint('add_cars', __name__, template_folder='templates')

@add_cars.route('/cars/', methods=['GET', 'POST'])
@login_required
def cars():

	import_form = Import_Car_Form()
	form = Car_Form()

	if import_form.submit_import.data and import_form.validate_on_submit():

		csv = import_cars_csv(import_form.file.data)
		data = csv['data']
		errors = csv['errors']

		if len(list(data.itertuples())) > 0:
			cars = []
			for row in data.itertuples():

				car = Car(car = str(row.car),
						fuel=str(row.fuel),
						consumption=str(row.consumption),
						user=current_user)
				cars.append(car)

			db.session.add_all(cars)
			db.session.commit()

		else:

			flash('Не получилось импортировать ни одной машины', 'danger')

		if len(list(errors.itertuples())) > 0:

			for row in errors.itertuples():

				flash(f'Не получается импортировать строку: {row.car}|{row.fuel}.', 'danger')

		if len(list(errors.itertuples())) == 0 and len(list(data.itertuples())) > 0:

			flash(f'Автомобили успешно добавлены', 'success')

		return redirect(url_for('.cars'))

	if form.submit.data and form.validate_on_submit():

		# add new location to db
		car = Car(car = form.car.data,
					fuel = form.fuel.data,
					consumption = form.consumption.data,
					user=current_user)

		db.session.add(car)
		db.session.commit()
		return redirect(url_for('.cars'))

	cars = Car.query.filter_by(user=current_user)

	return render_template('cars.html',
							form = form,
							import_form=import_form,
							cars=cars)

@add_cars.route('/delete_c_row/', methods=['GET','POST'])
def delete_row():

	if request.method == 'POST':
		carid = int(request.form['carid'])
		print('Delete ID:',carid)
		print(type(carid))
		Car.query.filter_by(id=carid).delete()
		db.session.commit()
	
	return redirect(url_for('.cars'))

@add_cars.route('/cars/export/', methods=['GET', 'POST'])
@login_required
@nocache
def export():

	# get file
	filename = export_cars_csv()

	@after_this_request
	def remove_file(response):
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
		return response 

	return	send_from_directory(app.config['UPLOAD_FOLDER'],
								filename,
								as_attachment=True,
								mimetype='application/xls',
								attachment_filename=(str(filename)))