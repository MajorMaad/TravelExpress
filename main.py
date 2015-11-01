#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import logging
import webapp2
import hmac
import datetime
import json


# Personnal imports :
from src.user import *
from src.travel import *
from src.registration import *
from src.travelChecker import *


# Template Jinja2 stuff :
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

# Main rendering function
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

# Hmac secret key
secret = 'thisIsReallyABigSecret'



############################
### 	MAIN HANDLER 	 ###
############################

# Mother handler class
# Render template with the kinka main rendering function
# Manage user connection and disconnection via securecookies
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






############################
### REGISTRATION HANDLER ###
############################

# Registration of a new user
class SignUp(MainHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		data = json.loads(self.request.body)
		
		#Check sign up informations via a dedicated agent
		checkAgent = CheckSignUp()
		ajaxResponse = checkAgent.check(data)
		logging.info("Data received : "+checkAgent.toString(data))

		#Create a user if there is no error
		if not ajaxResponse['error']:			
			user = User.register(data)
			user.put()
			self.jumpIn(user)

		#Send back the computed data
		self.response.out.write(json.dumps(ajaxResponse))



# Login of a registered user
class LogIn(MainHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		data = json.loads(self.request.body)

		#Check log in informations via a dedicated agent
		checkAgent = CheckLogIn()
		ajaxResponse = checkAgent.check(data)
		logging.info("Data received : "+checkAgent.toString(data))


		if not ajaxResponse['error_login']:
			user = User.logIn( data['nickname'], data['password'], data['is_email'])

			if not user:
				ajaxResponse['error_login_msg'] = "The given informations don't match any user"
				ajaxResponse['error_login'] = True

			else:
				self.jumpIn(user)

		self.response.out.write(json.dumps(ajaxResponse))


# Disconnect logged in user
class LogOut(MainHandler):

	def get(self):
		self.doExit()




############################
### 	TRAVELS HANDLER  ###
############################

# Add a new travel as a driver
class AddTravel(MainHandler):
	####################################################
	# Render the html template bind to choice == "add" #
	####################################################

	def get(self):	
		self.render('base.html', user = self.user, choice="add", datetime_departure = datetime.datetime.now())

	def post(self):
		# Save data into a dictionnary
		data = {}
		data['departure'] = self.request.get('departure')
		data['arrival'] = self.request.get('arrival')
		data['departure_date'] = self.request.get('departure-date')
		data['departure_hour'] = self.request.get('departure-hour')
		data['departure_minutes'] = self.request.get('departure-minutes')
		data['price'] = self.request.get('price')
		data['animals'] = self.request.get('animals')
		data['smoking'] = self.request.get('smoking')
		data['luggage'] = self.request.get('luggage')

		self.seats = self.request.get('seats')

		# Check data via a dedicated agent
		travelerAgent = CheckTravel(data)
		checkedResult = travelerAgent.check()

		if checkedResult['error']:
			self.render('base.html', 
				user = self.user,
				choice = "add",
				travel_ok = False,
				**checkedResult)

		else:
			# Register the new travel into DB
			travel_data = {
				'user_id'			: self.user.key().id(),
				'departure'			: data['departure'],
				'arrival'			: data['arrival'],
				'places_number'		: int(self.seats),
				'places_remaining'	: int(self.seats),
				'datetime_departure': checkedResult['datetime_departure'],
				'price'				: int(data['price']),
				'animal'			: checkedResult['animal_ok'],
				'smoking'			: checkedResult['smoking_ok'],
				'luggage'			: checkedResult['big_luggage_ok']
			}
			travel = Travel.add_travel(travel_data)	

			self.render('base.html', 
							user = self.user, 
							choice = "add",
							travel_ok = True, 
							datetime_departure = datetime.datetime.now())


# Modify an owned travel
class ModifyTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "modify" #
	#######################################################

	def get(self):
		self.travel_id = int(self.request.get('id'))
		travel = Travel.by_id(self.travel_id)
		self.render('base.html', user = self.user, choice = "modify", travel = travel)

	def post(self):
		self.travel_id = int(self.request.get('travel_id'))

		# Save data into a dictionnary
		data = {}
		data['departure'] = self.request.get('departure')
		data['arrival'] = self.request.get('arrival')
		data['departure_date'] = self.request.get('departure-date')
		data['departure_hour'] = self.request.get('departure-hour')
		data['departure_minutes'] = self.request.get('departure-minutes')
		data['price'] = self.request.get('price')
		data['animals'] = self.request.get('animals')
		data['smoking'] = self.request.get('smoking')
		data['luggage'] = self.request.get('luggage')

		self.seats = self.request.get('seats')

		# Tests to change a travel are same to a new Travel
		# So the agent is the same as the one used in AddTravel
		travelerAgent = CheckTravel(data)
		checkedResult = travelerAgent.check()

		if checkedResult['error']:
			self.render('base.html', 
				user = self.user,
				choice = "modify",
				travel = Travel.by_id(self.travel_id),
				travel_ok = False,
				**checkedResult)

		else:
			# Bring changes to the targeted travel
			travel_data = {
				'user_id'			: self.user.key().id(),
				'departure'			: data['departure'],
				'arrival'			: data['arrival'],
				'places_number'		: int(self.seats),
				'places_remaining'	: int(self.seats),
				'datetime_departure': checkedResult['datetime_departure'],
				'price'				: int(data['price']),
				'animal'			: checkedResult['animal_ok'],
				'smoking'			: checkedResult['smoking_ok'],
				'luggage'			: checkedResult['big_luggage_ok']
			}
			travel = Travel.modify_travel(self.travel_id, travel_data)
			self.render('base.html', user = self.user, choice = 'modify', travel = Travel.by_id(self.travel_id), travel_ok = True)


# Look for a travel
class SearchTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "search" #
	#######################################################


	def get(self):
		today = datetime.datetime.now().strftime("%Y-%m-%d")
		success_booking = self.request.get('success_booking')
		self.render('base.html', user = self.user, choice = "search", today = today, success_booking = success_booking)

	def post(self):
		# Save data into dictionnary
		data = {}
		data['departure'] = self.request.get('departure')
		data['arrival'] = self.request.get('arrival')
		data['departure_date'] = self.request.get('departure-date')
		data['departure_hour'] = self.request.get('departure-hour')
		data['departure_minutes'] = self.request.get('departure-minutes')
		data['animals'] = self.request.get('animals')
		data['smoking'] = self.request.get('smoking')
		data['luggage'] = self.request.get('luggage')

		# Check data via a dediacted agent
		searchAgent = CheckSearchTravel(data)
		checkedResult = searchAgent.check()


		if checkedResult['error']:
			today = datetime.datetime.now().strftime("%Y-%m-%d")
			self.render('base.html',
				user = self.user,
				choice = "search",
				error = checkedResult['error'],
				error_samedeparture = checkedResult['error_samedeparture'],
				today = today)

		else:
			# Get back travels that match the filter
			travels = Travel.by_filter(data['departure'], 
										data['arrival'], 
										checkedResult['date_min'], 
										checkedResult['animal_ok'], 
										checkedResult['smoking_ok'],
										checkedResult['big_luggage_ok'])
			self.render('base.html', 
						user = self.user,
						choice = "resultSearch", 
						travels = travels)


# Delete a previously created travel
class DeleteTravel(MainHandler):

	def get(self):
		self.travel_id = int(self.request.get('id'))
		Travel.remove_travel(self.travel_id, self.user.key().id())
		self.redirect('/')


# Register for a travel as a traveller
class AddUserToTravel(MainHandler):
	#######################################################
	# Render the html template bind to choice == "search" #
	# Implicit rendering 
	# --> cf redirect on SearchTravel class
	#######################################################

	def post(self):
		self.user_id = self.user.key().id()
		self.travel_id = int(self.request.get('travel_id'))
		self.places_reservation = int(self.request.get('places_reservation'))		

		added = Travel.add_user(self.user_id, self.travel_id, self.places_reservation)

		if added:
			self.redirect('/?success_booking=True')
		else:
			self.redirect('/searchTravel?success_booking=False')


# Show my travels as a driver
class ShowDriverTravels(MainHandler):
	##############################################################
	# Render the html template bind to choice == "driverTravels" #
	##############################################################

	def get(self):
		travels = Travel.by_author(self.user.key().id())
		self.render('base.html', user = self.user, choice = "driverTravels", travels = travels)


# Show my travels as a traveller
class ShowTravelerTravels(MainHandler):
	################################################################
	# Render the html template bind to choice == "travelerTravels" #
	################################################################

	def get(self):
		travels = Travel.by_passenger(self.user.key().id())
		travel_id_email = []

		# Getting email adress of drivers to be able to send a message
		for travel in travels:
			driver_mail = User.by_id(travel.user_id).email
			couple_travel_mail = (travel.key().id(), driver_mail)
			travel_id_email.append(couple_travel_mail)

		self.render('base.html', user = self.user, choice = 'travelerTravels', travels = travels, couples_id_mail = travel_id_email)




############################
###  USER-PAGE HANDLER   ###
############################

class MyProfile(MainHandler):

	def get(self):
		if not self.user:
			self.redirect('/')
		else:
			self.render('base.html', user=self.user, choice="userPage")

	# Handle user modification
	def post(self):
		data = json.loads(self.request.body)

		
		response = {}
		response['error'] = False

		if data['attr'] == 'name':
			self.user.name = data['value']
			self.user.put()

		elif data['attr'] == 'firstName':
			self.user.firstName = data['value']
			self.user.put()		

		elif data['attr'] == 'email':
			alreadyUsed = User.by_email(data['value'])
			if alreadyUsed:
				response['error'] = True
				response['error_msg'] = "Email address already used"

			else:
				self.user.email = data['value']
				self.user.put()

		elif data['attr'] == "changePWD":
			# check if old password provide the log in functionnality
			logTest = User.logIn(self.user.nickName, data['oldPass'], False)
			
			if logTest:

				if data['newPass'] != '':						
					# Change password
					hashedPWD = self.user.changePWD(self.user, data['newPass'])
					self.user.password = hashedPWD
					self.user.put()
				else:
					response['error'] = True
					response['error_msg'] = 'You must enter a new password'	

			else:
				response['error'] = True
				response['error_msg'] = 'The old password is not good'

		elif data['attr'] == "pref":
			self.user.animals = data['animals']
			self.user.smoking = data['smoking']
			self.user.big_luggage = data['luggage']
			self.user.put()

		
		self.response.out.write(json.dumps(response))	







# URL handler dispatcher
app = webapp2.WSGIApplication([('/', MainHandler),
								('/signUp', SignUp),
								('/logIn', LogIn),
								('/logOut', LogOut),
								('/addTravel', AddTravel),
								('/driverTravels', ShowDriverTravels),
								('/deleteTravel', DeleteTravel),
								('/modifyTravel', ModifyTravel),
								('/searchTravel', SearchTravel),
								('/addUserToTravel', AddUserToTravel),
								('/travelerTravels', ShowTravelerTravels),
								('/myProfile', MyProfile)],
								debug=True)
