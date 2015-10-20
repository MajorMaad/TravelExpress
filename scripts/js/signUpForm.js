

//validate email address via regex
function validateEmail(email) {
	var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
	return re.test(email);
}


//Check for empty or non correct user inputs
//return false if not correct
function ensureSignUpNonEmpty(){
	var correct = true;
	var inputs = $("#signUpForm").find("input");

	//Iterate over inputs to check if inputs are correct
	//
	for (i=0; i<inputs.length; i++){

		var wellFormed = true;

		//check if inputs empty
		if($(inputs[i]).val() == ""){

			//Name case
			if ($(inputs[i]).attr('id') == "name"){
				$(document.getElementById('nameEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('nameEmpty')).hide();				
				});
			}

			//First name case
			if ($(inputs[i]).attr('id') == "firstName"){
				$(document.getElementById('firstNameEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('firstNameEmpty')).hide();				
				});
			}

			//Nick name case
			if ($(inputs[i]).attr('id') == "nickName"){
				$(document.getElementById('nickNameEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('nickNameEmpty')).hide();				
				});
			}

			//email case
			if ($(inputs[i]).attr('id') == "email"){
				$(document.getElementById('mailEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('mailEmpty')).hide();				
				});
			}

			//Pass 1 case
			if ($(inputs[i]).attr('id') == "passInput"){
				$(document.getElementById('emptyPass1')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('emptyPass1')).hide();				
				});
			}

			//Pass 2 case
			if ($(inputs[i]).attr('id') == "passValidate"){
				$(document.getElementById('emptyPass2')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('emptyPass2')).hide();				
				});
			}

			wellFormed = false;								
		}

		//email case : check validity
		if ($(inputs[i]).attr('id') == "email" && !validateEmail($(inputs[i]).val()) ){
			$(document.getElementById('mailEmpty')).val('Email not correct')
			$(document.getElementById('mailEmpty')).show();
				$(inputs[i]).click(function(e){
					$(document.getElementById('mailEmpty')).hide();				
				});
			wellFormed = false;
		}

		//Reset content when click if input was not correct
		if(!wellFormed){
			console.log("entry is not wellformed");
			$(inputs[i]).click(function(e){
				$(this).val('');					
			});
		}

		//Ensure that the boolean is well instanciated
		if(!wellFormed && correct){
			correct = false;
		}		
	}
	//end of loop

	//Compare both passwords 
	if ($("#passInput").val() != $("#passValidate").val()){		
		//Highlight password validation
		$(document.getElementById('emptyPass2')).val('password is not the same')
		$(document.getElementById('emptyPass2')).show();
		$("#passValidate").click(function(e){
			$(document.getElementById('emptyPass2')).hide();				
		});
		correct = false;
	}

	return correct;
}