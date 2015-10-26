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


# Template Jinja2 stuff :
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

# Main rendering function
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)


#Import des sources
from src.user import *
from src.travel import *


secret = 'thisIsReallyABigSecret'

class MainHandler(webapp2.RequestHandler):

	#Overwrite the initialize method of webapp2
	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		#Look for a cookie session and initialise the user boolean if found
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))


	#Function called when a user sign up or logged in
	#Associate a cookie encrypted
	def set_secure_cookie(self, name, db_id):
		cookie_val = self.make_secure_val(db_id)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

	#Encryption of a cookie : The seed is the database ID of the user
	def make_secure_val(self, db_id):
		return '%s|%s' % (db_id, hmac.new(secret, db_id).hexdigest())

	#Uncryption of a secure cookie
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



	def get(self, **params):
		if self.user:
			self.render('base.html', user=self.user, **params)
		else:
			self.render('base.html', **params)

	def post(self):
		self.response.out.write("main post ")

	def render(self, template, **params):
		self.response.out.write(render_str(template, **params))


	#Set a cookie for the user who just jumped in (via SignUp or LogIn)
	#Then redirect to '/' to handle the new rendering, according to the cookie session
	def jumpIn(self, user):
		self.set_secure_cookie('user_id', db_id=str(user.key().id()))
		self.redirect('/')


	#Log out th euser via a reset of the cookie
	def doExit(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
		self.redirect('/')




#This class handle the registration of a new user
#Inheritance of MainHandler to get the webapp2 module and the render function and overwrites post method
class SignUp(MainHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		self.name = self.request.get('name')
		self.firstName = self.request.get('firstName')
		self.nickName = self.request.get('nickName')
		self.email = self.request.get('email')
		self.passBasic = self.request.get('passBasic')
		self.passValidate = self.request.get('passValidate')

		#Look into database if nickName or email is already in use
		error = False
		error_nickname = ''
		error_email = ''

		if User.by_name(self.nickName):
			error_nickname = "Sorry, this nickname is already used."
			error = True

		if User.by_email(self.email):
			error_email = "Sorry, this email address is already used."
			error = True

		#Render same page for user correction
		if error:
			self.render('base.html',error_signup = error,
									name = self.name,
									firstName = self.firstName,
									nickName = self.nickName,
									email = self.email,
									passBasic = self.passBasic,
									passValidate = self.passValidate,
									error_nick = error_nickname,
									error_email = error_email)

		#Save the new user, log it and rerender the base.html
		else:
			user_data = {'name': self.name, 'firstName': self.firstName, 'nickName': self.nickName, 'email': self.email, 'password': self.passBasic}
			user = User.register(user_data)
			user.put()
			self.jumpIn(user)

class LogIn(MainHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		self.user_data = self.request.get('userLogData')
		self.password = self.request.get('password')
		self.is_email = self.request.get('is_email')

		#Request a user according to these informations
		user = User.logIn(self.user_data, self.password, self.is_email)

		if user:
			#Log user and rerender the base.html
			self.jumpIn(user)

		else:
			#Render same page for user correction
			self.render('base.html', error_login = "The given informations are not correct ...")


class LogOut(MainHandler):

	def get(self):
		self.doExit()


class AddTravel(MainHandler):

	def get(self):
		self.render('addTravel.html', user = self.user, datetime_departure = datetime.datetime.now())

	def post(self):
		error = False
		error_samedeparture = ""
		error_datetime = ""
		error_price = ""

		self.departure = self.request.get('departure')
		self.arrival = self.request.get('arrival')
		self.departure_date = self.request.get('departure-date')
		self.departure_hour = self.request.get('departure-hour')
		self.departure_minutes = self.request.get('departure-minutes')
		self.seats = self.request.get('seats')
		self.price = self.request.get('price')
		self.animals = self.request.get('animals')
		self.smoking = self.request.get('smoking')
		self.luggage = self.request.get('luggage')

		if self.departure == self.arrival:
			error_samedeparture = "cannot be the same as departure"
			error = True

		date_tab = self.departure_date.split('-')
		try:
			year = int(date_tab[0])
			month = int(date_tab[1])
			day = int(date_tab[2])
		except ValueError:
			year = 2000
			month = 1
			day = 1

		hour = int(self.departure_hour)
		minutes = int(self.departure_minutes)

		departure_datetime = datetime.datetime(year, month, day, hour, minutes)
		now = datetime.datetime.now()

		if departure_datetime <= now:
			error_datetime = "Wrong Date / Time"
			error = True

		try:
			self.price = int(self.price)
		except ValueError:
			error_price = "Wrong price value"
			error = True

		if self.price <= 0 or self.price > 10000:
			error_price = "Wrong price value"
			error = True

		if self.animals == 'ok':
			animal_ok = True
		else:
			animal_ok = False

		if self.smoking == 'ok':
			smoking_ok = True
		else:
			smoking_ok = False

		if self.luggage == 'suitcase':
			big_luggage_ok = True
		else:
			big_luggage_ok = False

		if error:
			self.render('addTravel.html',
				user = self.user,
				travel_ok = False,
				error = error,
				error_samedeparture = error_samedeparture,
				error_datetime = error_datetime,
				error_price = error_price,
				departure = self.departure,
				arrival = self.arrival,
				datetime_departure = departure_datetime,
				seats = self.seats,
				price = self.price,
				animal_ok = animal_ok,
				smoking_ok = smoking_ok,
				big_luggage_ok = big_luggage_ok)

		else:
			travel_data = {
				'user_id': self.user.key().id(),
				'departure': self.departure,
				'arrival': self.arrival,
				'places_number': int(self.seats),
				'places_remaining': int(self.seats),
				'datetime_departure': departure_datetime,
				'price': self.price,
				'animal': animal_ok,
				'smoking': smoking_ok,
				'luggage': big_luggage_ok
			}

			travel = Travel.add_travel(travel_data)
			self.render('addTravel.html', user = self.user, travel_ok = True, datetime_departure = datetime.datetime.now())



class ShowDriverTravels(MainHandler):

	def get(self):
		travels = Travel.by_author(self.user.key().id())
		self.render('driverTravels.html', user = self.user, travels = travels)


class DeleteTravel(MainHandler):

	def get(self):
		self.travel_id = int(self.request.get('id'))
		Travel.remove_travel(self.travel_id)
		self.redirect('/')


class ModifyTravel(MainHandler):

	def get(self):
		self.travel_id = int(self.request.get('id'))
		travel = Travel.by_id(self.travel_id)
		self.render('modifyTravel.html', user = self.user, travel = travel)

	def post(self):
		error = False
		error_samedeparture = ""
		error_datetime = ""
		error_price = ""

		self.travel_id = int(self.request.get('travel_id'))
		self.departure = self.request.get('departure')
		self.arrival = self.request.get('arrival')
		self.departure_date = self.request.get('departure-date')
		self.departure_hour = self.request.get('departure-hour')
		self.departure_minutes = self.request.get('departure-minutes')
		self.seats = self.request.get('seats')
		self.price = self.request.get('price')
		self.animals = self.request.get('animals')
		self.smoking = self.request.get('smoking')
		self.luggage = self.request.get('luggage')

		if self.departure == self.arrival:
			error_samedeparture = "cannot be the same as departure"
			error = True

		date_tab = self.departure_date.split('-')
		try:
			year = int(date_tab[0])
			month = int(date_tab[1])
			day = int(date_tab[2])
		except ValueError:
			year = 2000
			month = 1
			day = 1

		hour = int(self.departure_hour)
		minutes = int(self.departure_minutes)

		departure_datetime = datetime.datetime(year, month, day, hour, minutes)
		now = datetime.datetime.now()

		if departure_datetime <= now:
			error_datetime = "Wrong Date / Time"
			error = True

		try:
			self.price = int(self.price)
		except ValueError:
			error_price = "Wrong price value"
			error = True

		if self.price <= 0 or self.price > 10000:
			error_price = "Wrong price value"
			error = True

		if self.animals == 'ok':
			animal_ok = True
		else:
			animal_ok = False

		if self.smoking == 'ok':
			smoking_ok = True
		else:
			smoking_ok = False

		if self.luggage == 'suitcase':
			big_luggage_ok = True
		else:
			big_luggage_ok = False

		if error:
			self.render('modifyTravel.html',
				user = self.user,
				travel_ok = False,
				error = error,
				error_samedeparture = error_samedeparture,
				error_datetime = error_datetime,
				error_price = error_price)

		else:
			travel_data = {
				'user_id': self.user.key().id(),
				'departure': self.departure,
				'arrival': self.arrival,
				'places_number': int(self.seats),
				'places_remaining': int(self.seats),
				'datetime_departure': departure_datetime,
				'price': self.price,
				'animal': animal_ok,
				'smoking': smoking_ok,
				'luggage': big_luggage_ok
			}

			travel = Travel.modify_travel(self.travel_id, travel_data)
			self.render('modifyTravel.html', user = self.user, travel = Travel.by_id(self.travel_id), travel_ok = True)



class SearchTravel(MainHandler):

	def get(self):
		today = datetime.datetime.now().strftime("%Y-%m-%d")
		self.render('searchTravel.html', user = self.user, today = today)

	def post(self):
		error = False
		error_samedeparture = ""

		self.departure = self.request.get('departure')
		self.arrival = self.request.get('arrival')
		self.departure_date = self.request.get('departure-date')
		self.departure_hour = self.request.get('departure-hour')
		self.departure_minutes = self.request.get('departure-minutes')
		self.animals = self.request.get('animals')
		self.smoking = self.request.get('smoking')
		self.luggage = self.request.get('luggage')

		if self.departure == self.arrival:
			error_samedeparture = "cannot be the same as departure"
			error = True

		departure = self.departure
		arrival = self.arrival

		date_tab = self.departure_date.split('-')
		try:
			year = int(date_tab[0])
			month = int(date_tab[1])
			day = int(date_tab[2])
		except ValueError:
			year = 2000
			month = 1
			day = 1

		hour = int(self.departure_hour)
		minutes = int(self.departure_minutes)

		date_min = datetime.datetime(year, month, day, hour, minutes)

		if self.animals == 'ok':
			animal_ok = True
		elif self.animals == 'ni':
			animal_ok = None
		else:
			animal_ok = False

		if self.smoking == 'ok':
			smoking_ok = True
		elif self.smoking == 'ni':
			smoking_ok = None
		else:
			smoking_ok = False

		if self.luggage == 'suitcase':
			big_luggage_ok = True
		elif self.luggage == 'ni':
			big_luggage_ok = None
		else:
			big_luggage_ok = False

		if error:
			today = datetime.datetime.now().strftime("%Y-%m-%d")
			self.render('searchTravel.html',
				user = self.user,
				error = error,
				error_samedeparture = error_samedeparture,
				today = today)

		else:
			travels = Travel.by_filter(departure, arrival, date_min, animal_ok, smoking_ok, big_luggage_ok)
			self.render('resultSearch.html', user = self.user, travels = travels)


class AddUserToTravel(MainHandler):

	def post(self):
		self.user_id = self.user.key().id()
		self.travel_id = int(self.request.get('travel_id'))
		self.places_reservation = int(self.request.get('places_reservation'))
		added = Travel.add_user(self.user_id, self.travel_id, self.places_reservation)

		if added:
			# TODO : Redirect with a success banner
			self.redirect('/')
		else:
			# TODO : render with an error banner
			self.redirect('/searchTravel')






app = webapp2.WSGIApplication([('/', MainHandler),
								('/signUp', SignUp),
								('/logIn', LogIn),
								('/logOut', LogOut),
								('/addTravel', AddTravel),
								('/driverTravels', ShowDriverTravels),
								('/deleteTravel', DeleteTravel),
								('/modifyTravel', ModifyTravel),
								('/searchTravel', SearchTravel),
								('/addUserToTravel', AddUserToTravel)],
								debug=True)
