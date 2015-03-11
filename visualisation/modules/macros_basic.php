<?php
function add_switch($item,$text){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$id = $page .'_'. str_replace('.','_',$item);

	echo "
						<span class='switch' id='$id' data-widget='basic.switch' data-item='$item' data-val-on='1' data-val-off='0' data-pic-on='icons/or/light_light.png' data-pic-off='icons/ffffff/light_light.png'>
							<a><img class='icon' src='icons/ffffff/light_light.png'/>$text</a>
						</span>
	";
}
function add_button($item,$value,$text){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$id = $page .'_'. str_replace('.','_',$item);

	echo "
						<a id='$id' href='#' data-widget='basic.button' data-item='$item' data-val='$value' data-role='button' data-mini='true'>$text</a>
	";
}
function add_scene_button($items,$values,$text){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$id = $page .'_'. str_replace('.','_',$item);

	echo "
						<a id='$id' href='#' data-widget='basic.button' data-item='$item' data-val='$value' data-role='button'>$text</a>
	";
}
function add_dimmer($item,$text){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$switch_id = $page .'_'. str_replace('.','_',$item)."_switch";
	$slider_id = $page .'_'. str_replace('.','_',$item)."_slider";
	echo "
	
						<span class='dimmer'>
							<p>$text</p>
							<span id='$switch_id' data-widget='basic.switch' data-item='$item' data-val-on='1' data-val-off='0' data-pic-on='icons/or/light_light.png' data-pic-off='icons/ffffff/light_light.png' class='switch'>
								<a class='ui-link'><img class='icon' src='icons/ffffff/light_light.png'></a>
							</span>
							<input id='$slider_id' data-widget='basic.slider' data-item='$item.value' type='range' value='0' min='0' max='255' step='5' data-highlight='true'/>
						</span>
	";
};
function add_shade_control($item,$text){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$up_id = $page .'_'. str_replace('.','_',$item)."_up";
	$down_id = $page .'_'. str_replace('.','_',$item)."_down";
	$slider_id = $page .'_'. str_replace('.','_',$item)."_slider";
	echo "
						<span class='shading'>
							<p>$text</p>
							<a id='$up_id'  data-widget='basic.button' data-item='$item.pos' data-val='0' class='left'><img class='icon' src='icons/ffffff/fts_shutter_10.png'></a>
							<input id='$slider_id' data-widget='basic.slider' data-item='$item.pos' type='range' value='0' min='0' max='255' step='5' data-highlight='true'/>
							<a id='$down_id'  data-widget='basic.button' data-item='$item.pos' data-val='255' class='right'><img class='icon' src='icons/ffffff/fts_shutter_100.png'></a>
						</span>";
};
function add_checkbox($item,$text){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$id = $page .'_'. str_replace('.','_',$item)."_check";
	echo "
						<label>
							<input type='checkbox' id='$id' data-widget='basic.checkbox' data-item='$item' data-mini='true'/>
							$text
						</label>";
};
function add_value($item,$unit,$decimals){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$id = $page .'_'. str_replace('.','_',$item)."_value";
	echo "
		<span id='$id' data-widget='basic.value' data-item='$item' data-unit='$unit' decimals='$decimals'>--- </span>";
	
};
function add_quantity($label,$item,$unit,$decimals){
	global $page;
	$page = explode('/',$page);
	$page = end($page);
	
	$id = $page .'_'. str_replace('.','_',$item)."_value";
	echo "
		<div class='quantity'>
			$label ";
			add_value($item,$unit,$decimals);
	echo "
		</div>";
	
};
function add_temperature($item,$text){
	
	echo "
		<div class='temperature'>
			$text ";
			add_value($item,"&deg;C",1);
	echo "
		</div>";
	
};

?>