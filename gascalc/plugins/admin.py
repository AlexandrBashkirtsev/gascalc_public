from flask import Flask
from flask import Blueprint
from flask_admin import Admin
from flask_login import current_user, login_required
from gascalc import db, app
from gascalc.forms import Location_Form, Import_Location_Form
from gascalc.models import User, Location, Employee, Car, Route_List, Review
from flask import (render_template, url_for, 
					flash, redirect, request, abort, send_file, make_response)

from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose, helpers

class AdminBlueprint(Blueprint):
    views=None


    def __init__(self,*args, **kargs):
        self.views = []
        return super(AdminBlueprint, self).__init__('admin2', __name__,url_prefix='/admin',static_folder='static', static_url_path='/static/admin')


    def add_view(self, view):
        self.views.append(view)

    def register(self,app, options, first_registration=False):
        admin = Admin(app, name='gascalc')

        for v in self.views:
            admin.add_view(v)

        return super(AdminBlueprint, self).register(app, options, first_registration)

adm = AdminBlueprint('admin2', __name__,url_prefix='/admin',static_folder='static', static_url_path='/static/admin')

class AdminView(ModelView):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.static_folder = 'static'

	def is_accessible(self):

		if current_user.is_authenticated:
			print('USER IS AUTH')
			return current_user.email == 'alex@demo.com'
		else:
			print('USER IS NOT AUTH')
			return False

	def inaccessible_callback(self, name, **kwargs):
		if not self.is_accessible():
			print('redirecting from admin')
			return redirect(url_for('account.login', next=request.url))

adm.add_view(AdminView(User, db.session))
adm.add_view(AdminView(Location, db.session))
adm.add_view(AdminView(Employee, db.session))
adm.add_view(AdminView(Car, db.session))
adm.add_view(AdminView(Route_List, db.session))
adm.add_view(AdminView(Review, db.session))