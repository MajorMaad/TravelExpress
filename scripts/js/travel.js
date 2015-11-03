//Global variables
var marker_dep;
var marker_arr;
var research_auto_complete_dep;
var research_auto_complete_arr;

var mapOptions = {
	    center:new google.maps.LatLng(46.887678, -72.260262),
	    zoom:5,
	    mapTypeId:google.maps.MapTypeId.ROADMAP,
	    mapTypeControl: false,
		streetViewControl: false
	};

function initializeGoogleMapsAdder() {

		
	//Create 2 map objects
	var map_dep = new google.maps.Map(document.getElementById("gmapDeparture"), mapOptions);
	var map_arr = new google.maps.Map(document.getElementById("gmapArrival"), mapOptions);

	//Create the geocoder guy
	var geocoder = new google.maps.Geocoder;

	//Bind listener for a specific marker and process the input	
	map_dep.addListener('click', function(event) {
		placeMarker(event.latLng, map_dep, "departure");
	    geocodeLatLng(geocoder, map_dep, event.latLng, "departure");
	});
	
	map_arr.addListener('click', function(event) {		
		placeMarker(event.latLng, map_arr, "arrival");
		geocodeLatLng(geocoder, map_arr, event.latLng, "arrival");
	});

	//Enable the autocomplete feature
	autocompleteOn("departure", map_dep);
	autocompleteOn("arrival", map_arr);

}

function initializeGoogleMapsModifyer() {

	var mapOptions = {
	    center:new google.maps.LatLng(46.887678, -72.260262),
	    zoom:5,
	    mapTypeId:google.maps.MapTypeId.ROADMAP,
	    mapTypeControl: false,
		streetViewControl: false
	};
	
	//Create 2 map objects
	var map_dep = new google.maps.Map(document.getElementById("gmapDeparture_modify"), mapOptions);
	var map_arr = new google.maps.Map(document.getElementById("gmapArrival_modify"), mapOptions);

	//Create the geocoder guy
	var geocoder = new google.maps.Geocoder;

	//Bind listener for a specific marker and process the input	
	map_dep.addListener('click', function(event) {
		placeMarker(event.latLng, map_dep, "departure_modify");
	    geocodeLatLng(geocoder, map_dep, event.latLng, "departure_modify");
	});
	
	map_arr.addListener('click', function(event) {		
		placeMarker(event.latLng, map_arr, "arrival_modify");
		geocodeLatLng(geocoder, map_arr, event.latLng, "arrival_modify");
	});

	//Bind the input to the marker creation
	codeAddress(geocoder, map_dep, "departure_modify");
	codeAddress(geocoder, map_arr, "arrival_modify");

	//Enable the autocomplete feature
	autocompleteOn("departure_modify", map_dep);
	autocompleteOn("arrival_modify", map_arr);
}


function initializeResearchAutocomplete(){

	var research_auto_complete_dep = new google.maps.places.Autocomplete(
		/** @type {HTMLInputElement} */(document.getElementById('departure_search')),
		{ types: ['geocode'] }
		);
	google.maps.event.addListener(research_auto_complete_dep, 'place_changed', function() {});
		
	var research_auto_complete_arr = new google.maps.places.Autocomplete(
		/** @type {HTMLInputElement} */(document.getElementById('arrival_search')),
		{ types: ['geocode'] }
		);
	google.maps.event.addListener(research_auto_complete_arr, 'place_changed', function() {});
}

//function to put marker on specific map
function placeMarker(location, targetMap, context) {

	if (context == "departure" || context =="departure_modify"){
		if (!marker_dep){
			console.log("new marker !!");
			marker_dep = new google.maps.Marker({
		        position: location, 
		        map: targetMap,
		        visble: true
		    });
		}else{
			console.log("already here");
			marker_dep.setPosition(location);
		}
	}

	if (context == "arrival" || context =="arrival_modify"){
		if (!marker_arr){
			console.log("new marker !!");
			marker_arr = new google.maps.Marker({
		        position: location, 
		        map: targetMap,
		        visble: true
		    });
		}else{
			console.log("already here");
			marker_arr.setPosition(location);
		}		
	}
}

//Decode latLng to a readable address
//https://developers.google.com/maps/documentation/javascript/examples/geocoding-reverse
function geocodeLatLng(geocoder, map, location, context) {
	geocoder.geocode({'location': location}, function(results, status) {
		if (status === google.maps.GeocoderStatus.OK) {
			if (results[1]) {
				map.setZoom(8);
				map.setCenter(location);
				var readableField = document.getElementById(context);
				readableField.value = results[1].formatted_address;
			} else {
				window.alert('No results found');
			}
		} else {
		  window.alert('Geocoder failed due to: ' + status);
		}
	});
}

//Encode LatLng from an address
function codeAddress(geocoder, target_map, context) {
    var address = document.getElementById(context).value;
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        target_map.setCenter(results[0].geometry.location);
        var position_marker = results[0].geometry.location
        placeMarker(position_marker, target_map, context);
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
}

//Enable autocomplete
// https://developers.google.com/maps/documentation/javascript/examples/places-autocomplete
function autocompleteOn(targetInput, targetMap){		
	var input = /** @type {!HTMLInputElement} */(
		document.getElementById(targetInput)
	);

	var depComplete = new google.maps.places.Autocomplete(input);
  	depComplete.bindTo('bounds', targetMap);

  	depComplete.addListener('place_changed', function() {
	    var place = depComplete.getPlace();
	    if (!place.geometry) {
	      window.alert("Autocomplete's returned place contains no geometry");
	      return;
	    }

	    //Put a marker on place :
	    placeMarker(place.geometry.location, targetMap, targetInput);

	    var address = '';
	    if (place.address_components) {
	      address = [
	        (place.address_components[0] && place.address_components[0].short_name || ''),
	        (place.address_components[1] && place.address_components[1].short_name || ''),
	        (place.address_components[2] && place.address_components[2].short_name || '')
	      ].join(', ');
	    }
  	});
}



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


