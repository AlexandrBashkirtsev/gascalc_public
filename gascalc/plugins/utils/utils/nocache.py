from functools import wraps, update_wrapper
from datetime import datetime
from flask import make_response, redirect, url_for
from flask_login import current_user

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache, view)

def requires_access_level(access_level):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			print(current_user.subscription)
			if current_user.subscription == 'admin':
				return f(*args, **kwargs)
			if current_user.subscription != access_level:
				return redirect(url_for('account.register'))
			return f(*args, **kwargs)
		return decorated_function
	return decorator