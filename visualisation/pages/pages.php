
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

	
	
		<div id='central_shading'>
		
		</div>

		<div id='firstfloor_living' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ws/scene_livingroom.png'>
					<h1>Living</h1>
					<div class='value'>
						<span data-widget='value' data-item='living.measurements.temperature' data-digits='1'>&deg;C</span>
					</div>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='true'>
					<h1>Light</h1>
					<div data-role='controlgroup' data-type='horizontal' align='center'>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='0' data-role='button' data-mini='true'>Dinner</a>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='1' data-role='button' data-mini='true'>Company</a>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='2' data-role='button' data-mini='true'>TV</a>
						<a id='$id' href='#' data-widget='button' data-item='living.scenes' data-value='3' data-role='button' data-mini='true'>Lights off</a>
					</div>
					<div class='group'>
						<div data-widget='lightswitch' data-item='living.lights.spots_kitchen'>
							Kitchen spots
						</div>
						<div data-widget='lightswitch' data-item='living.lights.light_kitchen'>
							Kitchen
						</div>
						<div data-widget='lightswitch' data-item='living.lights.spots_dinnertable'>
							Dinner table spots
						</div>
						<div data-widget='lightswitch' data-item='living.lights.light_dinnertable'>
							Dinner table
						</div>
					</div>
					<div class='group'>
						<div data-widget='lightdimmer' data-item='living.lights.light_tv'>
							TV lights
						</div>
					</div>
				</section>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='true'>
					<h1>Shading</h1>
					<div class='group'>
						<div data-widget='shading' data-item='living.windows.back.shading'>
							Back shading
						</div>
					</div>
				</section>	
			</div>
		</div>		
