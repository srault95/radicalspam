var global_options = {
    spin_opts: {
          lines: 13 // The number of lines to draw
        , length: 28 // The length of each line
        , width: 14 // The line thickness
        , radius: 42 // The radius of the inner circle
        , scale: 1 // Scales overall size of the spinner
        , corners: 1 // Corner roundness (0..1)
        , color: '#000' // #rgb or #rrggbb or array of colors
        , opacity: 0.2 // Opacity of the lines
        , rotate: 0 // The rotation offset
        , direction: 1 // 1: clockwise, -1: counterclockwise
        , speed: 1 // Rounds per second
        , trail: 60 // Afterglow percentage
        , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
        , zIndex: 2e9 // The z-index (defaults to 2000000000)
        , className: 'spinner' // The CSS class to assign to the spinner
        , top: '50%' // Top position relative to parent
        , left: '50%' // Left position relative to parent
        , shadow: true // Whether to render a shadow
        , hwaccel: false // Whether to use hardware acceleration
        , position: 'absolute' // Element positioning
    }
};

function spinnerShow(){
    $('#spinner').spin(global_options.spin_opts);
}

function spinnerHide(){
    $('#spinner').spin(false);
}

function ajax(uri, method, data) {
    var request = {
        url: uri,
        type: method,
        async: false,
        timeout: 60 * 1000,
        contentType: "application/json",
        accepts: "application/json",
        //cache: false,
        dataType: 'json',
        data: data,
        traditional: true,
        error: function(jqXHR) {
        	//TODO: ecrire erreur dans champs status
            console.log("ajax error " + jqXHR.status);
        }
    };
    return $.ajax(request);
}

function debug_doc(options) {
	
    $(options.button_id).click(function(e){
        e.preventDefault();
        if ($(options.parent_id).is(":visible")) {
        	$(options.parent_id).toggle();	
        } else {
 		   	$.ajax({
		        url: options.url,
		        cache: false,
		        complete: function(jqXHR, textStatus){
		            if (textStatus == "success"){
		            	$(options.target_id).text(jqXHR.responseJSON);
		            }
		        }
		   	});
 		   $(options.parent_id).toggle();
        }
    });
}
