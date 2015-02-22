//
// 
// view.js is part of KNXControl
// @author: Brecht Baeten
// @license: GNU GENERAL PUBLIC LICENSE
// 
//

/*****************************************************************************/
/*                     Header                                                */
/*****************************************************************************/
$(function(){
	$("body>[data-role='header']").toolbar();
});
// hide header elements from non admin users
$(document).on('connect',function(event,user_id){
	if(user_id!=1){
		$("#header a.hide").remove();
	}
});

/*****************************************************************************/
/*                     Menu                                                  */
/*****************************************************************************/
$(function(){
	$("#menu").panel().enhanceWithin();
});

// menu swipe
/*
$(document).on('swiperight', function(){
	if($(window).width()<800){
		$('#menu').panel("open");			
	};
});
*/

// menu bars
$(document).on('click','#menu_button', function(){
	$('#menu').panel("toggle");		
});

/*****************************************************************************/
/*                     Pagebuilder                                           */
/*****************************************************************************/

$(function(){
	$("#rendermenu").hide();
	$("#header nav div.pagebuilder").hide();
});
$(document).on('pageinit','#home_pagebuilder', function(){
	// change the menu panel with the pagebuilder menu
	$('#mainmenu').hide();
	$("#rendermenu").show();
	
	// remove the normal header buttons
	$("#header nav div.home").hide();
	$("#header nav div.pagebuilder").show();
});
$(document).on('click','a[href="#home_pagebuilder"]', function(){
	// change the menu panel with the pagebuilder menu
	$('#mainmenu').hide();
	$("#rendermenu").show();
	
	// remove the normal header buttons
	$("#header nav div.home").hide();
	$("#header nav div.pagebuilder").show();
});
$(document).on('click','a[href="#home_home"]', function(){
	location.reload();
	
	// change back to the menu panel
	$("#rendermenu").hide();
	$('#mainmenu').show();
	
	// show the header buttons
	$("#header nav div.home").show();
	$("#header nav div.pagebuilder").hide();
});


/*****************************************************************************/
/*                     General popups                                        */
/*****************************************************************************/
$(document).on('ready',function(){
	$("#message_popup").enhanceWithin().popup();
	$("#action_def_popup").enhanceWithin().popup();
	$("#measurement_def_popup").enhanceWithin().popup();
});



