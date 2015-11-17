#########################################################################
# This module provides url handler dedicated to travel
# Ensure : 
# 	* Creation	--> AddTravel
# 	* Modification	--> ModifyTravel
# 	* Research 	--> SearchTravel & ResultSearchTravel
# 	* Destruction 	--> DeleteTravel
# 	* Register user for a travel 	--> AddUserToTravel
#	* Cancel registration of a user --> RmUserOfTravel
# 	* Display list of travels of a driver 	--> ShowDriverTravels
# 	* Display list of travels of a traveler --> ShowTravelerTravels
#########################################################################

from src.handler import *
from src.travel import *
from src.travelChecker import *
from src.driver import *
from google.appengine.api import memcache
import datetime
import json



############################
### 	TRAVELS HANDLER  ###
############################

# Add a new travel as a driver
class AddTravel(MainHandler):
	####################################################
	# Render the html template bind to choice == "add" #
	####################################################

	def get(self):	
		self.render('base.html', user = self.user, choice="add", datetime_departure = datetime.datetime.now())


	# Powered by Ajax
	def post(self):
		# Save data into a dictionnary
		data = json.loads(self.request.body)
		self.seats = data['seats']

		# Check data via a dedicated agent
		travelerAgent = CheckTravel(data)
		checkedResult = travelerAgent.check()

		if checkedResult['error']:
			logging.info("error in add travel")
			# Merge the 2 dicts
			renderingDict = data.copy()
			renderingDict.update(checkedResult)

			# Send back response
			self.response.out.write(json.dumps(renderingDict))

		else:
			# Bind the new travel to the driver's travel list related to this user
			driver = Driver.get_driver(self.user.key())

			# Check if user is already a driver
			if driver is None:
				logging.info("User "+self.user.nickName+" is not registered as a driver.")
				driver = Driver.register_as_driver(self.user)

			else:
				logging.info("User "+self.user.nickName+" is already a driver.")
					

			# Register the new travel into DB
			travel_data = {
				'departure'			: data['departure'],
				'arrival'			: data['arrival'],
				'places_number'		: int(self.seats),
				'places_remaining'	: int(self.seats),
				'datetime_departure': [data['departure_day'], data['departure_hour'], data['departure_minutes'] ],
				'price'				: int(data['price']),
				'animal'			: data['animals'],
				'smoking'			: data['smoking'],
				'luggage'			: data['luggage']
			}
			t = Travel.register_travel(driver, travel_data)	
			

			# # Send back response
			self.response.out.write(json.dumps({}))


# Modify an owned travel
class ModifyTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "modify" #
	#######################################################

	def get(self):
		self.travel_id = int(self.request.get('id'))
		travel = Travel.by_id(self.travel_id)

		if travel is None:
			logging.info('travel is None')
			self.redirect('/driverTravels')			
		else:
			self.render('base.html', user = self.user, choice = "modify", travel = travel)

	# Powered by Ajax
	def post(self):
		# Save data into a dictionnary
		data = json.loads(self.request.body)
		self.travel_id = int(data['travel_id'])
		self.seats = data['seats']

		# Check data via a dedicated agent
		travelerAgent = CheckTravel(data)
		checkedResult = travelerAgent.check(self.user, self.travel_id)

		if checkedResult['error']:
			# Merge the 2 dicts
			renderingDict = data.copy()
			renderingDict.update(checkedResult)

			# Send back response
			self.response.out.write(json.dumps(renderingDict))

		else:
			# Modify travel in DB
			travel_data = {
				'departure'			: data['departure'],
				'arrival'			: data['arrival'],
				'places_number'		: int(self.seats),
				'places_remaining'	: int(self.seats),
				'datetime_departure': [data['departure_day'], data['departure_hour'], data['departure_minutes'] ],
				'price'				: int(data['price']),
				'animal'			: data['animals'],
				'smoking'			: data['smoking'],
				'luggage'			: data['luggage']
			}

			Travel.modify_travel(self.travel_id, travel_data)
			self.response.out.write(json.dumps({}))


# Delete a previously created travel
class DeleteTravel(MainHandler):

	def get(self):
		self.redirect('/driverTravels')

	# Powered by Ajax
	def post(self):
		data = json.loads(self.request.body)
		Travel.remove_travel(data['travel_id'])
		self.response.out.write(json.dumps({}))


