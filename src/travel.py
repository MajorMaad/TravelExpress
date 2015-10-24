# Class describing a travel publication
from google.appengine.ext import db
from user import *
import datetime


def travel_key(name = 'default'):
	return db.Key.from_path('travel', name)


class Travel(db.Model):

	user_id = db.IntegerProperty(required = True)
	departure = db.StringProperty(required = True)
	arrival = db.StringProperty(required = True)
	places_number = db.IntegerProperty(required = True)
	places_remaining = db.IntegerProperty(required = True)
	datetime_departure = db.DateTimeProperty(required = True)
	price = db.IntegerProperty(required = True)
	passengers_id = db.ListProperty(int)
	# preferences_id = db.ListProperty(int)

	@classmethod
	def by_id(cls, uid):
		return Travel.get_by_id(uid, parent = travel_key())

	# Show my travels (traveler)
	@classmethod
	def by_passenger(cls, user_id):
		return Travel.all().filter('passengers_id =', user_id).get()

	# Look for a travels
	@classmethod
	def by_filter(cls, departure = None, arrival = None, places_remaining = None, date_min = datetime.datetime.now(), price_max = None, preferences = None):
		query = Travel.all()
		query.filter('datetime_departure >=', date_min)

		if departure is not None:
			query.filter('departure =', departure)

		if arrival is not None:
			query.filter('arrival =', arrival)

		if places_remaining is not None:
			query.filter('places_remaining >=', places_remaining)

		if price_max is not None:
			query.filter('price <=', price_max)

		# TODO : gérer préférences

		return query.get()

	# Show my travel (driver)
	@classmethod
	def by_author(cls, user_id):
		return Travel.all().filter('user_id =', user_id).get()

	# Add a travel
	@classmethod
	def add_travel(cls, travel_data):
		travel = None
		travel = Travel(parent = travel_key(),
						user_id = travel_data['user_id']
						departure = travel_data['departure'],
						arrival = travel_data['arrival'],
						places_number = travel_data['places_number'],
						places_remaining = travel_data['places_number'],
						datetime_departure = travel_data['datetime_departure'],
						price = travel_data['price'],
						passengers_id = None)

		travel.put()
		return travel

	# Modify a travel
	@classmethod
	def modify_travel(cls, travel_id, departure = None, arrival = None, places_remaining = None, date_min = None, price_max = None, preferences = None):
		travel = cls.by_id(travel_id)

		if departure is not None:
			travel.departure = departure

		if arrival is not None:
			travel.arrival = arrival

		if places_number is not None:
			travel.places_number = places_number

		if datetime_departure is not None:
			travel.datetime_departure = datetime_departure

		if price is not None:
			travel.price = price

		travel.put()
		return travel

	# Delete a travel
	@classmethod
	def remove_travel(cls, travel_id):
		travel = cls.by_id(travel_id)
		travel.delete()
