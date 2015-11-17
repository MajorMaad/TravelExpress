#########################################################################
# This module provides url handler dedicated to user
# Ensure : 
# 	* SignUp	
# 	* Login
# 	* LogOut
# 	* Profile modification
#########################################################################

from src.handler import *
from src.user import *
from src.registration import *


from src.traveler import Traveler
from src.driver import Driver
from src.travel import Travel

import json



############################
### REGISTRATION HANDLER ###
############################

# Registration of a new user
class SignUp(MainHandler):

	def get(self):
		self.redirect('/')

	# Powered by Ajax
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

		# Ajax response
		self.response.out.write(json.dumps(ajaxResponse))



# Login of a registered user
class LogIn(MainHandler):

	def get(self):
		self.redirect('/')

	# Powered by Ajax
	def post(self):
		data = json.loads(self.request.body)

		#Check log in informations via a dedicated agent
		checkAgent = CheckLogIn()
		ajaxResponse = checkAgent.check(data)
		logging.info("Data received : "+checkAgent.toString(data))


		if not ajaxResponse['error_login']:
			user = User.logIn( data['nickname'], data['password'], data['is_email'])


			# If user exists : log him
			if not user:
				ajaxResponse['error_login_msg'] = "The given informations don't match any user"
				ajaxResponse['error_login'] = True

			else:
				self.jumpIn(user)

		# Ajax response
		self.response.out.write(json.dumps(ajaxResponse))


# Disconnect logged in user
class LogOut(MainHandler):

	def get(self):
		# MainHandler doExit method : destroy cookie and redirect to '/'
		self.doExit()





############################
###  USER-PAGE HANDLER   ###
############################

class MyProfile(MainHandler):

	def get(self):
		# Check if user is logged before rendering his profile page
		if not self.user:
			self.redirect('/')
		else:
			url = self.request.url
			nickname = url.split('/')[-1]
			logging.info("--> "+nickname)

			if self.user.nickName == nickname:
				member = self.user
			else:
				member = User.by_nickName(nickname)
				
			stats = self.getStats(member)
			self.render('base.html', user=self.user, choice="userPage", member=member, stats=stats)

	# Powered by Ajax
	def post(self):
		data = json.loads(self.request.body)

		response = {}
		response['error'] = False

		# Check all key of the loaded JSON with attribute of a User : 
		# If there is a modification and the modification is correct : apply changes to database

		if data['attr'] == 'name':
			self.user.name = data['value']
			self.user.put()

		elif data['attr'] == 'firstName':
			self.user.firstName = data['value']
			self.user.put()		

		elif data['attr'] == 'email':
			# ensure email wanted is not already in use
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
					# Generate new hashed password
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

		# Ajax response
		self.response.out.write(json.dumps(response))


	def getStats(self, member):
		# According to the user id, get the number of travel booked and the number of travel as a driver
		traveler = Traveler.get_traveler(member.key())
		if traveler :
			nb_booking = Travel.by_traveler(traveler).count()
			
		
		driver = Driver.get_driver(member.key())
		if driver :
			nb_lifts = Travel.by_driver(driver).count()


		return {'nb_booking':nb_booking, 'nb_lifts':nb_lifts}