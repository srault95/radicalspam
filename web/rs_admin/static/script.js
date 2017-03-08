function ajax(uri, method, data, new_options, callback_error) {
	
    var options_default = {
        timeout: 120 * 1000, //120 seconds
        cache: true,
        dataType: 'json',
    };
	
	var options = $.extend(true, {}, options_default, new_options);
	
    var request = {
        url: uri,
        type: method,
        timeout: options.timeout,
        cache: options.cache,
        dataType: options.dataType,
        data: data,
        error: function(jqXHR, textStatus, errorThrown) {
        	//TODO: ecrire erreur dans champs status
        	//if(textStatus === 'timeout')
        	if (callback_error){
        		callback_error(jqXHR, textStatus, uri, method, data, options);
        	} else {
        		console.log("ajax error : ", jqXHR, textStatus);
        	}
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

$(document).ready(function() {

    $('.human-number').each(function(i, item){
        var value = $(item).text();
         $(item).text(Humanize.formatNumber(value));
    });

    $('.human-size-mb').each(function(i, item){
        var value = $(item).text();
         $(item).text(Humanize.fileSize(value));
    });
    
    toastr.options = {
      "closeButton": true,
      "debug": false,
      "newestOnTop": false,
      "progressBar": true,
      "positionClass": "toast-top-right",
      "preventDuplicates": false,
      "onclick": null,
      "showDuration": "3000",
      "hideDuration": "1000",
      "timeOut": "5000",
      "extendedTimeOut": "8000",
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut"
    };
    
    $(document).ajaxStart($.blockUI).ajaxStop($.unblockUI);
    
    var ajaxErrorMsg = "<h2>An unexpected error has occurred</h2>"+
                       "<p>The administrator has been notified.</p>"+
                       "<p>Sorry for the inconvenience!</p>";

    $(document).ajaxError(function(){
        toastr['error'](ajaxErrorMsg, {showDuration: 5000, 
                                      closeButton: true});
    });
    
});