import os
from flask import Blueprint
from flask_login import current_user, login_required
from gascalc import db, app
from gascalc.forms import Employee_Form, Import_Employee_Form
from gascalc.models import User, Employee
from flask import (render_template, url_for, 
					flash, redirect, request,
					abort, send_file, make_response,
					send_from_directory, after_this_request)
from utils.import_export import import_empl_csv, export_empl_csv
from utils.nocache import nocache

add_employees = Blueprint('add_employees', __name__, template_folder='templates')

@add_employees.route('/employees/', methods=['GET', 'POST'])
@login_required
def employees():

	import_form = Import_Employee_Form()
	form = Employee_Form()

	if import_form.submit_import.data and import_form.validate_on_submit():

		csv = import_empl_csv(import_form.file.data)
		data = csv['data']
		errors = csv['errors']

		if len(list(data.itertuples())) > 0:
			employees = []
			for row in data.itertuples():

				employee = Employee(first_name = str(row.first_name),
									second_name=str(row.second_name),
									surname=str(row.surname),
									workday=str(row.workday),
									duration=str(row.duration),
									quota=int(row.quota),
									user=current_user)
				employees.append(employee)

			db.session.add_all(employees)
			db.session.commit()

		else:

			flash('Не получилось импортировать ни одного сотрудника', 'danger')

		if len(list(errors.itertuples())) > 0:

			for row in errors.itertuples():

				flash(f'Не получается импортировать строку: {row.first_name}|{row.second_name}.', 'danger')

		if len(list(errors.itertuples())) == 0 and len(list(data.itertuples())) > 0:

			flash(f'Сотрудники успешно добавлены', 'success')

		return redirect(url_for('.employees'))

	if form.submit.data and form.validate_on_submit():

		# add new location to db
		employee = Employee(first_name = form.first_name.data,
							second_name = form.second_name.data,
							surname = form.surname.data,
							workday=form.workday.data,
							duration=form.duration.data,
							quota=form.quota.data,
							user=current_user)

		db.session.add(employee)
		db.session.commit()
		return redirect(url_for('.employees'))

	employees = Employee.query.filter_by(user=current_user)

	return render_template('employees.html',
							form = form,
							import_form=import_form,
							employees=employees)

@add_employees.route('/delete_e_row/', methods=['GET','POST'])
def delete_row():

	if request.method == 'POST':
		employeeid = int(request.form['employeeid'])
		print('Delete ID:',employeeid)
		print(type(employeeid))
		Employee.query.filter_by(id=employeeid).delete()
		db.session.commit()
	
	return redirect(url_for('.employees'))

@add_employees.route('/employees/export/', methods=['GET', 'POST'])
@login_required
@nocache
def export():

	# get file
	filename = export_empl_csv()

	@after_this_request 
	def remove_file(response):
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
		return response 

	return	send_from_directory(app.config['UPLOAD_FOLDER'],
								filename,
								as_attachment=True,
								mimetype='application/xls',
								attachment_filename=(str(filename)))