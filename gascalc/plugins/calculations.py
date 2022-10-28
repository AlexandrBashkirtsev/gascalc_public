import json
import os
from datetime import datetime
from flask import Blueprint
from flask_login import current_user, login_required
from gascalc import db, app
from gascalc.forms import Select_Employee, Set_Calc_Params_Form, Resource_Form, Manual_Calc_Form
from gascalc.models import User, Location, Employee, Car, Route_List
from utils.load import (get_route, get_consumption,
						format_route, get_route_manual)
from utils.nocache import nocache, requires_access_level
from utils.documents import get_docx, mass_gen
from flask import (render_template, url_for, 
					flash, redirect, request, abort,
					send_from_directory, make_response,
					after_this_request)


calculations = Blueprint('calculations', __name__, template_folder='templates')

@calculations.route('/start/', methods=['GET', 'POST'])
@login_required
@requires_access_level('demo')
@nocache
def start_calc():

	form = Set_Calc_Params_Form()

	# load settings and summary if present
	settings = json.loads(current_user.settings)
	summary = json.loads(current_user.summary)

	# resource available
	resource = current_user.resource

	formatted_route = format_route(summary=summary,
										start_time=current_user.start_time)
	
	route_lists = Route_List.query.filter_by(user=current_user).all()

	general_marge = 0
	for route in route_lists:
		new_route = json.loads(route.route_list)
		general_marge = general_marge + new_route['summary']['summary']['resource_marge']

	progress = int(100 * general_marge / (1 + current_user.resource))


	if form.validate_on_submit():

		# load current settings
		settings = json.loads(current_user.settings)

		driver = form.employee.data
		car = form.car.data
		base_location = form.base_location.data
		current_user.start_time = form.start_time.data

		settings['driver_id'] = driver.id
		settings['base_location_id'] = base_location.id
		settings['base_location'] = base_location.comment
		settings['driver_shortname'] = repr(driver)
		settings['driver_fullname'] = repr(driver)
		settings['fuel'] = car.fuel
		settings['car'] = car.car
		settings['car_id'] = car.id
		settings['consumption'] = car.consumption
		settings['resource_price'] = float(form.price.data)

		# upload settings back in db
		current_user.settings = json.dumps(settings)

		db.session.commit()

		# ROUTE CALCULATION
		result = get_route(base_location=base_location,
							workday=driver.workday,
							duration=driver.duration)

		summary = result['summary']
		status = result['status']

		if summary:

			summary['summary'] = get_consumption(route=summary,
												consumption=settings['consumption'],
												price=settings['resource_price'])

			current_user.summary = json.dumps(summary)

			db.session.commit()

			flash('Маршрут рассчитан успешно. Теперь его можно сохранить в базу данных или выгрузить в виде маршрутного листа.', 'success')

		else:

			flash('Возникла проблема с расчетом маршрута. Попробуйте позже или обратитесь в поддержку.', 'danger')
			flash(f'Код ошибки:{status}', 'danger')
			if status == 200:
				flash('Ответ от API получен. Ошибка приложения', 'danger')
			elif status == 400:
				flash('API отклонил запрос. Ошибка приложения', 'danger')
		return	redirect(url_for('.start_calc'))

	elif request.method == 'GET':

		# current driver
		if settings['driver_id'] is not None:
			form.employee.data = Employee.query.filter_by(id=settings['driver_id']).first()

		# current driver
		if settings['car_id'] is not None:
			form.car.data = Car.query.filter_by(id=settings['car_id']).first()

		# current base_location
		if settings['base_location_id'] is not None:
			form.base_location.data = Location.query.filter_by(id=settings['base_location_id']).first()

		# current start_time
		form.start_time.data = current_user.start_time


		# current price
		if settings['resource_price'] is not None:
			form.price.data = settings['resource_price']

		if 'summary' in summary:
			pass
		else:
			summary=app.config['SUMMARY_INIT']

	return render_template('calc.html',
							manual=False,
							form=form,
							route = summary['locations'],
							summary = summary['summary'],
							settings=settings,
							formatted_route=formatted_route,
							general_marge=general_marge,
							progress=progress,
							resource=resource)

@calculations.route('/start/save', methods=['GET', 'POST'])
@login_required
@nocache
def save():

	# load settings and summary if present
	settings = json.loads(current_user.settings)
	summary = json.loads(current_user.summary)

	route_summary = {'settings':settings,
					'summary':summary,
					'start_time':str(current_user.start_time)}

	route_list = Route_List(route_list = json.dumps(route_summary),
							user=current_user)

	db.session.add(route_list)
	db.session.commit()

	return redirect(url_for('.start_calc'))

@calculations.route('/open/', methods=['GET', 'POST'])
@login_required
@nocache
def open():

	if request.method == 'POST':
		routeid = int(request.form['open_routeid'])
		route = Route_List.query.filter_by(id=routeid).first()
		route = json.loads(route.route_list)
		# load settings and summary if present
		settings = route['settings']
		summary = route['summary']

		current_user.settings = json.dumps(settings)
		current_user.summary = json.dumps(summary)
		current_user.start_time = datetime.strptime(route['start_time'], '%Y-%m-%d %H:%M:%S')

		db.session.commit()

		return redirect(url_for('.start_calc'))

@calculations.route('/start/generate', methods=['GET', 'POST'])
@login_required
@nocache
def generate():

	# load settings and summary if present
	settings = json.loads(current_user.settings)
	summary = json.loads(current_user.summary)

	filename = get_docx(summary=summary,
					settings=settings,
					gen_time=current_user.start_time,
					mass_export=False)

	@after_this_request 
	def remove_file(response): 
		os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
		return response 

	return	send_from_directory(app.config['UPLOAD_FOLDER'],
								filename,
								as_attachment=True,
								mimetype='application/docx',
								attachment_filename=(str(filename)))

