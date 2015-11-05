# This module describe the model used in database to represent a driver
# Ensure : 
# 	* Reference to the user
# 	* Reference of a list of preferences
# 	* Reference to a grade as a driver
#########################################################################

from src.user import *


class Driver(db.Model):

	user_id = db.ReferenceProperty(User)
	preferences = db.StringListProperty(default=["ni", "ni", "ni"], required=True)
	grade = db.IntegerProperty(required=False)


	@classmethod
	def register_as_driver(cls, user):
		driver = Driver()
		driver.user_id = user
		driver.put()
		return driver

	@classmethod
	def get_driver(cls, user_key):
		query = Driver.all()
		query.filter("user_id = ", user_key)
		return query.get()






