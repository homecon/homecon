<?php

// articles
function begin_article($class = NULL){

	if($class){
		echo "
		<article class=$class>";
	}
	else{
		echo "
		<article>";
	}
}
function end_article(){
	echo "
		</article>";
}
function add_header($text,$icon,$temperature_item = NULL){
	echo "
		<header>
			<img src='icons/ws/$icon'>
			<h1>$text</h1>";
			
	if($temperature_item){
		echo "
			<div class='climate'>";
				add_quantity("",$temperature_item,"&deg;C",1);
		echo "
				</div>";
	}		
	echo "
		</header>";
}

// collapsibels and collapsible sets
function begin_collapsible_set(){
	echo "
			<section data-role='collapsible-set'>";
}
function end_collapsible_set(){
	echo "
			</section>";
}
function begin_collapsible($title,$collapsed = NULL){
	if($collapsed){
		$collapsed_str = "true";
	}
	else{
		$collapsed_str = "false";
	}
	echo "
			<section data-role='collapsible' data-theme='c' data-content-theme='a' data-collapsed='$collapsed_str'>
				<h1>$title</h1>";
}
function end_collapsible(){
	echo "
		</section>";
}

// add title text
function add_title($text){
	echo "
		$text";
}

// groups of controls with variable number of collumns and control groups
function begin_group($columns = NULL){
	if($columns==2){
		echo "
			<div class='twocols'>";
	}
	else{
		echo "
			<div>";
	}
}
function end_group(){
	echo "
			</div>";
}
function add_space(){
	echo "
			</br>";
}
function begin_controlgroup(){
	echo "
			<div>
				<div data-role='controlgroup' data-type='horizontal' align='center'>";
}
function end_controlgroup(){
	echo "
				</div>
			</div>";
}


?>