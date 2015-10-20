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


secret = 'terribly secret'

class MainHandler(webapp2.RequestHandler):

	# Simply write the template as a response
	def get(self, **params):
		self.render('base.html', **params)

	def post(self):
		self.response.out.write("main post ")

	def render(self, template, **params):
		self.response.out.write(render_str(template, **params))

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def set_secure_cookie(self, name, val):
		cookie_val = self.make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))
	
	def make_secure_val(self, val):
		return '%s|%s' % (val, hmac.new(secret, val).hexdigest())



#This class handle the registration of a new user
#Inheritance of MainHandler to get the webapp2 module and the render function and overwrites post method
class SignUp(MainHandler):

	def get(self):
		self.render('signUpForm.html')

	def post(self):
		self.response.out.write("sign up  post ")


		# Get attributes given via the post request
		self.name = self.request.get('name')
		self.firstName = self.request.get('firstName')
		self.nickName = self.request.get('nickName')
		self.email = self.request.get('email')
		self.passBasic = self.request.get('passBasic')
		self.passValidate = self.request.get('passValidate')

		params = dict(name = self.name,
					  firstName = self.firstName,
					  nickName = self.nickName,
					  email = self.email,
					  password = self.passBasic)

		#Look into database if nickName or email is already in use
		error = False
		same_nickname = User.by_name(self.nickName)
		same_email = User.by_email(self.email)

		if same_nickname:
			logging.debug("Sorry, this nickname is already used." )
			params['error_nickname'] = "Sorry, this nickname is already used."
			error = True

		if same_email:
			logging.debug("Sorry, this email address is already used." )
			params['error_email'] = "Sorry, this email address is already used."
			error = True

		if error:			
			error_nick = None
			error_email = None

			if 'error_nickname' in params:
				error_nick = params['error_nickname']
			if 'error_email' in params:
				error_email = params['error_email']

			self.render('base.html',error_signup = error, 
									name=params['name'],
									firstName = params['firstName'],
									nickName = params['nickName'],
									email = params['email'],
									passBasic = params['password'],
									passValidate = self.passValidate,
									error_nick=error_nick, 
									error_email=error_email)

		else:
			user = User.register(user_data=params)
			user.put()
			self.login(user)
			self.response.out.write('no error : User created')

class LogIn(MainHandler):

	def post(self):
		self.response.out.write('log in post\n')

		self.user_data = self.request.get('userLogData')
		self.is_email = self.request.get('is_email')
		self.password = self.request.get('password')

		#Request a user according to these informations
		user = User.logIn(self.user_data, self.password, is_email=self.is_email)
		if user:
			self.response.out.write("User correctly retrived from database")
		else:
			self.render('base.html', error_login = "The given informations are not correct")






	

app = webapp2.WSGIApplication([('/', MainHandler),
								('/signUp', SignUp),
								('/logIn', LogIn)],
								debug=True)
