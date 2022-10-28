import folium
import os
import json
from gascalc import app
from gascalc.models import User, Location
from flask import (render_template, url_for)

# adds markers to featuregroup in folium
def add_point(fg, lat, lon, popup):
	# fg: FeatureGroup()
	# location: [50.23231, 75.3213123]
	# popup: 'location desription'

	if isinstance(popup, dict):
		popup=popup['location']
	else:
		popup=popup.comment


	html=render_template('popup_card.html',
						popup=popup)

	iframe = folium.IFrame(html=html, width='300', height='200')
	popup = folium.Popup(iframe, max_width='100%')

	fg.add_child(folium.Marker(location = [lat, lon], 
								popup = popup))
	pass

# create base map
def create_base_map(locations):

	# instance of folium FeatureGroup
	fg = folium.FeatureGroup(name = 'Base addressess')
	for location in locations:

		add_point(fg=fg,
					lat = location.LAT,
					lon = location.LON,
					popup = location)

	minlat = min(float(location.LAT) for location in locations)
	minlon = min(float(location.LON) for location in locations)
	maxlat = max(float(location.LAT) for location in locations)
	maxlon = max(float(location.LON) for location in locations)

	# bounds for map
	sw = [minlat, minlon]
	ne = [maxlat, maxlon]

	fmap = folium.Map(location = [(maxlat+minlat)/2, (maxlon+minlon)/2],
					 zoom_start = 5)
	fmap.fit_bounds([sw, ne])
	fmap.add_child(fg)
	#map.save(os.path.join(app.config['MAPS_FOLDER'],'map.html'))

	return fmap

# create base map
def create_route_map(locations):

	geometry = []

	for location in locations[1:]:

		route = location['geometry'].replace('[','').split('],')
		for point in route:

			point = point.replace('[','')
			point = point.replace(' ','')
			point = point.replace(']','')
			point = point.split(',')
			point = (float(point[0]), float(point[1]))
			geometry.append(point)

	froute = folium.PolyLine(geometry, weight=10, opacity=0.5)
	# instance of folium FeatureGroup
	fg = folium.FeatureGroup(name = 'Base addressess')

	for location in locations:

		add_point(fg=fg,
					lat = location['LAT'],
					lon = location['LON'],
					popup = location)

	minlat = min(float(location['LAT']) for location in locations)
	minlon = min(float(location['LON']) for location in locations)
	maxlat = max(float(location['LAT']) for location in locations)
	maxlon = max(float(location['LON']) for location in locations)

	# bounds for map
	sw = [minlat, minlon]
	ne = [maxlat, maxlon]

	fmap = folium.Map(location = [(maxlat+minlat)/2, (maxlon+minlon)/2],
					 zoom_start = 5)
	fmap.fit_bounds([sw, ne])
	fmap.add_child(fg)
	fmap.add_child(froute)
	#map.save(os.path.join(app.config['MAPS_FOLDER'],'map.html'))

	return fmap