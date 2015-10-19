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



# Template Jinja2 stuff :
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

# Main rendering function
def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)


#Import des sources :
# from src import user

class MainHandler(webapp2.RequestHandler):

	# Simply write the template as a response
	def get(self):
		self.response.out.write(render_str("base.html"))

	def post(self):
		self.response.out.write("main post ")
	# 	# Get attribute given via the post request
	# 	self.name = self.request.get('name')
	# 	self.firstName = self.request.get('firstName')
	# 	self.nickName = self.request.get('nickName')
	#     self.email = self.request.get('email')
	#     self.password = self.request.get('passBasic')
	#     self.passwordValidation = self.request.get('passValidate')

	#     logging.info(self.name)
	#     logging.info(self.firstName)
	#     logging.info(self.nickName)
	#     logging.info(self.email)
	#     logging.info(self.password)
	#     logging.info(self.passwordValidation)

	#     self.response.out.write("lolilol "+self.name)


#this class handle the registration of a new user
class SignUp(webapp2.RequestHandler):

	def post(self):
		self.response.out.write("sign up  post ")


		# Get attribute given via the post request
		self.name = self.request.get('name')
		self.firstName = self.request.get('firstName')
		self.nickName = self.request.get('nickName')
		self.email = self.request.get('email')
		self.password = self.request.get('passBasic')
		self.passwordValidation = self.request.get('passValidate')

		if self.user and self.firstName and self.nickName and self.email and self.password and self.passwordValidation:
			if self.password == self.passwordValidation:
				#Check for database if correct
				self.response.out.write(render_str("base.html"))



	

app = webapp2.WSGIApplication([('/', MainHandler),
								('/signUp', SignUp)],
								debug=True)
