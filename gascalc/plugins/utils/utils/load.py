import os
import json
import pandas as pd
import random
import datetime
import requests
import secrets
from gascalc import app, db
from gascalc.models import Location
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func, select
from flask_login import current_user



# get geocode for location
def get_geocode(location):
		
		geocode = app.config['GEOCODER'].geocode(location)

		return geocode

# get route between locations
def get_route_simple(locations):

	route_coords = []
	for location in locations:
		route_coords.append([float(location.LON), float(location.LAT)])

	headers = {'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
				'Authorization': app.config['ROUTES_API_KEY'],
	    		'Content-Type': 'application/json; charset=utf-8'}

	body = {"coordinates":route_coords}

	call = requests.post(app.config['ROUTES_API'], json=body, headers=headers)

	#print(call.status_code, call.reason)
	#print('STATUS', call.status_code)

	if call.status_code == 200:

		result = call.json()

		features = result['features'][0]
		summary = features['properties']['summary']
		geometry = features['geometry']['coordinates']
		full_route = result

		geometry = [[point[1],point[0]] for point in geometry]

		#print('ROUTE SUMMARY:',summary)
		#print('ROUTE GEOMETRY:',geometry)

		result = {'summary':summary,
				'geometry':geometry,
				'full_route':full_route}

		return {'result':result,
				'status':call.status_code}

	else:

		return {'result':None,
				'status':call.status_code}


# get route from base location
def get_route(base_location, workday, duration):


	# init summary and route dicts
	summary = app.config['SUMMARY_INIT']
	summary['locations'] = []

	worktime = 0
	start_time = 0
	used_locations = []

	location = {'location':base_location.comment,
				'id':base_location.id,
				'addr':base_location.location,
				'LAT':base_location.LAT,
				'LON':base_location.LON,
				'distance':0.0,
				'duration':0,
				'time_spent':0,
				'worktime':0,
				'start_time':0,
				'finish_time':0,
				'geometry':[]}

	summary['locations'].append(location)

	start = True
	index = 0

	routing_locations = list(Location.query\
							.filter_by(user=current_user)\
							.filter(Location.category != 'Собственная')\
							.order_by(func.random())\
							.all())

	while (worktime < ((workday)*3600)) and len(routing_locations) > 0:

		routing_location = random.choice(routing_locations)
		routing_locations.remove(routing_location)

		if routing_location not in used_locations:

			locations = []

			if start:
				locations.append(base_location) # start location
				start = False
			else:
				locations.append(used_locations[-1]) # previous location

			locations.append(routing_location)
			used_locations.append(routing_location)

			result = get_route_simple(locations)
			new_route = result['result']
			status = result['status']

			if new_route and 'summary' in new_route and 'distance' in new_route['summary']:

				res_distance = int(new_route['summary']['distance'])
				res_duration = int(new_route['summary']['duration']) + 600 # city roads
				res_geometry = str(new_route['geometry'])

				if duration == 'short':
					min_time = 5
					max_time = 10
				elif duration == 'medium':
					min_time = 10
					max_time = 30
				elif duration == 'long':
					min_time = 30
					max_time = 90

				time_spent = random.randrange(min_time, max_time, 1) * 60 # in seconds

				worktime = worktime + time_spent + res_duration

				finish_time = start_time + res_duration
				start_time = worktime
				index += 1
				location = {'location':routing_location.comment,
							'id':routing_location.id,
							'addr':routing_location.location,
							'LAT':routing_location.LAT,
							'LON':routing_location.LON,
							'distance':res_distance/1000,
							'duration':res_duration,
							'time_spent':time_spent,
							'worktime':worktime,
							'start_time':start_time,
							'finish_time':finish_time,
							'geometry':res_geometry}

				summary['locations'].append(location)


				print(res_duration)

				if res_duration > (((workday*3600)- worktime)/2):

					break

			else:

				return {'summary':None,
						'status':status}

		else: 

			continue

	locations = []

	locations.append(used_locations[-1])
	locations.append(base_location) # stop location

	result = get_route_simple(locations)
	new_route = result['result']
	status = result['status']

	if new_route:

		res_distance = int(new_route['summary']['distance'])
		res_duration = int(new_route['summary']['duration']) + 1200 # city roads
		res_geometry = str(new_route['geometry'])
		time_spent = 0

		start_time = worktime
		worktime = worktime + res_duration
		finish_time = worktime

		location = {'location':base_location.comment,
					'id':base_location.id,
					'addr':base_location.location,
					'LAT':base_location.LAT,
					'LON':base_location.LON,
					'distance':res_distance/1000,
					'duration':res_duration,
					'time_spent':time_spent,
					'worktime':worktime,
					'start_time':start_time,
					'finish_time':finish_time,
					'geometry':res_geometry}

		summary['locations'].append(location)

		# CODE SUMMARY THERE

		return {'summary':summary,
				'status':status}
	else:

		return {'summary':None,
				'status':status}

