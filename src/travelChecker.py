from src.travel import *


# This class checks if all required information is well given
class CheckAddTravel():


	def __init__(self, data, *args, **kwargs):
		self.departure 			= data['departure']
		self.arrival 			= data['arrival']
		self.departure_date 	= data['departure_date']
		self.departure_hour 	= data['departure_hour']
		self.departure_minutes 	= data['departure_minutes']
		self.price 				= data['price']
		self.animals 			= data['animals']
		self.smoking 			= data['smoking']
		self.luggage 			= data['luggage']


	def check(self):
		# The checking status will be returned as a dictionnary
		checkingResult = {}

		error = False

		# Departure and arrival must be different
		if self.departure == self.arrival:
			checkingResult['error_samedeparture'] = "cannot be the same as departure"
			error = True

		# Datetime checking
		date_tab = self.departure_date.split('-')
		try:
			year = int(date_tab[0])
			month = int(date_tab[1])
			day = int(date_tab[2])
		except ValueError:
			year = 2000
			month = 1
			day = 1

		hour = int(self.departure_hour)
		minutes = int(self.departure_minutes)

		departure_datetime = datetime.datetime(year, month, day, hour, minutes)
		checkingResult['datetime_departure'] = departure_datetime

		now = datetime.datetime.now()

		# Datetime of departure must be after now
		if departure_datetime <= now:
			checkingResult['error_datetime'] = "Wrong Date / Time"
			error = True
		
		

		#price checking
		try:
			self.price = int(self.price)
		except ValueError:
			checkingResult['error_price'] = "Price must be an integer"
			error = True

		if self.price <= 0 :			
			checkingResult['error_price'] = "Price cannot be negative"
			error = True

		if self.price > 10000:
			checkingResult['error_price'] = "Are you kidding me ????"
			error = True


		# Checking global result
		checkingResult['error'] = error

		#Preferences checking
		checkingResult['animal_ok'] = self.animals == 'ok'
		checkingResult['smoking_ok'] = self.smoking == 'ok'
		checkingResult['big_luggage_ok'] = self.luggage == 'suitcase'

		return checkingResult
		
