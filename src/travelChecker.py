#####################################################################
# This module ensure data received from the client are correct for :
# 	* add / modify a travel --> CheckTravel
# 	* research a travel 	--> CheckSearchTravel
#####################################################################



from src.travel import *


############################################
### NEW Travel PROCESS CHECKER ###
############################################
class CheckTravel():
	def __init__(self, data, *args, **kwargs):
		self.departure 			= data['departure']
		self.arrival 			= data['arrival']
		self.price 				= data['price']

	def check(self, user=None, travel_id=None):
		# The checking status will be returned as a dictionnary
		checkingResult = {}
		error = False

		# Modification case :
		if user is not None and travel_id is not None:
			# Ensure this travel is owned by the user
			driver = Driver.get_driver(user.key())

			if driver is None:
				checkingResult['error_no_driver'] = "You are not registered as a driver."
				error = True

			if not error :
				owned = False
				driver_travels = Travel.by_driver_still_actif(driver)
				for t in driver_travels:
					if t.key().id() == travel_id:					
						owned = True
						break

				if not owned :
					checkingResult['error_wrong_driver'] = "You are not the driver of this travel."
					error = True

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

		if self.price_max != '' and int(self.price_max) <= 0:
			checkingResult['error_price'] = "price must be positive"
			checkingResult['error'] = True	

		return checkingResult
