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
			# Merge the 2 dicts
			renderingDict = data.copy()
			renderingDict.update(checkedResult)

			# datetime cannot be json serializable
			renderingDict.pop('datetime_departure', None)

			# Send back response
			self.response.out.write(json.dumps(renderingDict))

		else:
			# Register the new travel into DB
			travel_data = {
				'user_id'			: self.user.key().id(),
				'departure'			: data['departure'],
				'arrival'			: data['arrival'],
				'places_number'		: int(self.seats),
				'places_remaining'	: int(self.seats),
				'datetime_departure': checkedResult['datetime_departure'],
				'price'				: int(data['price']),
				'animal'			: data['animals'],
				'smoking'			: data['smoking'],
				'luggage'			: data['luggage']
			}
			travel = Travel.add_travel(travel_data)	

			# Send back response
			self.response.out.write(json.dumps({}))


# Modify an owned travel
class ModifyTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "modify" #
	#######################################################

	def get(self):
		try:
			self.travel_id = int(self.request.get('id'))
			travel = Travel.by_id(self.travel_id)
			self.render('base.html', user = self.user, choice = "modify", travel = travel)
		except:
			self.redirect('/driverTravels')
		

	# Powered by Ajax
	def post(self):
		# Save data into a dictionnary
		data = json.loads(self.request.body)
		self.travel_id = int(data['travel_id'])
		self.seats = data['seats']

		# Check data via a dedicated agent
		travelerAgent = CheckTravel(data)
		checkedResult = travelerAgent.check()

		if checkedResult['error']:
			# Merge the 2 dicts
			renderingDict = data.copy()
			renderingDict.update(checkedResult)

			# datetime cannot be json serializable
			renderingDict.pop('datetime_departure', None)

			# Send back response
			self.response.out.write(json.dumps(renderingDict))

		else:
			for k in data:
				logging.info('my data are : %r : %r '%(k, data[k]))


			# Register the new travel into DB
			travel_data = {
				'user_id'			: self.user.key().id(),
				'departure'			: data['departure'],
				'arrival'			: data['arrival'],
				'places_number'		: int(self.seats),
				'places_remaining'	: int(self.seats),
				'datetime_departure': checkedResult['datetime_departure'],
				'price'				: int(data['price']),
				'animal'			: data['animals'],
				'smoking'			: data['smoking'],
				'luggage'			: data['luggage']
			}
			travel = Travel.modify_travel(self.travel_id, travel_data)
			self.response.out.write(json.dumps({}))


# Look for a travel
class SearchTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "search" #
	#######################################################


	def get(self):
		today = datetime.datetime.now().strftime("%Y-%m-%d")
		success_booking = self.request.get('success_booking')
		self.render('base.html', user = self.user, choice = "search", today = today, success_booking = success_booking)


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
										date = data['departure_date'],
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


# Delete a previously created travel
class DeleteTravel(MainHandler):

	def get(self):
		self.redirect('/driverTravels')

	# Powered by Ajax
	def post(self):
		data = json.loads(self.request.body)
		Travel.remove_travel(data['travel_id'], self.user.key().id())
		self.response.out.write(json.dumps({}))


# Register for a travel as a traveller
class AddUserToTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "search" #
	# Implicit rendering 
	# --> cf redirect on SearchTravel class
	#######################################################

	# NOT POWEREDBY AJAX
	def post(self):
		self.user_id = self.user.key().id()
		self.travel_id = int(self.request.get('travel_id'))
		self.places_reservation = int(self.request.get('places_reservation'))		

		status, msg = Travel.add_user(self.user_id, self.travel_id, self.places_reservation)

		if status:
			logging.info("CORRECT book a travel : "+msg)
			self.redirect('/?success_booking=True')
		else:
			logging.info("ERROR book a travel : "+msg)
			self.redirect('/searchTravel?success_booking=False')

# Unregister user of a travel
class RmUserOfTravel(MainHandler):

	# Powered by Ajax
	def post(self):
		self.user_id = int(self.user.key().id())
		
		data = json.loads(self.request.body)
		self.travel_id = int(data['travel_id'])

		Travel.remove_user_from_travel(self.travel_id, self.user_id)

		# Ajax response
		self.response.out.write(json.dumps({}))





# Show my travels as a driver
class ShowDriverTravels(MainHandler):
	##############################################################
	# Render the html template bind to choice == "driverTravels" #
	##############################################################

	def get(self):
		travels = Travel.by_author_still_actif(self.user.key().id())
		if travels.count() == 0:
			logging.info("empty : yes")
			self.render('base.html', user = self.user, choice = "driverTravels", noTravel = True)
		else:
			logging.info("empty : no")
			self.render('base.html', user = self.user, choice = "driverTravels", travels = travels)


		


# Show my travels as a traveller
class ShowTravelerTravels(MainHandler):
	################################################################
	# Render the html template bind to choice == "travelerTravels" #
	################################################################

	def get(self):
		travels = Travel.by_passenger(self.user.key().id())
		travel_id_email = []

		# Getting email adress of drivers to be able to send a message
		for travel in travels:
			driver_mail = User.by_id(travel.user_id).email
			couple_travel_mail = (travel.key().id(), driver_mail)
			travel_id_email.append(couple_travel_mail)

		self.render('base.html', user = self.user, choice = 'travelerTravels', travels = travels, couples_id_mail = travel_id_email)

