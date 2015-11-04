/*Global variables :*/
//Markers
var marker_dep;
var marker_arr;

//Autocompletion
var research_auto_complete_dep;
var research_auto_complete_arr;

//mapOption for the map creation
var mapOptions = {
	    center:new google.maps.LatLng(46.887678, -72.260262),
	    zoom:5,
	    mapTypeId:google.maps.MapTypeId.ROADMAP,
	    mapTypeControl: false,
		streetViewControl: false
	};


/*Initialize 2 google maps for the AddTravel.html template*/
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


/*Initialize 2 google maps for the ModifyTravel.html template*/
function initializeGoogleMapsModifyer() {
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


/*Create 2 autocompletion objects for the ReserachTravel.html template*/
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
		targetMap.setCenter(location);
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
		targetMap.setCenter(location);	
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
