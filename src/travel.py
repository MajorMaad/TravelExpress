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


from src.driver import *
from google.appengine.ext import db
import datetime
import logging


def travel_key(name = 'default'):
	return db.Key.from_path('travel', name)


class Travel(db.Model):
	# Flag of activity
	actif = db.BooleanProperty(default = True, required = True)

	# Driver
	driver = db.ReferenceProperty(Driver)

	# target locations
	departure = db.StringListProperty(required = True)
	arrival = db.StringListProperty(required = True)

	# Price
	price = db.IntegerProperty(required = True)

	# Schedule
	schedule_day = db.StringProperty(default="monday", required = True)	
	schedule_hour = db.IntegerProperty(default=00, required = True)
	schedule_minute = db.IntegerProperty(default=00, required = True)

	# Preferences
	pref_animal = db.StringProperty(default="ni", required=True)
	pref_smoking = db.StringProperty(default="ni", required=True)
	pref_big_luggage = db.StringProperty(default="ni", required=True)
	

	# Places system
	places_number = db.IntegerProperty(required = True)
	places_remaining = db.IntegerProperty(required = True)

	# Booking system	
	bookers_id = db.ListProperty(int)
	places_bind_to_each_reservation = db.ListProperty(int)




	
	@classmethod
	def register_travel(cls, driver, travel_data):
		travel = Travel(parent = travel_key(),
						driver =  driver.key(),
						departure = cls.split_address(travel_data['departure']),
						arrival = cls.split_address(travel_data['arrival']),
						price = travel_data['price'],
						schedule_day = travel_data['datetime_departure'][0],
						schedule_hour = int(travel_data['datetime_departure'][1]),
						schedule_minute = int(travel_data['datetime_departure'][2]),
						pref_animal = travel_data['animal'],
						pref_smoking = travel_data['smoking'],
						pref_big_luggage = travel_data["luggage"],
						places_number = travel_data['places_number'],
						places_remaining = travel_data['places_number']
			)
		travel.put()


	@classmethod
	def modify_travel(cls, travel_id, travel_data):
		travel = cls.by_id(travel_id)

		travel.departure = cls.split_address(travel_data['departure'])
		travel.arrival = cls.split_address(travel_data['arrival'])
		travel.places_number = travel_data['places_number']
		travel.places_remaining = travel_data['places_number']		
		travel.price = travel_data['price']
		travel.schedule_day = travel_data['datetime_departure'][0]
		travel.schedule_hour = int(travel_data['datetime_departure'][1])
		travel.schedule_minute = int(travel_data['datetime_departure'][2])
		travel.pref_animal = travel_data['animal']
		travel.pref_smoking = travel_data['smoking']
		travel.pref_big_luggage = travel_data['luggage']

		travel.put()


	############################
	### RESEARCH 	METHODS  ###
	############################

	@classmethod
	def by_id(cls, tid):
		return Travel.get_by_id(tid, parent = travel_key())

	@classmethod
	def by_driver_still_actif(cls, driver):
		return Travel.all().filter("driver = ", driver.key()).filter("actif =", True)





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
	def by_filter(cls, departure, arrival, schedule, price_max, animal_ok, smoking_ok, big_luggage_ok, actif = True):

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

		
		if schedule[0] != "":
			query.filter('schedule_day = ', schedule[0])

		if schedule[1] != "":
			query.filter('schedule_hour >= ', int(schedule[1]))
		
		if price_max != "":
			query.filter('price <=', int(price_max))
			query.order('price')


		# Preferences checking
		if animal_ok != "ni":
			logging.info("preferences : animal_ok "+animal_ok)
			query.filter('pref_animal =', animal_ok)

		if smoking_ok != "ni":
			logging.info("preferences : smoking_ok "+smoking_ok)
			query.filter('pref_smoking =', smoking_ok)

		if big_luggage_ok != "ni":
			logging.info("preferences : big_luggage_ok "+big_luggage_ok)
			query.filter('pref_big_luggage =', big_luggage_ok)


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



	############################
	### MODIFICATION METHODS ###
	############################



	############################
	### 	DELETE METHODS 	 ###
	############################

	# Fake a deletion of the travel
	@classmethod
	def remove_travel(cls, travel_id):
		travel = cls.by_id(travel_id)
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
