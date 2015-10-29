# Class describing a user
from google.appengine.ext import db
from string import letters
import random
import hashlib

import logging



def user_key(name = 'default'):
	return db.Key.from_path('user', name)

def make_pw_hash(nickName, pw, salt=None):
	if not salt:
		salt = ''.join(random.choice(letters) for x in xrange(7))
	h = hashlib.sha256(nickName + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def reverse_pw(nickName, password, hashed_pw):
	salt = hashed_pw.split(',')[0]
	return hashed_pw == make_pw_hash(nickName, password, salt)

class User(db.Model):
	name = db.StringProperty(required = False)
	firstName = db.StringProperty(required = False)
	nickName = db.StringProperty(required = True)
	email = db.StringProperty(required = True)
	password = db.StringProperty(required = True)


	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent = user_key())

	@classmethod
	def by_name(cls, name):
		return User.all().filter('name =', name).get()

	@classmethod
	def by_firstName(cls, firstName):
		return User.all().filter('firstName =', firstName).get()

	@classmethod
	def by_nickName(cls, nickName):
		return User.all().filter('nickName =', nickName).get()

	@classmethod
	def by_email(cls, email):
		return User.all().filter('email =', email).get()

	@classmethod
	def register(cls, user_data):
		#Hash the user password :
		hash_pwd = make_pw_hash(user_data['nickName'], user_data['password'])
		#Return an instance of user
		return User(parent = user_key(),
					name = user_data['name'],
					firstName = user_data['firstName'],
					nickName = user_data['nickName'],
					email = user_data['email'],
					password = hash_pwd);

	@classmethod
	def logIn(cls, user_data, password, is_email):
		user = None
		if is_email:
			user = cls.by_email(user_data)
		else:
			user = cls.by_nickName(user_data)

		if user and reverse_pw(user.nickName, password, user.password):
			return user







