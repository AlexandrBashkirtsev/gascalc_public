from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, 
					SubmitField, BooleanField, TextAreaField, 
					SelectField, DateTimeField)
from wtforms.validators import (DataRequired, Length, Email,
								EqualTo, ValidationError, InputRequired)
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from gascalc.models import User, Employee, Location, Car
from utils.validators import Price_Float, Consumption_Float, WorkHours_Int
from gascalc import app, db
from flask_login import current_user
    
def employee_choices():      
    return db.session.query(Employee).filter_by(user=current_user)

def base_location_choices():      
    return db.session.query(Location).filter_by(user=current_user,
    											category="Собственная")
def dyn_location_choices():      
    return db.session.query(Location).filter_by(user=current_user)

def car_choices():      
    return db.session.query(Car).filter_by(user=current_user)

class Location_Form(FlaskForm):

	location = StringField('Адрес',
							validators=[DataRequired()])
	comment = StringField('Организация',
							validators=[DataRequired()])
	LAT = StringField('Широта')
	LON = StringField('Долгота')
	category = SelectField('Категория',
							choices=app.config['LOC_CATEGORIES'],
							validators=[DataRequired()])
	quota = StringField('Квота посещений',
						validators=[DataRequired()])
	submit = SubmitField('Добавить')

class General_Settings(FlaskForm):

	org_name = StringField('Организация',
							validators=[DataRequired()])
	org_addr = StringField('Юридический адрес',
							validators=[DataRequired()])
	OGRN 	 = StringField('ОГРН',
							validators=[DataRequired()])
	INN 	 = StringField('ИНН',
							validators=[DataRequired()])
	accountant = StringField('Бухгалтер',
							validators=[DataRequired()])

	submit = SubmitField('Обновить')

class Import_Location_Form(FlaskForm):

	file = FileField('Файл',
					validators = [DataRequired(),
								FileAllowed(app.config['ALLOWED_EXT'])])
	submit_import = SubmitField('Импорт')

class Import_Employee_Form(FlaskForm):

	file = FileField('Файл',
					validators = [DataRequired(),
								FileAllowed(app.config['ALLOWED_EXT'])])
	submit_import = SubmitField('Импорт')

class Import_Car_Form(FlaskForm):

	file = FileField('Файл',
					validators = [DataRequired(),
								FileAllowed(app.config['ALLOWED_EXT'])])
	submit_import = SubmitField('Импорт')

class Employee_Form(FlaskForm):

	first_name = StringField('Имя',
							validators=[DataRequired()])
	second_name = StringField('Фамилия',
							validators=[DataRequired()])
	surname = StringField('Отчество',
							validators=[DataRequired()])
	quota = StringField('Квота поездок',
						validators=[DataRequired()])
	duration = SelectField('Среднее время посещений',
							choices=app.config['EMPL_DURATION'],
							validators=[DataRequired()])
	workday = StringField('Рабочий день, ч',
						validators=[DataRequired(),
									WorkHours_Int])
	submit = SubmitField('Добавить')

class Car_Form(FlaskForm):

	car = StringField('Наименование автомобиля',
							validators=[DataRequired()])
	fuel = StringField('Тип топлива',
							validators=[DataRequired()])
	consumption = StringField('Расход топлива л/100км',
							validators=[DataRequired(),
										Consumption_Float])
	submit = SubmitField('Добавить')

class Resource_Form(FlaskForm):

	resource = StringField('Целевые затраты',
							validators=[DataRequired(),
										Price_Float])

	submit = SubmitField('Подтвердить')

class Set_Calc_Params_Form(FlaskForm):

	price = StringField('Стоимость, руб',
							validators=[DataRequired(),
										Price_Float])
	employee = QuerySelectField('Сотрудник',
								query_factory=employee_choices,
								validators=[DataRequired()])
	car = QuerySelectField('Автомобиль',
							query_factory=car_choices,
							validators=[DataRequired()])
	base_location = QuerySelectField('Точка отправления',
									query_factory=base_location_choices,
									validators=[DataRequired()])
	start_time = DateTimeField('Дата и время выезда',
								validators=[InputRequired()],
                              	format='%Y-%m-%dT%H:%M')
	submit = SubmitField('Рассчитать')

class Manual_Calc_Form(FlaskForm):

	add_location = QuerySelectField('Маршрут',
									query_factory=dyn_location_choices,
									validators=[DataRequired()])
	price = StringField('Стоимость, руб',
							validators=[DataRequired(),
										Price_Float])
	employee = QuerySelectField('Сотрудник',
								query_factory=employee_choices,
								validators=[DataRequired()])
	car = QuerySelectField('Автомобиль',
							query_factory=car_choices,
							validators=[DataRequired()])
	start_time = DateTimeField('Дата и время выезда',
									validators=[InputRequired()],
	                              	format='%Y-%m-%dT%H:%M')
	submit = SubmitField('Рассчитать')
	

class Select_Employee(FlaskForm):

	employee = QuerySelectField('Сотрудник',
							query_factory=employee_choices,
							validators=[DataRequired()])
	submit = SubmitField('Рассчитать')

class Settings_Route_Form(FlaskForm):

	base_location = StringField('Базовый адрес',
							validators=[DataRequired()])
	current_mileage = StringField('Дневной пробег')
	total_mileage = StringField('Общий пробег')
	submit = SubmitField('Рассчитать')

class RegistrationForm(FlaskForm):

	email = StringField('Email',
						validators=[DataRequired(), Email()])
	password = PasswordField('Пароль',
							validators=[DataRequired()])
	confirm_password = PasswordField('Подтвердите пароль',
							validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Зарегистрироваться')

	def validate_email(self, email):

		user = User.query.filter_by(email=email.data).first()
		# if user exists throw validation error
		if user:
			raise ValidationError('Аккаунт с таким адресом уже есть. Попробуйте выбрать другой.')

class LoginForm(FlaskForm):

	email = StringField('Email',
						validators=[DataRequired(), Email()])
	password = PasswordField('Пароль',
							validators=[DataRequired()])
	remember = BooleanField('Запомнить Меня')
	submit = SubmitField('Войти')

class ReviewForm(FlaskForm):

	review = TextAreaField('Отзыв',
						validators=[DataRequired()])
	submit = SubmitField('Отправить')

'''
	add_location = SelectField("Enter a Name",
                       choices=[("777", "sasha")] + [(uuid, name) for uuid, name in possible_names.items()],  # [("", "")] is needed for a placeholder
                       validators=[DataRequired()])

'''