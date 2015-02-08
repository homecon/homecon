language = {
	weekday: ['maandag','dinsdag','woensdag','donderdag','vrijdag','zaterdag','zondag'],
	weekday_short: ['maa','din','woe','don','vri','zat','zon'],
	month: ['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'],
	month_short: ['jan','feb','maa','apr','mei','jun','jul','aug','sep','okt','nov','dec'],
	temperature: 'temperatuur',
	wind: 'wind',
	irradiation: 'irradiatie',
	alarm: 'wekker',
	add_alarm: 'wekker toevoegen',
	select_action: 'selecteer actie',
	add_action: 'actie toevoegen',
	add_measurement: 'meting toevoegen',
// methods
// capitalize 1st letter	
	capitalize: function(string){
		return string.charAt(0).toUpperCase() + string.slice(1);
	},
	
// translate winddirection
	winddirection: function(deg){
		var str = '';
		if(deg<22.5){
			str = 'N';
		}
		if(deg<67.5){
			str = 'NO';
		}
		else if(deg<112.5){
			str = 'O';
		}
		else if(deg<157.5){
			str = 'ZO';
		}
		else if(deg<202.5){
			str = 'Z';
		}
		else if(deg<247.5){
			str = 'ZW';
		}		
		else if(deg<292.5){
			str = 'W';
		}
		else if(deg<337.5){
			str = 'NW';
		}
		else{
			str = 'N'
		}
		return str;
	}
}