#####################################################################
# This module ensure data received from the client are correct for :
# 	* a new user to sign up --> CheckSignUp
# 	* a user to log in 		--> CheckLogIn
# 	* Both classes have method toString to display input data
#####################################################################


from src.user import User


# Check if the SignUpForm.html is correctly completed
class CheckSignUp():

	# Check data fill in the form andsend back a dictionnary
	def check(self, data):
		ajaxResponse = {}
		error = False

		#Check for empty fields and bind specific error message
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


		#Prepare the response to the ajax request
		ajaxResponse['error'] = error
		return ajaxResponse


	def toString(self, data):
		s = ''
		for key in data:
			s = s+"%s : %r \n" %(key, data[key])
		return s


# Check if the logInForm.html is correctly completed
class CheckLogIn():

	# Check data fill in the form andsend back a dictionnary
	def check(self, data):
		ajaxResponse = {}
		error = False

		#Ensure user has enter a nickname or email address
		if not data['nickname']:
			ajaxResponse['error_login_msg'] =  "You must enter a nickname or an e-mail address"
			error = True			

		#Ensure user has enter a password
		elif not data['password']:
			ajaxResponse['error_login_msg'] = "You must enter your password"
			error = True			

		ajaxResponse['error_login'] = error
		return ajaxResponse
		

	def toString(self, data):
		s = ''
		for key in data:
			s = s+"%s : %r \n" %(key, data[key])
		return s