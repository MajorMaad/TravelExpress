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
from src.traveler import *
from google.appengine.ext import db
import datetime
import logging
import time


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
	bookers_id = db.StringListProperty()
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
	def by_traveler(cls, traveler):
		return Travel.all().filter("bookers_id = ", str(traveler.key()))






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
	def add_traveler(cls, user, travel_id, places):

		# Ensure the given user is not the driver of this travel
		user_driver = Driver.get_driver(user.key())

		if user_driver is not None:
			user_driver_travels = Travel.by_driver_still_actif(user_driver)
			for t in user_driver_travels:
				if t.key().id() == travel_id:
					return (False, "You cannot book this travel : you are the driver.")

		# Check if user is already a traveler
		traveler = Traveler.get_traveler(user.key())
		
		if traveler is None:
			logging.info("User "+user.nickName+" is not registered as a traveler.")
			traveler = Traveler.register_as_traveler(user)
		else:
			logging.info("User "+user.nickName+" is already a traveler.")

			
		this_travel = Travel.by_id(travel_id)
		if this_travel is None:
			logging.info("Travel doesn't exist")
			return(False, "Travel doesn't exists")
		
		else:
			# Check if required places matches the remaining places
			if (this_travel.places_remaining - places ) < 0:
				logging.info("Not enough place available")
				return(False, "Not engouh seats available")
			
			else:
				# Check if this traveler is not already registered for this Traveler
				target_key = str(traveler.key())

				if target_key in this_travel.bookers_id:					
					logging.info("Traveler already registered for this travel")

					# Update traveler reservation
					index = this_travel.bookers_id.index(target_key)
					this_travel.places_bind_to_each_reservation[index] += places

				else:
					logging.info("ADDING a new traveler")
					
					# Book the Traveler
					this_travel.bookers_id.append(target_key)
					this_travel.places_bind_to_each_reservation.append(places)	

				
				# Update remaining places
				this_travel.places_remaining -= places
				# Save into DB
				this_travel.put(deadline=1.5)
				time.sleep(1.5)
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
	def remove_user_from_travel(cls, travel_id, traveler):
		# get back travel and traveler key
		this_travel = cls.by_id(travel_id)
		traveler_key = str(traveler.key())

		if traveler_key in this_travel.bookers_id:
			index = this_travel.bookers_id.index(traveler_key)

			# Remove User and corresponding places from lists
			this_travel.bookers_id.pop(index)
			new_places = this_travel.places_bind_to_each_reservation.pop(index)

			# Update places remaining
			this_travel.places_remaining += new_places
			this_travel.put()


	############################
	### 	TOOLS METHODS 	 ###
	############################


	@classmethod
	def split_address(cls, address):
		full_addr = address.split(', ')
		if len(full_addr) >= 3:
			return full_addr[-3:]
		return full_addr
