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
import json



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



