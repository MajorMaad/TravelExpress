#####################################################################
# This module ensure data received from the client are correct for :
# 	* add / modify a travel --> CheckTravel
# 	* research a travel 	--> CheckSearchTravel
#####################################################################



from src.travel import *


############################################
### NEW AND MODIFICATION PROCESS CHECKER ###
############################################
class CheckTravel():
	def __init__(self, data, *args, **kwargs):
		self.departure 			= data['departure']
		self.arrival 			= data['arrival']
		self.price 				= data['price']

	def check(self):
		# The checking status will be returned as a dictionnary
		checkingResult = {}
		error = False

		# Departure and arrival checking
		if self.departure == "":
			checkingResult['error_departure'] = "You have to set a departure location"
			error = True 

		elif self.arrival == "":
			checkingResult['error_arrival'] = "You have to set a destination location"
			error = True 

		elif self.departure == self.arrival:
			checkingResult['error_samedeparture'] = "Departure and destination must be different places"
			error = True
	
		#price checking
		try:
			self.price = int(self.price)
			if self.price <= 0 :			
				checkingResult['error_price'] = "Price cannot be negative"
				error = True

			if self.price > 10000:
				checkingResult['error_price'] = "Are you kidding me ????"
				error = True
		except ValueError:
			checkingResult['error_price'] = "Price must be an integer"
			error = True

		# Checking global result
		checkingResult['error'] = error

		return checkingResult


################################
### RESEARCH PROCESS CHECKER ###
################################
class CheckSearchTravel():	
	def __init__(self, data, *args, **kwargs):
		self.departure 			= data['departure']
		self.arrival 			= data['arrival']
		self.departure_date 	= data['departure_date']
		self.price_max 			= data['price_max']

	def check(self):
		# The checking status will be returned as a dictionnary
		checkingResult = {}
		checkingResult['error'] = False

		if self.departure == '' and self.arrival == '':
			checkingResult['error_src_dest'] = "No destination and no arrival"
			checkingResult['error'] = True		

		# Departure and arrival must be different
		elif self.departure == self.arrival:
			checkingResult['error_samedeparture'] = "Cannot be the same as departure"
			checkingResult['error'] = True		

		# Ensure date is posterior
		if self.departure_date != '':
			date_tab = self.departure_date.split('-')
			try:
				year = int(date_tab[0])
				month = int(date_tab[1])
				day = int(date_tab[2])
			except ValueError:
				year = 2000
				month = 1
				day = 1
			
			search_date = datetime.datetime(year, month, day)
			yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

			# Datetime of departure must be after now
			if search_date < yesterday:
				checkingResult['error_datetime'] = "You must enter a posterior date"
				checkingResult['error'] = True	

		if self.price_max != '' and int(self.price_max) <= 0:
				checkingResult['error_price'] = "price must be positive"
				checkingResult['error'] = True	

		return checkingResult
