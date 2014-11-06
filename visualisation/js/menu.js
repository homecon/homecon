
// menu swipe
$(document).on('swiperight', function(){
	if($(window).width()<800){
		$.mobile.activePage.find('#menu').panel("open");			
	}
});

// menu bars
$(document).on('click','#menu_button', function(){
	if($(window).width()<800){
		$.mobile.activePage.find('#menu').panel("toggle");			
	}
});


