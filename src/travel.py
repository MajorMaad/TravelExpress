#########################################################################
# This module describe the model used in database to represent a travel
# Ensure : 
# 	* Creation
# 	* Research in DB
# 	* Modification
# 	* Destruction
#########################################################################



from google.appengine.ext import db
import datetime


def travel_key(name = 'default'):
	return db.Key.from_path('travel', name)


class Travel(db.Model):
	# Flag of activity
	actif = db.BooleanProperty(required = True)

	# Attributes of a travel for the database
	user_id = db.IntegerProperty(required = True)
	departure = db.StringListProperty(required = True)
	arrival = db.StringListProperty(required = True)
	places_number = db.IntegerProperty(required = True)
	places_remaining = db.IntegerProperty(required = True)
	datetime_departure = db.DateTimeProperty(required = True)
	price = db.IntegerProperty(required = True)
	animal_ok = db.StringProperty(required = True)
	smoking_ok = db.StringProperty(required = True)
	big_luggage_ok = db.StringProperty(required = True)
	bookers_id = db.ListProperty(int)



	############################
	### RESEARCH 	METHODS  ###
	############################

	@classmethod
	def by_id(cls, tid):
		return Travel.get_by_id(tid, parent = travel_key())

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

	# Look for a travels
	@classmethod
	def by_filter(cls, departure, arrival, date, animal_ok, smoking_ok, big_luggage_ok, actif = True):
		query = Travel.all()

		if departure != "":
			query.filter('departure =', departure)

		if arrival != "":
			query.filter('arrival =', arrival)

		if date != "":
			# Recompose the date
			date_tab = date.split('-')
			try:
				year = int(date_tab[0])
				month = int(date_tab[1])
				day = int(date_tab[2])

				date_min = datetime.datetime(year, month, day)
				query.filter('datetime_departure >=', date_min)
			except:
				logging.info("date problem")

		if animal_ok != "ni":
			query.filter('animal_ok =', animal_ok)

		if smoking_ok != "ni":
			query.filter('smoking_ok =', smoking_ok)

		if big_luggage_ok != "ni":
			query.filter('big_luggage_ok =', big_luggage_ok)

		# Check only for travel not deleted
		if actif:
			query.filter('actif =', actif)

		return query.order('datetime_departure')



	############################
	### 	ADDING METHODS 	 ###
	############################

	# Add a user to a travel
	@classmethod
	def add_user(cls, user_id, travel_id, places):
		travel = Travel.by_id(travel_id)

		if user_id == travel.user_id:
			return False
		else:
			travel.bookers_id.append(user_id)
			travel.places_remaining -= places
			travel.put()
			return True	

	# Add a travel
	@classmethod
	def add_travel(cls, travel_data):
		# Split the departure and arrival data to determine country, province, and city
		full_dep_addr = travel_data['departure'].split(', ')
		full_arr_addr = travel_data['arrival'].split(', ')

		if len(full_dep_addr) >= 3:
			full_dep_addr = full_dep_addr[-3:]

		if len(full_arr_addr) >= 3:
			full_arr_addr = full_arr_addr[-3:]

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
		full_dep_addr = travel_data['departure'].split(', ')
		full_arr_addr = travel_data['arrival'].split(', ')

		if len(full_dep_addr) >= 3:
			full_dep_addr = full_dep_addr[-3:]

		if len(full_arr_addr) >= 3:
			full_arr_addr = full_arr_addr[-3:]

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
