# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from geopy.geocoders import ArcGIS
from yandex_checkout import Configuration

# app init
app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
# get settings from settings.json
SENSITIVE = os.path.join(BASE_DIR, "settings.json")
overrides = json.loads(open(SENS_SETTINGS).read())

# reload templates on run, like map template
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app config
app.config['SECRET_KEY'] = SENSITIVE['SECRET_KEY']
# API Key to openrouteservice
app.config['ROUTES_API_KEY'] = SENSITIVE['ROUTES_API_KEY']
# API link to openrouteservice
app.config['ROUTES_API'] = SENSITIVE['ROUTES_API']
# database address
app.config['SQLALCHEMY_DATABASE_URI'] = SENSITIVE['SQLALCHEMY_DATABASE_URI']
# geocoder instance
app.config['GEOCODER'] = ArcGIS()

# yandex money id
app.config['SHOP_ID'] = SENSITIVE['SHOP_ID']
app.config['KEY'] = 'test_Fh8hUAVVBGUGbjmlzba6TB0iyUbos_lueTHE-axOwM0'

Configuration.account_id = app.config['SHOP_ID']
Configuration.secret_key = app.config['KEY']

# database init
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# hashing utilities
bcrypt = Bcrypt(app)

# folders config
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'input_files')
MAPS_FOLDER = os.path.join(APP_ROOT, 'templates','maps')

# upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# allowed extensions
app.config['ALLOWED_EXT'] = ['csv', 'xls', 'xlsx']

# maps folder (not needed, maps generated as html repr)
app.config['MAPS_FOLDER'] = MAPS_FOLDER

# list of categories
app.config['LOC_CATEGORIES'] = [('Клиент','Клиент'),
								('Поставщик','Поставщик'),
								('Собственная','Собственная'),
								('Другое','Другое')]

app.config['EMPL_DURATION'] = [('short','Быстро (5-10 мин)'),
								('medium','Стандартно (10-30 мин)'),
								('long','Долго (30-90 мин)')]

app.config['OIL_CATEGORIES'] = [('Е-95','Е-95'),
								('Е-98','Е-98'),
								('Дизель','Дизель'),
								('Газ','Газ')]

app.config['SUMMARY_INIT'] = {
								'locations':[],
								'resource_marge':None,
								'summary':
										{'fuel_marge':0.0,
										 'distance':0}
								}

app.config['SETTINGS_INIT'] = {
								'org_name':'',
								'org_address':'',
								'INN':'XXXXXXXXXX',
								'OGRN':'XXXXXXXXXXXXX',
								'accountant':'',
								'driver_id':None,
								'driver_fullname':'',
								'driver_shortname':'',
								'car_id':None,
								'car':'',
								'fuel':'',
								'consumption':0.0,
								'base_location_id':None,
								'resource_price':0
								
								}

login_manager = LoginManager(app)
login_manager.login_view = 'account.login'
login_manager.login_message_category = 'info'

# blueprints
import utils
from .plugins import add_locations
from .plugins import account
from .plugins import mapping
from .plugins import add_employees
from .plugins import calculations
from .plugins import add_cars
from .plugins import settings
from .plugins import landing
from .plugins import adm

app.register_blueprint(add_locations)
app.register_blueprint(account)
app.register_blueprint(mapping)
app.register_blueprint(add_employees)
app.register_blueprint(calculations)
app.register_blueprint(add_cars)
app.register_blueprint(settings)
app.register_blueprint(landing)
app.register_blueprint(adm)