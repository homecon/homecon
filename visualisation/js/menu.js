
// menu swipe
$(document).bind("pageinit", function() {
    $(document).bind( "swiperight", function(){
	
		if($(window).width()<800){
			$( "#menu" ).panel( "open" );	
		}
		
    });
});