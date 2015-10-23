# Class describing a travel publication
from google.appengine.ext import db
from user import User
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
	passengers = db.ListProperty(User)
	# preferences = db.ListProperty(Preference)

	@classmethod
	def by_id(cls, uid):
		return Travel.get_by_id(uid, parent = travel_key())

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
