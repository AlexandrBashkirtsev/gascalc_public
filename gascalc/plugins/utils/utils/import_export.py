import os
import pandas as pd
from gascalc import app, db
from gascalc.models import Location, Employee, Car
from flask_login import current_user

# importing locations file
def import_locs_csv(form_csv):

	data = pd.read_csv(form_csv, encoding = "utf-8")
	data['geocode'] = data['location'].apply(app.config['GEOCODER'].geocode)
	data['LAT'] = data['geocode'].apply(lambda x: x.latitude if x != None else None)
	data['LON'] = data['geocode'].apply(lambda x: x.longitude if x != None else None)
	data['coords'] = data['LON'].astype(str) + ',' + data['LAT'].astype(str)

	# check null rows (with not loaded geocode)
	errors = data[data.isnull().any(axis=1)]

	# rows without null goes in data
	data = data.dropna()

	return {'data':data,
			'errors':errors}

# exporting locations file
def export_locs_csv():

	locations = Location.query.filter_by(user=current_user)

	data = pd.DataFrame(columns=['location', 'organization', 'category', 'quota'])

	for location in locations:

		df =  pd.DataFrame([[location.location,
							location.comment,
							location.category,
							location.quota]],
							columns=['location',
									'organization',
									'category',
									'quota'])
		data = data.append(df, ignore_index=True)

	name = current_user.email + '_' + 'locations' + '.csv'
	filename = os.path.join(app.config['UPLOAD_FOLDER'], name)

	data.to_csv(filename, index=False)

	return name

# importing employees file
def import_empl_csv(form_csv):

	data = pd.read_csv(form_csv, encoding = "utf-8")

	def duration_format(duration):

		if duration == "Быстро":
			return 'short'
		elif duration == "Средне":
			return 'medium'
		elif duration == "Медленно":
			return 'long'

	data['duration'] = data['duration'].apply(duration_format)

	# check null rows (with not loaded geocode)
	errors = data[data.isnull().any(axis=1)]

	# rows without null goes in data
	data = data.dropna()

	return {'data':data,
			'errors':errors}

# exporting employees file
def export_empl_csv():

	employees = Employee.query.filter_by(user=current_user)

	data = pd.DataFrame(columns=['first_name',
								'surname',
								'second_name',
								'workday',
								'duration',
								'quota'])

	for employee in employees:

		if employee.duration == "short":
			employee.duration = "Быстро"
		elif employee.duration == "medium":
			employee.duration = "Средне"
		elif employee.duration == "long":
			employee.duration = "Медленно"

		df =  pd.DataFrame([[employee.first_name,
							employee.surname,
							employee.second_name,
							employee.workday,
							employee.duration,
							employee.quota]],
							columns=['first_name',
									'surname',
									'second_name',
									'workday',
									'duration',
									'quota'])

		data = data.append(df, ignore_index=True)

	name = current_user.email + '_' + 'employees' + '.csv'
	filename = os.path.join(app.config['UPLOAD_FOLDER'], name)

	data.to_csv(filename, index=False)

	return name

# importing cars file
def import_cars_csv(form_csv):

	data = pd.read_csv(form_csv, encoding = "utf-8")

	def sepflt(strsep):

		if ',' in strsep:

			strsep = strsep.replace(',', '.')

			return strsep

	data['consumption'] = data['consumption'].apply(sepflt)

	# check null rows (with not loaded geocode)
	errors = data[data.isnull().any(axis=1)]

	# rows without null goes in data
	data = data.dropna()

	return {'data':data,
			'errors':errors}

# exporting cars file
def export_cars_csv():

	cars = Car.query.filter_by(user=current_user)

	data = pd.DataFrame(columns=['car',
								'fuel',
								'consumption'])

	for car in cars:

		df =  pd.DataFrame([[car.car,
							car.fuel,
							car.consumption]],
							columns=['car',
									'fuel',
									'consumption'])

		data = data.append(df, ignore_index=True)

	name = current_user.email + '_' + 'cars' + '.csv'
	filename = os.path.join(app.config['UPLOAD_FOLDER'], name)

	data.to_csv(filename, index=False)

	return name