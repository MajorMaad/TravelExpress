/*Perform ajax request to add a travel*/
function submitAddTravel(){

	//Retrieve departure and arrival :
	var departure = document.getElementById("departure").value;
	var arrival = document.getElementById("arrival").value;


	// Retrieve number of seats
	var seats = document.getElementById('seats');
	var seatNumber = seats.options[seats.selectedIndex].value;

	//Retrieve departure moments
	var dep_date = document.getElementById('departure-date').value;
	var dep_hour = document.getElementById('departure-hour').value;
	var dep_min = document.getElementById('departure-minutes').value;

	//Retrieve the price
	var price = document.getElementById("price").value;

	var animals = "ni";
	var smoking = "ni";
	var big_luggage = "ni";
	
	var preferences = document.getElementsByClassName("preferences");	
	for (var i = 0; i < preferences.length; i++){

		if (preferences[i].checked){				
			if (preferences[i].name == 'animals'){			
				animals = preferences[i].value;
			}
			if (preferences[i].name == "smoking"){
				smoking = preferences[i].value;
			}
			if (preferences[i].name == "luggage"){
				big_luggage = preferences[i].value;
			}			
		}
	}
	console.log("animals : "+animals);
	console.log("smoking "+smoking);
	console.log("luggage "+big_luggage);
	

	//Prepare ajax request
	$.ajax({
	  type: "POST",
	  url: "/addTravel",
	  dataType: 'json',
	  data: JSON.stringify({ "departure" : departure,
	  						"arrival" : arrival,
	  						"departure_date" : dep_date,
	  						"departure_hour" : dep_hour,
	  						"departure_minutes" : dep_min,
	  						"price" : price,
	  						"animals" : animals,
	  						"smoking" : smoking,
	  						"luggage" : big_luggage,
	  						"seats" : seatNumber
							})
	})
	.done(function( data ) { 		
		console.log("data received back");

		// Hide error field
		var alert_components = document.getElementsByClassName('error');
		for (var i = 0; i < alert_components.length; i++){
			alert_components[i].style.display = 'none';
		}

		//If there is error, handle appropriate error messages
		if (data['error']){

			//Display main error banner
			var addError = document.getElementById("addError");
			addError.style.display = 'block';

			//error message as a palceholder
			if (data['error_departure']){
				$("#departure").attr('placeholder', data['error_departure']);
			}
			
			//error message as a palceholder
			if (data['error_arrival']){
				$("#arrival").attr('placeholder', data['error_arrival']);
			}

			//Error message append to the error banner
			if (data['error_samedeparture']){
				var error_div = document.getElementById('addError');
				error_div.lastChild.data = data['error_samedeparture'];
			}


			if (data['error_datetime']){
				var span_error = document.getElementById('error_datetime');
				span_error.innerHTML = data['error_datetime'];
				span_error.style.display = 'block';
			}

			if (data['error_price']){
				var span_error = document.getElementById('error_price');
				span_error.innerHTML = data['error_price'];
				span_error.style.display = 'block';
			}
		}else{
			//handle success and redirect to the list of travel whereuser is the driver
			var success = document.getElementById("addSuccess");
			success.style.display = 'block';

			window.setTimeout(function(){
				window.location.replace("driverTravels");
			}, 1500);
		}
	});
}


