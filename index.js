window.addEventListener("load", function(){

    // Add a keyup event listener to our input element
    var name_input = document.getElementById('name_input');
	var dropdown = document.getElementById('dropdown');
	
    name_input.addEventListener("keyup", function(event){hinter(event)});

    // create one global XHR object 
    // so we can abort old requests when a new one is make
    window.hinterXHR = new XMLHttpRequest();
});


// Autocomplete for form
function hinter(event) {

    // retireve the input element
    var input = event.target;
	var helpers =
	{
		buildDropdown: function(result, dropdown, emptyMessage)
		{
			// Remove current options
			// Check result isnt empty
			if(result != '')
			{
				// Loop through each of the results and append the option to the dropdown
				$.each(result, function(k, v) {
					name_input.append('<option value="' + v.operation + '">' + v.operation + '</option>');
				});
			}
		}
	}


    // minimum number of characters before we start to generate suggestions
    var min_characters = 0;

    if (input.value.length < min_characters ) { 
        return;
    } else { 

        // abort any pending requests
        window.hinterXHR.abort();

        window.hinterXHR.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {

                // We're expecting a json response so we convert it to an object
                var response = JSON.parse( this.responseText ); 

                // clear any previously loaded options in the datalist
                helpers.buildDropdown(
                    jQuery.parseJSON(this.responseText ),
                    $('#dropdown'),
                    'Select an option'
                );

                
            }
        };

        window.hinterXHR.open("POST", "http://localhost:5000/", true);
		window.hinterXHR.setRequestHeader("Content-type", "application/json");
        window.hinterXHR.send(JSON.stringify({"data":input.value}))
    }
}