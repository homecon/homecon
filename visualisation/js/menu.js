
// menu swipe
$( document ).on( "pageinit", function(){
    $( document ).on( "swiperight", function(){
	
		if($(window).width()<800){
			$( "#menu" ).panel( "open" );	
		}
		
    });
});