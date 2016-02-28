
(function(document) {
	'use strict';

	// Grab a reference to our auto-binding template
	// and give it some initial binding values
	// Learn more about auto-binding templates at http://goo.gl/Dx1u2g
	var app = document.querySelector('#app');

	// Sets app default base URL
	app.baseUrl = '';
	if (window.location.port === '') {  // if production
		// Uncomment app.baseURL below and
		// set app.baseURL to '/your-pathname/' if running from folder in production
		// app.baseUrl = '/polymer-starter-kit/';
	}
	app.displayInstalledToast = function() {
		// Check to make sure caching is actually enabled—it won't be in the dev environment.
		if (!Polymer.dom(document).querySelector('platinum-sw-cache').disabled) {
			Polymer.dom(document).querySelector('#caching-complete').show();
		}
	};

	app.checkToken = function(token){
		// Checks if the app token is valid
		var valid = false;
		try{
			var parts = token.split('.');
			var header = JSON.parse(atob(parts[0]));
			var payload = JSON.parse(atob(parts[1]));

			if( Date.now() / 1000 < payload['exp'] ){
				valid = true;
			}
		}
		catch(e){
		}
		
		valid = true; // for testing
		return valid;

	};
	app.checkRoute = function(route,token){
		var allowed = false;
		// check if route is valid
		if(app.checkToken(token)){

			var parts = app.token.split('.');
			var header = JSON.parse(atob(parts[0]));
			var payload = JSON.parse(atob(parts[1]));

			try{
				if(payload['permission']>=9){
					allowed =  true;
				}
				else if(payload['permission']>=1){
					if( ['login','ranking','pron','results','profile','logout'].indexOf(route)>-1 ){
						allowed = true
					}
				}
				else{
					if( ['login','logout'].indexOf(route)>-1 ){
						allowed = true
					}
				}
			}
			catch(e){
			}
		}
		allowed = true;  // for testing
		return allowed;
	}

	// Listen for template bound event to know when bindings
	// have resolved and content has been stamped to the page
	app.addEventListener('dom-change', function() {
		console.log('Our app is ready to rock!');
	});


	// See https://github.com/Polymer/polymer/issues/1381
	window.addEventListener('WebComponentsReady', function() {
		// imports are loaded and elements have been registered
	});

	// Scroll page to top and expand header
	app.scrollPageToTop = function() {
		//app.$.headerPanel.scrollToTop(true);
	};

	app.closeDrawer = function() {
		app.$.main.closeDrawer();
	};

	// temporary definition of pages
	app.pages = {
		'sections': [
			{
				'title': 'Centraal',
				'pages': [
					{
						'id': 0,
						'title': 'Zonnewering',
						'icon': 'scene_livingroom',
						'header': {},
					},
					{
						'id': 1,
						'title': 'Energie',
						'icon': 'scene_livingroom'
					},
					{
						'id': 2,
						'title': 'Zonnewering',
						'icon': 'scene_livingroom'
					}
				]
			},
			{
				'title': 'Gelijkvloers',
				'pages': [
					{
						'id': 3,
						'title': 'Living',
						'icon': 'scene_livingroom'
					},
					{
						'id': 4,
						'title': 'Bureau',
						'icon': 'scene_office'
					},
				]
			},
			{
				'title': 'Verdieping',
				'pages': [],
			}
		]
	};

	// set the starting page to home
	app.page = 'home'

})(document);
