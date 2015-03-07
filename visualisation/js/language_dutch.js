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
	export_measurements: 'metingen exporteren',
	save: 'opslaan',
	settings_saved: 'settings opgeslagen',
	add_user: 'gebruiker toevoegen',
	delete_user: 'gebruiker verwijderen',
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