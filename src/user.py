# Class describing a user
from google.appengine.ext import db


class User(db.model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty()
	phone = db.StringProperty()
	address = db.StringProperty()

	


