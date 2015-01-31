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
/*                     Templates                                             */
/*****************************************************************************/
var template = {
	alarm: '',
	alarm_action: '',
	alarm_action_def: ''
};

$(document).on('pagebeforecreate',function(){
	$.each(template,function(key,value){
		template[key] = $('#templates .'+key).prop('outerHTML');
	});
});