# Look for a travel
class SearchTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "search" #
	#######################################################


	def get(self):
		success_booking = self.request.get('success_booking')
		self.render('base.html', user = self.user, choice = "search", success_booking = success_booking)


	# Powered by Ajax
	def post(self):
		# Save data into dictionnary
		data = json.loads(self.request.body)

		# Check data via a dediacted agent
		searchAgent = CheckSearchTravel(data)
		checkedResult = searchAgent.check()

		if checkedResult['error']:
			self.response.out.write(json.dumps(checkedResult))

		else:
			# Get back travels that match the filter
			travels = Travel.by_filter(departure = data['departure'], 
										arrival = data['arrival'], 
										schedule = [data['departure_day'], data['departure_hour']],
										price_max = data['price_max'], 
										animal_ok = data['animals'], 
										smoking_ok = data['smoking'],
										big_luggage_ok = data['luggage'])		
	
			self.response.out.write(json.dumps({}))
			
			# Store request into memcache to acces it later
			# Delay to handle memcache is of 5 seconds
			memcache.delete(key=str(self.user.key().id()))
			memcache.add(key=str(self.user.key().id()), value=travels, time=5)


# Display result of query handled by SearchTravel.post method
class ResultSearchTravel(MainHandler):

	def get(self):
		# Look into memcache to retrieve latest data of this user
		previous_request = memcache.get(key=str(self.user.key().id()))
		if previous_request is not None:
			self.render('base.html', user=self.user, choice="resultSearch", travels = previous_request)
		else:
			self.redirect('/searchTravel')


# Register traveler for a travel
class AddUserToTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "search" #
	# Implicit rendering 
	# --> cf redirect on SearchTravel class
	#######################################################

	# NOT POWEREDBY AJAX
	def post(self):
		self.travel_id = int(self.request.get('travel_id'))
		self.places_reservation = int(self.request.get('places_reservation'))

		status, msg = Travel.add_traveler(self.user, self.travel_id, self.places_reservation)

		if status:
			logging.info("CORRECT book a travel : "+msg)
			self.redirect('/travelerTravels?success_booking=True')
		else:
			logging.info("ERROR book a travel : "+msg)
			self.redirect('/searchTravel?success_booking=False&msg='+msg)

# Unregister user of a travel
class RmUserOfTravel(MainHandler):

	# Powered by Ajax
	def post(self):		
		data = json.loads(self.request.body)
		self.travel_id = int(data['travel_id'])

		# Get back traveler
		traveler = Traveler.get_traveler(self.user)
		if traveler is not None:
			Travel.remove_user_from_travel(self.travel_id, traveler)
		else:
			logging.info("traveler not found")

		# Ajax response
		self.response.out.write(json.dumps({}))


# Show my travels as a driver
class ShowDriverTravels(MainHandler):
	##############################################################
	# Render the html template bind to choice == "driverTravels" #
	##############################################################

	def get(self):
		# Look for the driver
		driver = Driver.get_driver(self.user.key())

		if driver is not None:
			logging.info("is a driver")
			travels = Travel.by_driver_still_actif(driver)

			if travels.count() > 0:
				logging.info("empty : no")
				
				# Is there a freshly added travel ?
				status = self.request.get('status')
				if status:
					self.render('base.html', user = self.user, choice = "driverTravels", isNew = status, travels = travels)		
				else:
					self.render('base.html', user = self.user, choice = "driverTravels", travels = travels)

				return

		self.render('base.html', user = self.user, choice = "driverTravels", noTravel = True)


		


# Show my travels as a traveller
class ShowTravelerTravels(MainHandler):
	################################################################
	# Render the html template bind to choice == "travelerTravels" #
	################################################################

	def get(self):
		# Look for the traveler
		traveler = Traveler.get_traveler(self.user.key())

		if traveler is not None:
			logging.info("is a traveler")
			travels = Travel.by_traveler(traveler)

			if travels.count() > 0:
				logging.info("empty : no")
				self.render('base.html', user = self.user, 
										choice = "travelerTravels", 
										travels = travels, 
										traveler_key = str(traveler.key()) )
				return

		self.render('base.html', user = self.user, choice = 'travelerTravels', travels = None)

