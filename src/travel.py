#########################################################################
# This module describe the model used in database to represent a travel
# Ensure : 
# 	* Creation			--> add_travel
# 	* Research in DB 	--> by_... methods
# 	* Modification 		--> modify_travel
# 	* User Booking 		--> add_user
# 	* Cancel Booking 	--> remove_user_from_travel
# 	* Destruction 		--> remove_travel
# 
# Important !!!!!
# 	* An object with the '.filter' method is a db.Query 
# 	* This type is mandatory to request several entities in DB
# 	* Raise Error when .filter with several inequalities (db restriction)
#########################################################################



from google.appengine.ext import db
import datetime
import logging


def travel_key(name = 'default'):
	return db.Key.from_path('travel', name)


class Travel(db.Model):
	# Flag of activity
	actif = db.BooleanProperty(required = True)

	# Attributes of a travel for the database
	# Owner
	user_id = db.IntegerProperty(required = True)

	# target locations
	departure = db.StringListProperty(required = True)
	arrival = db.StringListProperty(required = True)

	# Date / Price / Preferences
	datetime_departure = db.DateTimeProperty(required = True)
	price = db.IntegerProperty(required = True)
	animal_ok = db.StringProperty(required = True)
	smoking_ok = db.StringProperty(required = True)
	big_luggage_ok = db.StringProperty(required = True)

	# Places system
	places_number = db.IntegerProperty(required = True)
	places_remaining = db.IntegerProperty(required = True)

	# Booking system	
	bookers_id = db.ListProperty(int)
	places_bind_to_each_reservation = db.ListProperty(int)




	############################
	### RESEARCH 	METHODS  ###
	############################


	@classmethod
	def by_id(cls, tid):
		return Travel.get_by_id(tid, parent = travel_key())

	@classmethod
	def get_multi(cls, list_ids):
		return [cls.by_id(x) for x in list_ids]

	# Show my travels (traveler)
	@classmethod
	def by_passenger(cls, user_id):
		return Travel.all().filter('bookers_id =', user_id).order('datetime_departure')

	# Show my travel (driver)
	@classmethod
	def by_author(cls, user_id):
		return Travel.all().filter('user_id =', user_id).order('datetime_departure')

	@classmethod
	def by_author_still_actif(cls, user_id):
		return Travel.all().filter('user_id =', user_id).filter('actif =', True ).order('datetime_departure')

	
	############################
	### 	ADVANCE RESEARCH ###
	############################

	@classmethod
	def by_filter(cls, departure, arrival, date, price_max, animal_ok, smoking_ok, big_luggage_ok, actif = True):

		query = Travel.all()

		# Check only for travel having the flag actif
		if actif:
			query.filter('actif =', actif)

		if departure != "":
			departure_addr = cls.split_address(departure)
			for part in departure_addr:
				query.filter('departure =', part)

		if arrival != "":
			arrival_addr = cls.split_address(arrival)
			for part in arrival_addr:
				query.filter('arrival =', part)

		# #######################################################
		# App Engine DataStore cannot handle several inequalities
		# --> filter can only handle date XOR price_max : not both
		# #######################################################

		
		if date != "":
			# 1 ) Date case
			date_tab = date.split('-')
			try:
				year = int(date_tab[0])
				month = int(date_tab[1])
				day = int(date_tab[2])
				date_min = datetime.datetime(year, month, day)

				# Filter with inequality
				query.filter('datetime_departure >=', date_min)	
				query.order('datetime_departure')
			except:
				logging.info("date problem")
		
		elif price_max != "":
			# 2 ) XOR case price (cf elif)
			# Filter with inequality
			query.filter('price <=', int(price_max))
			query.order('price')


		# Preferences checking
		if animal_ok != "ni":
			logging.info("preferences : animal_ok "+animal_ok)
			query.filter('animal_ok =', animal_ok)

		if smoking_ok != "ni":
			logging.info("preferences : smoking_ok "+smoking_ok)
			query.filter('smoking_ok =', smoking_ok)

		if big_luggage_ok != "ni":
			logging.info("preferences : big_luggage_ok "+big_luggage_ok)
			query.filter('big_luggage_ok =', big_luggage_ok)


		# Return the db.Query object
		return query
			
		



	############################
	### 	ADDING METHODS 	 ###
	############################

	# Add a user to a travel
	@classmethod
	def add_user(cls, user_id, travel_id, places):
		travel = Travel.by_id(travel_id)

		# Traveler cannot be the driver
		if user_id == travel.user_id:
			return (False, "You cannot book this travel : you re the driver.")

		# traveler cannot book twice the same travel
		if user_id in travel.bookers_id:
			return (False, "You have already book this travel.")

		# Ensure there are enough places
		if (travel.places_remaining - places ) < 0:
			return (False, "There are not enough places.")

		# Register the user and the associated number of places
		travel.bookers_id.append(user_id)
		travel.places_bind_to_each_reservation.append(places)

		# Update the places system
		travel.places_remaining -= places

		# Register and return status withstatus message
		travel.put()
		return (True, "Your reservation has been saved.")

	# Add a travel
	@classmethod
	def add_travel(cls, travel_data):
		# Split the departure and arrival data to determine country, province, and city
		# Split the departure and arrival data to determine country, province, and city
		full_dep_addr = cls.split_address(travel_data['departure'])
		full_arr_addr = cls.split_address(travel_data['arrival'])

		travel = None
		travel = Travel(parent = travel_key(),
						actif = True,
						user_id = travel_data['user_id'],
						departure = full_dep_addr,
						arrival = full_arr_addr,
						places_number = travel_data['places_number'],
						places_remaining = travel_data['places_number'],
						datetime_departure = travel_data['datetime_departure'],
						price = travel_data['price'],
						animal_ok = travel_data['animal'],
						smoking_ok = travel_data['smoking'],
						big_luggage_ok = travel_data['luggage'])

		travel.put()
		return travel

	############################
	### MODIFICATION METHODS ###
	############################

	# Modify a travel
	@classmethod
	def modify_travel(cls, travel_id, travel_data):
		travel = cls.by_id(travel_id)

		# Split the departure and arrival data to determine country, province, and city
		full_dep_addr = cls.split_address(travel_data['departure'])
		full_arr_addr = cls.split_address(travel_data['arrival'])

		travel.departure = full_dep_addr
		travel.arrival = full_arr_addr
		travel.places_number = travel_data['places_number']
		travel.places_remaining = travel_data['places_number']
		travel.datetime_departure = travel_data['datetime_departure']
		travel.price = travel_data['price']
		travel.animal_ok = travel_data['animal']
		travel.smoking_ok = travel_data['smoking']
		travel.big_luggage_ok = travel_data['luggage']

		travel.put()
		return travel

	############################
	### 	DELETE METHODS 	 ###
	############################

	# Fake a deletion of the travel
	@classmethod
	def remove_travel(cls, travel_id, user_id):
		travel = cls.by_id(travel_id)

		# Make sure it is the driver who deletes it
		if (travel.user_id == user_id):
			travel.actif = False
			travel.put()


	# Remove user from a privious booked travel
	@classmethod
	def remove_user_from_travel(cls, travel_id, user_id):
		travel = cls.by_id(travel_id)

		# Make sure user was in this travel
		if user_id in travel.bookers_id:
			
			# Get index of the user
			idx = travel.bookers_id.index(user_id) 

			# Remove user and the corresponding number of reserved places
			travel.bookers_id.remove(user_id)
			places = travel.places_bind_to_each_reservation.pop(idx)

			# Update the places_remaining variable
			travel.places_remaining += places

			travel.put()


	############################
	### 	TOOLS METHODS 	 ###
	############################


	@classmethod
	def split_address(cls, address):
		full_addr = address.split(', ')
		if len(full_addr) >= 3:
			return full_addr[-3:]
		return full_addr
