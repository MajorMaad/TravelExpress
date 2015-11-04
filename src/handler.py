#########################################################################
# This module provides the main url handler
# Mother handler class
# Render template with the jinja2 main rendering function
# Manage user connection and disconnection via securecookies
#########################################################################

import os
import webapp2
import jinja2
import hmac
import logging

from src.user import *



# Template Jinja2 stuff :
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

# Main rendering function
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params).encode('utf-8')

# Hmac secret key
secret = 'thisIsReallyABigSecret'



############################
### 	MAIN HANDLER 	 ###
############################

class MainHandler(webapp2.RequestHandler):

	#Overwrite the initialize method of webapp2
	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		#Look for a cookie session and initialise the user boolean if found
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))



	############################
	### 	SECURE COOKIE 	 ###
	############################	

	# Function called when a user sign up or logged in : Associate a cookie encrypted
	def set_secure_cookie(self, name, db_id):
		cookie_val = self.make_secure_val(db_id)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

	# Encryption of a cookie : The seed is the database ID of the user
	def make_secure_val(self, db_id):
		return '%s|%s' % (db_id, hmac.new(secret, db_id).hexdigest())

	# Decryption of a secure cookie
	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		# If there is a cookie, ensure that it is valid and return the seed of the encryption (ie, the DataBase ID of the user logged in)
		if cookie_val :
			potentialUserID = cookie_val.split('|')[0]
			# Compare the value previously get with the potential seed extracted from the secure cookie
			if (cookie_val == self.make_secure_val(potentialUserID)):
				# self.response.out.write("Cookie found : "+cookie_val+" 	-	initial_val : "+potentialUserID+"	-	secure :"+self.make_secure_val(potentialUserID)+"	-	eval : true.")
				# Return the database ID of the user
				return potentialUserID
		return False


	############################
	### HTTP METHOD HANDLER	 ###
	############################	

	def get(self, **params):
		success_booking = self.request.get('success_booking')
		if self.user:
			self.render('base.html', user=self.user, success_booking = success_booking, **params)
		else:
			self.render('base.html', **params)


	############################
	### JINJA 	RENDERING 	 ###
	############################	

	def render(self, template, **params):
		self.response.out.write(render_str(template, **params))


	############################
	### 	USER SESSION 	 ###
	############################	

	#Set a cookie for the user who just jumped in (via SignUp or LogIn)
	def jumpIn(self, user):
		self.set_secure_cookie('user_id', db_id=str(user.key().id()))
		# Redirection is done via ajax method


	#Log out th euser via a reset of the cookie
	def doExit(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
		self.redirect('/')