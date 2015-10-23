//validate email address via regex
function validateEmail(email) {
	var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
	return re.test(email);
}


//Check for empty or non correct user inputs
//return false if not correct
function ensureForgotNonEmpty(){

	if ($("#userForgotPWD").val() == ""){
		$(document.getElementById('userForgotPWDEmpty')).show();
		$(this).click(function(e){
			$(document.getElementById('userForgotPWDEmpty')).hide();				
		});
		return false;
	}
	return true;

}


// function called when the form is submit
//Check if inputs are non empty
//Evaluate if the user data is an email address, to anticipate server database request
function submitForgottenPWDForm(){
	if (ensureForgotNonEmpty()){
		var retrieve_data = $(document.getElementById('userForgotPWD')).val();
		is_email = validateEmail(retrieve_data)
		if (is_email){
			return true;
		}
	}
	return false;
}