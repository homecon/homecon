



/**
 * Objects
 */ 

$(document).on('pagebeforeshow',
	function () {

	
		// licht switches
		var text,item,id;

		text = $('[data-object="light.switch"]').html();
		item = $('[data-object="light.switch"]').attr('data-item');
		id = "test123";
		
		$('[data-object="light.switch"]').replaceWith(
		
			"<span class='switch' id='"+id+"' data-widget='basic.switch' data-item='"+item+"' data-val-on='1' data-val-off='0' data-pic-on='icons/or/light_light.png' data-pic-off='icons/ws/light_light.png'><a><img class='icon' src='icons/ws/light_light.png'/>"+text+"</a></span>"
		
		);
	
		// buttons
		text = $('[data-object="light.switch"]').html();
		item = $('[data-object="light.switch"]').attr('data-item');
		val = 1;
		
		$('[data-object="scene.button"]').replaceWith(
		
			"<a href='#' data-widget='basic.button' data-item='"+item+"' data-val='"+val+"' data-role='button' data-mini='true'>"+text+"</a>"
		);
	
	}
);