def format_route(summary, start_time, web=True):

	new_locations = []
	old_locations = summary['locations']
	route_len = len(old_locations)

	for i in range(1, route_len):

		if web:
			comment = old_locations[i-1]['location'] + ' - ' + old_locations[i]['location']
		else:
			comment = old_locations[i-1]['location'] + ' : ' + \
					old_locations[i-1]['addr'] + ' - ' + \
					old_locations[i]['location'] + ' : ' + \
					old_locations[i]['addr']

		distance = "{:.1f}".format(old_locations[i]['distance'])
		out_time = start_time+datetime.timedelta(seconds=old_locations[i-1]['start_time'])
		out_time = out_time.time()
		in_time = start_time+datetime.timedelta(seconds=old_locations[i]['finish_time'])
		in_time = in_time.time()
		duration = datetime.timedelta(seconds=old_locations[i]['duration'])
		time_spent = datetime.timedelta(seconds=old_locations[i]['time_spent'])

		formatted_location = {'location': comment,
								'index':str(i),
								'duration':str(duration),
								'distance':str(distance),
								'time_spent':str(time_spent),
								'out_time':str(out_time),
								'in_time':str(in_time)}
		new_locations.append(formatted_location)

	return new_locations

def get_consumption(route, consumption, price):

	distance = 0

	for location in route['locations']:
		distance = distance + location['distance']

	fuel_marge = consumption*distance/100
	resource_marge = int(price*fuel_marge)

	return {'resource_marge':resource_marge,
			'fuel_marge':fuel_marge,
			'distance':distance}

# get route from base location
def get_route_manual(locations, duration):

	# init summary and route dicts
	summary = app.config['SUMMARY_INIT']
	summary['locations'] = []

	location = {'location':locations[0].comment,
				'id':locations[0].id,
				'addr':locations[0].location,
				'LAT':locations[0].LAT,
				'LON':locations[0].LON,
				'distance':0,
				'duration':0.0,
				'time_spent':0,
				'worktime':0,
				'start_time':0,
				'finish_time':0,
				'geometry':[]}

	summary['locations'].append(location)

	worktime = 0
	start_time = 0

	for i in range(1, len(locations)):

		result = get_route_simple([locations[i-1],locations[i]])
		new_route = result['result']
		status = result['status']

		if new_route and 'summary' in new_route and 'distance' in new_route['summary']:

				res_distance = int(new_route['summary']['distance'])
				res_duration = int(new_route['summary']['duration']) + 600 # city roads
				res_geometry = str(new_route['geometry'])

				if duration == 'short':
					min_time = 5
					max_time = 10
				elif duration == 'medium':
					min_time = 10
					max_time = 30
				elif duration == 'long':
					min_time = 30
					max_time = 90

				time_spent = random.randrange(min_time, max_time, 1) * 60 # in seconds

				worktime = worktime + time_spent + res_duration
				finish_time = start_time + res_duration
				start_time = worktime
				location = {'location':locations[i].comment,
							'id':locations[i].id,
							'addr':locations[i].location,
							'LAT':locations[i].LAT,
							'LON':locations[i].LON,
							'distance':res_distance/1000,
							'duration':res_duration,
							'time_spent':time_spent,
							'worktime':worktime,
							'start_time':start_time,
							'finish_time':finish_time,
							'geometry':res_geometry}

				summary['locations'].append(location)

		else:

			return {'summary':None,
					'status':status}

	if summary:

		return {'summary':summary,
				'status':status}
	else:

		return {'summary':None,
				'status':status}