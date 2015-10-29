from src.user import User

class CheckSignUp():


	def check(self, data):
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


		#Prepare the response to the ajax request
		ajaxResponse['error'] = error
		return ajaxResponse


	def toString(self, data):
		s = ''
		for key in data:
			s = s+"%s : %r \n" %(key, data[key])

		return s 
