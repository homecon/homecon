
<!-- this file should be automatically generated -->
<!-- it contains all custom pages in the visualization -->


		<div id='home' data-role='page' data-theme='b'>
			<div data-role='content'>
		
				<section>
					<div data-widget='clock'></div>
				</section>
				<section>
					<div data-widget='current_weather' data-item-temperature='' data-item-wind=''  data-item-irradiation=''></div>
				</section>
				<section>
					<div data-widget='weather_forecast'></div>
				</section>
		
			</div>
		</div>

	
	
		<div id='central_shading' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ws/fts_sunblind.png'>
					<h1>Central shading control</h1>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Light</h1>
					<div class='group'>
						<div data-role='shading' data-item='central.shading.shading_firstfloor'>
							Shading first floor
						</div>
					</div>
				</section>
			</div>
		</div>

		<div id='firstfloor_living' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ws/scene_livingroom.png'>
					<h1>Living</h1>
					<div class='value'>
						<span data-role='displayvalue' data-item='living.measurements.temperature' data-digits='1'></span>&deg;C
					</div>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Light</h1>
					<div class='group' data-role='controlgroup' data-type='horizontal' align='center'>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='0' data-role='button' data-mini='true'>Dinner</a>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='1' data-role='button' data-mini='true'>Company</a>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='2' data-role='button' data-mini='true'>TV</a>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='3' data-role='button' data-mini='true'>Lights off</a>
					</div>
					<div class='group'>
						<div data-role='lightswitch' data-item='living.lights.spots_eiland'>
							Kitchen spots
						</div>
						<div data-role='lightswitch' data-item='living.lights.licht_eiland'>
							Kitchen
						</div>
						<div data-role='lightswitch' data-item='living.lights.licht_eettafel'>
							Dinner table spots
						</div>
						<div data-role='lightswitch' data-item='living.lights.licht_zithoek'>
							Dinner table
						</div>
					</div>
					<div class='group'>
						<div data-role='lightdimmer' data-item='living.lights.spots_zithoek.value'>
							TV lights
						</div>
						<div data-role='lightdimmer' data-item='living.lights.mood_light.value'>
							Mood lights
						</div>
					</div>
				</section>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='true'>
					<h1>Shading</h1>
					<div class='group'>
						<div data-role='shading' data-item='living.windows.keuken_links.shading.pos'>
							Back shading
						</div>
						<div data-role='shading' data-item='living.windows.front.shading.pos'>
							Front shading
						</div>
					</div>
				</section>	
			</div>
		</div>		
