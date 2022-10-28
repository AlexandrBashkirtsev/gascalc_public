from datetime import datetime
from gascalc import db,login_manager, app
from geopy.geocoders import ArcGIS
import json
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):

	id = db.Column(db.Integer,
					primary_key=True)

	email = db.Column(db.String(120),
					unique=True,
					nullable=False)

	password = db.Column(db.String(60),
						nullable=False)

	summary = db.Column(db.JSON,
						nullable=True,
						default=json.dumps(app.config['SUMMARY_INIT']))

	settings = db.Column(db.JSON,
						nullable=True,
						default=json.dumps(app.config['SETTINGS_INIT']))
	
	start_time = db.Column(db.DateTime,
						nullable=True,
						default=datetime.utcnow)

	resource = db.Column(db.Integer,
						nullable=False,
						default=0)

	subscription = db.Column(db.String(120),
							server_default='demo',
							default='demo')

	# relation models
	employees = db.relationship("Employee",
								backref='user',
								lazy=True)

	locations = db.relationship("Location",
								backref='user',
								lazy=True)

	cars = db.relationship("Car",
							backref='user',
							lazy=True)

	route_lists = db.relationship("Route_List",
							backref='user',
							lazy=True)

	def __repr__(self):
		
		return f"User('{self.email}|')"

class Location(db.Model):

	id = db.Column(db.Integer,
					primary_key=True)

	location = db.Column(db.String(100),
						unique=False,
						nullable=False)

	geocode = db.Column(db.String(200),
						unique=False,
						nullable=True)

	LAT = db.Column(db.String(60),
					nullable=True)

	LON = db.Column(db.String(60),
					nullable=True)

	comment = db.Column(db.String(100),
						unique=False,
						nullable=False,
						default="Организация")

	addr_formatted = db.Column(db.String(200),
						unique=False,
						nullable=True,
						default="")

	category = db.Column(db.String(100),
						unique=False,
						nullable=False,
						default="")

	quota = db.Column(db.Integer,
					nullable=False,
					default=0)

	r_quota = db.Column(db.Integer,
						nullable=True,
						default=0)

	date_used = db.Column(db.DateTime,
						nullable=False,
						default=datetime.utcnow)

	# relation models
	user_id = db.Column(db.Integer,
						db.ForeignKey('user.id'),
						nullable=False)

	def to_json(self):

		res = {'id':str(self.id),
				'geocode':self.geocode,
				'LAT':self.LAT,
				'LON':self.LON,
				'comment':self.comment}

		return json.dumps(res, ensure_ascii=False)

	def __repr__(self):
		
		return f"{self.comment}:{self.geocode}"

class Car(db.Model):

	id = db.Column(db.Integer,
					primary_key=True)

	car = db.Column(db.String(200),
					nullable=False,
					default="Honda CR-V гос. номер AXXXAA XXX RUS")

	fuel = db.Column(db.String(100),
						unique=False,
						nullable=True,
						default="Бензин (AИ-95,92)")

	consumption = db.Column(db.Float,
					nullable=False,
					default=0.0)

	# relation models
	user_id = db.Column(db.Integer,
						db.ForeignKey('user.id'),
						nullable=False)

	def __repr__(self):
		
		return f"{self.car}"

class Employee(db.Model):

	id = db.Column(db.Integer,
					primary_key=True)

	first_name = db.Column(db.String(60),
							nullable=False,
							default="Иван")

	second_name = db.Column(db.String(60),
							nullable=False,
							default="Иванов")

	surname = db.Column(db.String(60),
						nullable=False,
						default="Иванович")

	quota = db.Column(db.Integer,
					nullable=False,
					default=0)

	r_quota = db.Column(db.Integer,
					nullable=True,
					default=0)

	duration = db.Column(db.String(60),
					nullable=True,
					default=0)

	workday = db.Column(db.Integer,
					nullable=False,
					default=8)

	r_workday = db.Column(db.Integer,
					nullable=False,
					default=8)

	# relation models
	user_id = db.Column(db.Integer,
						db.ForeignKey('user.id'),
						nullable=False)

	def __repr__(self):
		
		return f"{self.second_name} {self.first_name[0]}.{self.surname[0]}."

class Route_List(db.Model):

	id = db.Column(db.Integer,
					primary_key=True)

	route_list = db.Column(db.JSON,
						nullable=True)

	# relation models
	user_id = db.Column(db.Integer,
						db.ForeignKey('user.id'),
						nullable=False)

	def __repr__(self):
		
		return f"Route:{self.id}"

class Review(db.Model):

	id = db.Column(db.Integer,
					primary_key=True)

	text = db.Column(db.String(5000),
						nullable=True)

	def __repr__(self):
		
		return f"Review:{self.text}"
