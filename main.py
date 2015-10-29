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
		success_booking = self.request.get('success_booking')
		if self.user:
			self.render('base.html', user=self.user, success_booking = success_booking, **params)
		else:
			self.render('base.html', **params)

	def post(self):
		self.response.out.write("main post ")

	def render(self, template, **params):
		self.response.out.write(render_str(template, **params))


	#Set a cookie for the user who just jumped in (via SignUp or LogIn)
	#Redirection is done via ajax method
	def jumpIn(self, user):
		self.set_secure_cookie('user_id', db_id=str(user.key().id()))


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

		data = json.loads(self.request.body)
		logging.info("""Data received from JSON : \n 
						name : %s 	\n
						firstname : %s \n
						nickName : %s \n
						email : %s \n
						is_email : %r \n
						password : %s \n
						passvalidate : %s \n
						"""
						%(	data['name'],
							data['firstName'],
							data['nickName'],
							data['email'],
							data['is_email'],
							data['password'],
							data['passValidate'])
					)


		ajaxResponse = {}
		error = False

		#Check for empty fields and respond with the correct message
		if not data['nickName']:
			ajaxResponse['error_notif_nick'] = True
			ajaxResponse['error_nick_msg'] = "You must enter a nickname"
			error = True

		if not data['email'] or not data['is_email']:
			ajaxResponse['error_notif_mail'] = True
			ajaxResponse['error_mail_msg'] = "You must enter a valid e-mail address"
			error = True

		if not data['password']:
			ajaxResponse['error_notif_pass'] = True
			ajaxResponse['error_pass_msg'] = "You must enter a password"
			error = True

		if not data['passValidate']:
			ajaxResponse['error_notif_pass_confirm'] = True
			ajaxResponse['error_pass_confirm_msg'] = "You must validate your password"
			error = True

		elif data['passValidate'] != data['password']:
			ajaxResponse['error_notif_pass_confirm'] = True
			ajaxResponse['error_pass_confirm_msg'] = "Passwords are not the same"
			error = True

		# All fields required are non empty
		else:

			#Check for an already existant user by nickname
			if User.by_name(data['nickName']):
				ajaxResponse['error_notif_nick'] = True
				ajaxResponse['error_nick_msg'] = "This nickname is already used."
				error = True

			#Check for an already existant user by mail
			if User.by_email(data['email']):
				ajaxResponse['error_notif_mail'] = True
				ajaxResponse['error_mail_msg'] = "This email address is already used."
				error = True


			#Create a user if there is no error
			if not error :
				user = User.register(data)
				user.put()
				self.jumpIn(user)

		#Prepare the response to the ajax request
		ajaxResponse['error'] = error

		#Send back the computed data
		self.response.out.write(json.dumps(ajaxResponse))

class LogIn(MainHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		data = json.loads(self.request.body)
		logging.info("Data received from JSON : \n %s 	-	%r 	-	%s" %(data['nickname'], data['is_email'], data['password']))

		self.user_data = data['nickname']
		self.password = data['password']
		self.is_email = data['is_email']

		
		#Ensure user has enter a nickname or email address
		if not self.user_data:
			error_msg =  "You must enter a nickname or an e-mail address"
			self.response.out.write(json.dumps(({'error_login': True, 'error_login_msg': error_msg})))

		#Ensure user has enter a password
		elif not self.password:
			error_msg =  "You must enter your password"
			self.response.out.write(json.dumps(({'error_login': True, 'error_login_msg': error_msg})))
		

		else:
			logging.info("Data correctly typed in")

			#Request a user according to these informations
			user = User.logIn(self.user_data, self.password, self.is_email)

			if user:
				logging.info("User found in DB")
				#Log user and send back data to Ajax to redirect properly
				self.jumpIn(user)
				self.response.out.write(json.dumps(({'error_login': False})))

			else:
				#Render same page for user correction
				error_msg =  "The given informations don't match any user"
				self.response.out.write(json.dumps(({'error_login': True, 'error_login_msg': error_msg})))


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
		Travel.remove_travel(self.travel_id, self.user.key().id())
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
		success_booking = self.request.get('success_booking')

		self.render('searchTravel.html', user = self.user, today = today, success_booking = success_booking)

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
			self.redirect('/?success_booking=True')
		else:
			self.redirect('/searchTravel?success_booking=False')



class ShowTravelerTravels(MainHandler):

	def get(self):
		travels = Travel.by_passenger(self.user.key().id())
		travel_id_email = []

		# Getting email adress of drivers to be able to send a message
		for travel in travels:
			driver_mail = User.by_id(travel.user_id).email
			couple_travel_mail = (travel.key().id(), driver_mail)
			travel_id_email.append(couple_travel_mail)

		self.render('travelerTravels.html', user = self.user, travels = travels, couples_id_mail = travel_id_email)







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
								('/travelerTravels', ShowTravelerTravels)],
								debug=True)