@calculations.route('/lists/', methods=['GET', 'POST'])
@login_required
def lists():

	form = Resource_Form()

	route_lists = Route_List.query.filter_by(user=current_user).all()
	routes = []
	general_marge = 0
	for route in route_lists:
		new_route = json.loads(route.route_list)
		new_route['id'] = route.id
		routes.append(new_route)
		general_marge = general_marge + new_route['summary']['summary']['resource_marge']

	progress = int(100 * general_marge / (1 + current_user.resource))

	if form.validate_on_submit():

		current_user.resource = float(form.resource.data)

		db.session.commit()

		return redirect(url_for('.lists'))

	elif request.method == 'GET':

		form.resource.data = str(current_user.resource)

	return render_template('route_lists.html',
							form=form,
							routes=routes,
							general_marge=general_marge,
							progress=progress,
							resource=current_user.resource)

@calculations.route('/delete_r_row/', methods=['GET','POST'])
def delete_row():

	if request.method == 'POST':
		routeid = int(request.form['delete_routeid'])
		Route_List.query.filter_by(id=routeid).delete()
		db.session.commit()
	
	return redirect(url_for('.lists'))

@calculations.route('/mass_generate', methods=['GET', 'POST'])
@login_required
@nocache
def mass_generate():

	if request.method == 'POST':

		route_ids = request.form.getlist("check")
		checked = []
		for ids in route_ids:
			checked.append(int(ids))

		print(checked)

		route_lists = Route_List.query.filter(Route_List.id.in_(checked)).all()
		print('route_lists', route_lists)
		routes = []
		for route in route_lists:
			new_route = json.loads(route.route_list)
			new_route['id'] = route.id
			routes.append(new_route)

		filename = mass_gen(routes=routes)

		@after_this_request 
		def remove_file(response): 
			os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 
			return response

		return send_from_directory(app.config['UPLOAD_FOLDER'],
								filename,
								as_attachment=True,
								mimetype='application/docx',
								attachment_filename=(str(filename)))

	return redirect(url_for('.lists'))

@calculations.route('/manual_calc/', methods=['GET', 'POST'])
@login_required
@nocache
def manual_calc():

	# load settings and summary if present
	settings = json.loads(current_user.settings)
	summary = json.loads(current_user.summary)

	data = [str(loc['id']) for loc in summary['locations']]

	form = Manual_Calc_Form()

	# resource available
	resource = current_user.resource

	formatted_route = format_route(summary=summary,
										start_time=current_user.start_time)
	
	route_lists = Route_List.query.filter_by(user=current_user).all()

	general_marge = 0
	for route in route_lists:
		new_route = json.loads(route.route_list)
		general_marge = general_marge + new_route['summary']['summary']['resource_marge']

	progress = int(100 * general_marge / (1 + current_user.resource))

	if request.method == "POST" and form.validate:

		print('FORM SUBMITTED')

		data = request.form.getlist('add_location')
		#data = [int(x) for x in data]
		data = [int(l) for l in data]
		print(data)

		# load current settings
		settings = json.loads(current_user.settings)

		driver = form.employee.data
		car = form.car.data
		current_user.start_time = form.start_time.data

		settings['driver_id'] = driver.id
		#settings['base_location_id'] = base_location.id
		#settings['base_location'] = base_location.comment
		settings['driver_shortname'] = repr(driver)
		settings['driver_fullname'] = repr(driver)
		settings['fuel'] = car.fuel
		settings['car'] = car.car
		settings['car_id'] = car.id
		settings['consumption'] = car.consumption
		settings['resource_price'] = float(form.price.data)

		# upload settings back in db
		current_user.settings = json.dumps(settings)

		db.session.commit()

		locations = Location.query.filter(Location.id.in_(data)).all()
		locations = [next(l for l in locations if l.id == id) for id in data]

		# ROUTE CALCULATION
		result = get_route_manual(locations=locations,
								duration=driver.duration)
		summary = result['summary']
		status = result['status']

		if summary:

			summary['summary'] = get_consumption(route=summary,
												consumption=settings['consumption'],
												price=settings['resource_price'])

			current_user.summary = json.dumps(summary)

			db.session.commit()

			flash('Маршрут рассчитан успешно. Теперь его можно сохранить в базу данных или выгрузить в виде маршрутного листа.', 'success')

		else:

			flash('Возникла проблема с расчетом маршрута', 'danger')
			flash(f'Код ошибки:{status}', 'danger')
			if status == 200:
				flash('Ответ от API получен, но ошибка произошла. Возможно были указаны повторяющиеся локации (маршрут и точки "А" в точку "А")', 'danger')
			elif status == 400:
				flash('API отклонил запрос', 'danger')


		return	redirect(url_for('.manual_calc'))

	#if request.method == "POST":

	elif request.method == "GET":

		print('GETTING')

		# current driver
		if settings['driver_id'] is not None:
			form.employee.data = Employee.query.filter_by(id=settings['driver_id']).first()

		# current driver
		if settings['car_id'] is not None:
			form.car.data = Car.query.filter_by(id=settings['car_id']).first()

		# current start_time
		form.start_time.data = current_user.start_time

		# current price
		if settings['resource_price'] is not None:
			form.price.data = settings['resource_price']

		if 'summary' in summary:
			pass
		else:
			summary=app.config['SUMMARY_INIT']

	return render_template('calc.html',
							manual=True,
							form=form,
							route = summary['locations'],
							summary = summary['summary'],
							settings=settings,
							formatted_route=formatted_route,
							general_marge=general_marge,
							progress=progress,
							resource=resource,
							data=json.dumps(data))