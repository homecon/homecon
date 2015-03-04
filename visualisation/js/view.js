/*
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
*/

/*****************************************************************************/
/*                     Header                                                */
/*****************************************************************************/
$(function(){
	$("body>[data-role='header']").toolbar();
});
// hide header elements from non admin users
$(document).on('authenticated',function(event,user_id){
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


/*****************************************************************************/
/*                     General popups                                        */
/*****************************************************************************/
$(document).on('ready',function(){
	$("#message_popup").enhanceWithin().popup();
	$("#action_def_popup").enhanceWithin().popup();
	$("#measurement_def_popup").enhanceWithin().popup();
});



