from wtforms.validators import ValidationError

class PriceError(Exception):
    pass

class ConsumptionError(Exception):
    pass

class WorkhoursError0(Exception):
    pass

class WorkhoursError24(Exception):
    pass

# validate float price
def Price_Float(form, field):

	try:
		float(field.data)
		
		if float(field.data) <= 0.0:
			raise PriceError('PriceError\n')
	
	except ValueError:
		raise ValidationError('Нужно указать цену.\n')

	except PriceError:
		raise ValidationError('Цена должна быть положительной.\n')

# validate float consumption
def Consumption_Float(form, field):

	try:
		float(field.data)
		if float(field.data) <= 0.0:
			raise ConsumptionError('ConsumptionError\n')
	
	except ValueError:
		raise ValidationError('Нужно указать расход.\n')

	except ConsumptionError:
		raise ValidationError('Расход должен быть положительным.\n')

# validate float consumption
def WorkHours_Int(form, field):

	try:
		int(field.data)
		
		if int(field.data) <= 0:
			raise WorkhoursError0('WorkhoursError0\n')
		
		if int(field.data) > 24:
			raise WorkhoursError24('WorkhoursError24\n')

	except ValueError:
		raise ValidationError('Нужно указать часы работы\n')

	except WorkhoursError0:
		raise ValidationError('Должен быть хотя-бы один час рабочего времени\n')

	except WorkhoursError24:
		raise ValidationError('Рабочий день не должен превышать 24 часа.\n')