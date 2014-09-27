<?php

if(  (strpos($page,'central') !== false) ){
	$data_collapsed_section1 = 'false';
}
else{
	$data_collapsed_section1 = 'true';
}
if(  strpos($page,'firstfloor') !== false || strpos($page,'home') !== false ){
	$data_collapsed_section2 = 'false';
}
else{
	$data_collapsed_section2 = 'true';
}
if(  strpos($page,'secondfloor') !== false ){
	$data_collapsed_section3 = 'false';
}
else{
	$data_collapsed_section3 = 'true';
}



echo "
		<nav class=$page_class data-role='collapsible-set' data-corners='false'>
			<section data-role='collapsible' class='ui-collapsible-inset' data-theme='c' data-content-theme='a' data-inset='false' data-collapsed='$data_collapsed_section1' >			
				<h1>Central</h1>
				<ul data-role='listview'>
					<li><a href='index.php?web=$web&page=pages/central_light'><img src='icons/ws/light_light.png'>Light</a></li>
					<li><a href='index.php?web=$web&page=pages/central_shading'><img src='icons/ws/fts_sunblind.png'>Shading</a></li>
					<li><a href='index.php?web=$web&page=pages/central_indoor'><img src='icons/ws/sani_heating.png'>Indoor climate</a></li>
					<li><a href='index.php?web=$web&page=pages/central_weather'><img src='icons/ws/weather_cloudy_light.png'>Weather</a></li>
					<li><a href='index.php?web=$web&page=pages/central_energy'><img src='icons/ws/measure_power_meter.png'>Energy</a></li>
				</ul>
			</section>
			<section data-role='collapsible' class='ui-collapsible-inset' data-theme='c' data-content-theme='a' data-inset='false' data-collapsed='$data_collapsed_section2' >			
				<h1>First floor</h1>
				<ul data-role='listview'>
					<li><a href='index.php?web=$web&page=pages/firstfloor_living'><img src='icons/ws/scene_livingroom.png'>Living</a></li>
					<li><a href='index.php?web=$web&page=pages/firstfloor_hallway'><img src='icons/ws/scene_hall.png'>Hallway</a></li>
				</ul>
			</section>
			<section data-role='collapsible' class='ui-collapsible-inset' data-theme='c' data-content-theme='a' data-inset='false' data-collapsed='$data_collapsed_section3' >			
				<h1>Second floor</h1>
				<ul data-role='listview'>
					<li><a href='index.php?web=$web&page=pages/secondfloor_corridor'><img src='icons/ws/scene_stairs.png'>Corridor</a></li>
					<li><a href='index.php?web=$web&page=pages/secondfloor_bathroom'><img src='icons/ws/scene_bath.png'>Bathroom</a></li>
					<li><a href='index.php?web=$web&page=pages/secondfloor_bedroom1'><img src='icons/ws/scene_sleeping_alternat.png'>Bedroom</a></li>
				</ul>
			</section>
		</nav>
";


?>