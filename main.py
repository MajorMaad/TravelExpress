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
from src.registration import *
from src.travelChecker import *


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


class LogOut(MainHandler):

	def get(self):
		self.doExit()


class AddTravel(MainHandler):

	def get(self):		
		self.render('base.html', user = self.user, choice="add", datetime_departure = datetime.datetime.now())

	def post(self):

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

		travelerAgent = CheckAddTravel(data)
		checkedResult = travelerAgent.check()

		if checkedResult['error']:
			self.render('base.html', 
				user = self.user,
				choice = "add",
				travel_ok = False,
				**checkedResult)

		else:
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

		# self.render('searchTravel.html', user = self.user, today = today, success_booking = success_booking)
		self.render('base.html', 
					user = self.user,
					choice = "search",
					today = today,
					success_booking = success_booking)

	def post(self):

		data = {}
		data['departure'] = self.request.get('departure')
		data['arrival'] = self.request.get('arrival')
		data['departure_date'] = self.request.get('departure-date')
		data['departure_hour'] = self.request.get('departure-hour')
		data['departure_minutes'] = self.request.get('departure-minutes')
		data['animals'] = self.request.get('animals')
		data['smoking'] = self.request.get('smoking')
		data['luggage'] = self.request.get('luggage')


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
			travels = Travel.by_filter(data['departure'], 
										data['arrival'], 
										checkedResult['date_min'], 
										checkedResult['animal_ok'], 
										checkedResult['smoking_ok'],
										checkedResult['big_luggage_ok'])
			self.render('resultSearch.html', user = self.user, choice = "search", travels = travels)


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
