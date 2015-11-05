# This module describe the model used in database to represent a traveler
# Ensure : 
# 	* Reference to the user
# 	* Reference of a list of travels
# 	* Reference of a list of preferences
#########################################################################

from src.user import *


class Traveler(db.Model):

	user_id = db.ReferenceProperty(User)
	preferences = db.StringListProperty(default=["ni", "ni", "ni"], required=True)
	travels = db.ListProperty(int)


	@classmethod
	def register_as_traveler(cls, user):
		traveler = Traveler()
		traveler.user_id = user
		traveler.put()
		return traveler

	@classmethod
	def get_traveler(cls, user_key):
		query = Traveler.all()
		query.filter("user_id = ", user_key)
		return query.get()

