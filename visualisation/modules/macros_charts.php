<?php
function add_chart($chart_title,$signals_str){

	$container = str_replace(' ','_',$chart_title.'_'.$signals_str);
	
	echo "
		<div id='$container' class='chart_placeholder' data-title='$chart_title' data-signals='$signals_str' data-chart='line' data-scale='quarter'></div>";
};

function add_bar_chart($chart_title,$signals_str){

	$container = str_replace(' ','_',$chart_title.'_'.$signals_str);
	
	echo "
		<div id='$container' class='chart_placeholder' data-title='$chart_title' data-signals='$signals_str' data-chart='bar' data-scale='week'></div>";
};
?>