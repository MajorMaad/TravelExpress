//validate email address via regex
function validateEmail(email) {
	var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
	return re.test(email);
}


//Check for empty or non correct user inputs
//return false if not correct
function ensureLogInNonEmpty(){
	var correct = true;
	var inputs = $("#logInForm").find("input");

	//Iterate over inputs to check if inputs are correct
	//
	for (i=0; i<inputs.length; i++){

		var wellFormed = true;

		//Check if the 2 inputs are non empty
		//If one is empty, display information message
		//If displayed message is shown, hide it when the input get focus by user
		if($(inputs[i]).val() == ""){

			if ($(inputs[i]).attr('id') == "userLogData"){
				$(document.getElementById('userLogDataEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('userLogDataEmpty')).hide();				
				});

			}

			if ($(inputs[i]).attr('id') == "password"){
				$(document.getElementById('passwordEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('passwordEmpty')).hide();				
				});
			}							
			wellFormed = false;								
		}

		//Ensure that the boolean is well instanciated
		if(!wellFormed && correct){
			correct = false;
		}
	}

	return correct;
}


// function called when the form is submit
//Check if inputs are non empty
//Evaluate if the user data is an email address, to anticipate server database request
function submitLogInForm(){
	if (ensureLogInNonEmpty()){
		var userLogData = $(document.getElementById('userLogData')).val();
		is_email = validateEmail(userLogData)
		if (is_email){
			$('<input type="hidden" id="is_email" name="is_email" value="True">').insertAfter($("#deployLogInForm"));			
		}

		console.log("data given : "+$(document.getElementById('userLogData')).val());
		return true;
	}
	return false;
}