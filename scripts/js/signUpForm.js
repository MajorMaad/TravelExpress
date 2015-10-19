

//validate email address via regex
function validateEmail(email) {
	var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
	return re.test(email);
}


//Check for empty or non correct user inputs
//return false if not correct
function ensureNonEmpty(){
	var correct = true;
	var inputs = $("#signUpForm").find("input");

	//Iterate over inputs to check if inputs are correct
	//
	for (i=0; i<inputs.length; i++){

		//Optimization : skip password cases
		//Skip submit button
		if($(inputs[i]).attr('id') != "passInput" || $(inputs[i]).attr('id') != "passValidate"){

			var wellFormed = true;

			//Basic cases : name / firstname / nickname
			if($(inputs[i]).val() == ""){
				if ($(inputs[i]).attr('id') == "name"){
					$(inputs[i]).attr('value', "Enter your name");
				}

				if ($(inputs[i]).attr('id') == "firstName"){
					$(inputs[i]).attr('value', "Enter your firstname");
				}

				if ($(inputs[i]).attr('id') == "nickName"){
					$(inputs[i]).attr('value', "Enter your nickname");
				}									
				wellFormed = false;								
			}

			//email case : the placeholder attribute configures the defautl text
			if ($(inputs[i]).attr('id') == "email" && !validateEmail($(inputs[i]).val()) ){
				wellFormed = false;
			}

			//Color the wrong input and Activate the on click behaviour
			if(!wellFormed){
				console.log("entry is not wellformed");
				$(inputs[i]).css("background-color", "red");
				$(inputs[i]).click(function(e){
					$(this).css("background-color", "transparent");
					$(this).val('');
					
				});
			}

			//Ensure that the boolean is well instanciated
			if(!wellFormed && correct){
				correct = false;
			}
		}
	}
	//end of loop

	//Compare both passwords 
	if ($("#passInput").val() != $("#passValidate").val()){
		//Hilight and reset of passwords
		$("#passInput").css("background-color", "red"); 
		$("#passValidate").css("background-color", "red");
		
		$("#passInput").click(function(e){
			$(this).css("background-color", "transparent");
			$(this).val('');									
		});

		$("#passValidate").click(function(e){
			$(this).css("background-color", "transparent");
			$(this).val('');									
		});

		correct = false;
	}

	return correct;
}