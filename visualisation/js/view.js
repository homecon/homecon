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

/*****************************************************************************/
/*                     Panel                                                 */
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
/*                     General popups                                        */
/*****************************************************************************/
$(document).on('ready',function() {
	$("#action_def_popup").enhanceWithin().popup();
});





