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


/*****************************************************************************/
/*                     Enhance widgets                                       */
/*****************************************************************************/
$(document).on('ready',function(){
	$('[data-widget="lightswitch"]').each(function(index,value){
		var text = $(this).html();
		$(this).html('<a href="#"><img src="icons/ws/light_light.png">'+text+'</a>');
	});
	
	$('[data-widget="lightdimmer"]').each(function(index,value){
		var text = $(this).html();
		$(this).html('<p>'+text+'</p><a href="#"><img src="icons/ws/light_light.png"></a><input type="range" value="0" min="0" max="255" step="5" data-highlight="true"/>');
	});

	$('[data-widget="shading"]').each(function(index,value){
		var text = $(this).html();
		$(this).html('<p>'+text+'</p><a href="#"><img src="icons/ws/fts_shutter_10.png" class="left"></a><a href="#"><img src="icons/ws/fts_shutter_100.png" class="right"></a><input type="range" value="0" min="0" max="255" step="5" data-highlight="true"/>');
	});
	
});





