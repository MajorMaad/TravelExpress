# Class describing a user
from google.appengine.ext import db
from string import letters
import random
import hashlib



def user_key(name = 'default'):
	return db.Key.from_path('user', name)

def make_pw_hash(name, pw):
    salt = ''.join(random.choice(letters) for x in xrange(7))
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

class User(db.Model):


	name = db.StringProperty(required = True)
	firstName = db.StringProperty(required = True)
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