/*Perform ajax request to modify an existing travel*/
function submitModificationTravel(){

	console.log("getting data");

	//Get trvel id
	var id = document.getElementById("travel_id_modif").value;
	console.log("id given is :"+id);

	//Retrieve departure and arrival :
	var departure = document.getElementById("departure_modify").value;
	var arrival = document.getElementById("arrival_modify").value;
	console.log("dep = "+departure+"	-	arrival : "+arrival);


	// Retrieve number of seats
	var seats = document.getElementById('seats_modify');
	var seatNumber = seats.options[seats.selectedIndex].value;

	//Retrieve departure moments
	var dep_date = document.getElementById('departure-date_modify').value;
	var dep_hour = document.getElementById('departure-hour_modify').value;
	var dep_min = document.getElementById('departure-minutes_modify').value;

	//Retrieve the price
	var price = document.getElementById("price_modify").value;

	var animals = "ni";
	var smoking = "ni";
	var big_luggage = "ni";
	
	var preferences = document.getElementsByClassName("preferences");	
	for (var i = 0; i < preferences.length; i++){

		if (preferences[i].checked){				
			if (preferences[i].name == 'animals'){			
				animals = preferences[i].value;
			}
			if (preferences[i].name == "smoking"){
				smoking = preferences[i].value;
			}
			if (preferences[i].name == "luggage"){
				big_luggage = preferences[i].value;
			}			
		}
	}
	console.log("animals : "+animals);
	console.log("smoking "+smoking);
	console.log("luggage "+big_luggage);
	console.log("preparing request");

	//Prepare ajax request
	$.ajax({
	  type: "POST",
	  url: "/modifyTravel",
	  dataType: 'json',
	  data: JSON.stringify({"travel_id" :id,
	  						"departure" : departure,
	  						"arrival" : arrival,
	  						"departure_date" : dep_date,
	  						"departure_hour" : dep_hour,
	  						"departure_minutes" : dep_min,
	  						"price" : price,
	  						"animals" : animals,
	  						"smoking" : smoking,
	  						"luggage" : big_luggage,
	  						"seats" : seatNumber
							})
	})
	.done(function( data ) { 		
		console.log("data received back");

		// Hide error field
		var alert_components = document.getElementsByClassName('error');
		for (var i = 0; i < alert_components.length; i++){
			alert_components[i].style.display = 'none';
		}

		//If there is error, handle appropriate error messages
		if (data['error']){

			//Display main error banner
			var addError = document.getElementById("addError");
			addError.style.display = 'block';

			//error message as a palceholder
			if (data['error_departure']){
				$("#departure").attr('placeholder', data['error_departure']);
			}
			
			//error message as a palceholder
			if (data['error_arrival']){
				$("#arrival").attr('placeholder', data['error_arrival']);
			}

			//Error message append to the error banner
			if (data['error_samedeparture']){
				var error_div = document.getElementById('addError');
				error_div.lastChild.data = data['error_samedeparture'];
			}


			if (data['error_datetime']){
				var span_error = document.getElementById('error_datetime');
				span_error.innerHTML = data['error_datetime'];
				span_error.style.display = 'block';
			}

			if (data['error_price']){
				var span_error = document.getElementById('error_price');
				span_error.innerHTML = data['error_price'];
				span_error.style.display = 'block';
			}
		}else{
			//handle success and redirect to the list of travel whereuser is the driver
			var success = document.getElementById("addSuccess");
			success.style.display = 'block';

			window.setTimeout(function(){
				window.location.replace("driverTravels");
			}, 1500);
		}
	});
}



/*Perform an ajax request to search a travel according to criteria*/
function searchTravel(){

	console.log("Retrieve search parameter");
	//Get search parameters
	var departure = document.getElementById("departure_search").value;
	var arrival = document.getElementById("arrival_search").value;
	if (departure == ""){
		console.log("departure empty");	
	}
	if (arrival == ""){
		console.log("arrival empty");	
	}
	console.log("dep : "+departure+"	-	arrival : "+arrival);

	var date = document.getElementById("date_search").value;
	var price = document.getElementById("price_search").value;

	var animals = "ni";
	var smoking = "ni";
	var big_luggage = "ni";
	
	var preferences = document.getElementsByClassName("preferences");	
	for (var i = 0; i < preferences.length; i++){

		if (preferences[i].checked){				
			if (preferences[i].name == 'animals'){			
				animals = preferences[i].value;
			}
			if (preferences[i].name == "smoking"){
				smoking = preferences[i].value;
			}
			if (preferences[i].name == "luggage"){
				big_luggage = preferences[i].value;
			}			
		}
	}
	console.log("animals : "+animals);
	console.log("smoking "+smoking);
	console.log("luggage "+big_luggage);

	console.log("Request preparation");
	$.ajax({
	  type: "POST",
	  url: "/searchTravel",
	  dataType: 'json',
	  data: JSON.stringify({"departure" : departure,
	  						"arrival" : arrival,
	  						"departure_date" : date,
	  						"price_max" : price,
	  						"animals" : animals,
	  						"smoking" : smoking,
	  						"luggage" : big_luggage
							})
	})
	.done(function( data ) { 	
		console.log("data received back");

		// Hide error field
		var alert_components = document.getElementsByClassName('error');
		for (var i = 0; i < alert_components.length; i++){
			alert_components[i].style.display = 'none';
		}

		//If there is error, handle appropriate error messages
		if (data['error']){

			//Display main error banner
			var searchError = document.getElementById("searchError");
			searchError.style.display = 'block';

			//error message as a palceholder
			if (data['error_src_dest']){
				$("#departure_search").attr('placeholder', data['error_src_dest']);
				$("#arrival_search").attr('placeholder', data['error_src_dest']);
			}

			//Error message append to the error banner
			if (data['error_samedeparture']){
				var error_div = document.getElementById('searchError');
				error_div.lastChild.data = data['error_samedeparture'];
			}


			if (data['error_datetime']){
				var span_error = document.getElementById('error_date_search');
				span_error.innerHTML = data['error_datetime'];
				span_error.style.display = 'block';
			}

			if (data['error_price']){
				var span_error = document.getElementById('error_price_search');
				span_error.innerHTML = data['error_price'];
				span_error.style.display = 'block';
			}
		}else{
			//handle success and redirect to the list of travel whereuser is the driver
			var success = document.getElementById("searchSuccess");
			success.style.display = 'block';
			window.location.replace("/resultSearch");
		}
	});	
}


