var h1_current = -1;
var h2_current = -1;
var m1_current = -1;
var m2_current = -1;

var path = "icons/clock/";

function flip(id,num){
    var src1 = path + num.toString() + ".png";
	image = document.getElementById(id);
	image.src = src1;
}
function retroClock(){
	now = new Date();
	h1 = Math.floor( now.getHours() / 10 );
	h2 = now.getHours() % 10;
	m1 = Math.floor( now.getMinutes() / 10 );
	m2 = now.getMinutes() % 10;
	   
	if( h2 != h2_current){
		flip('hoursRight',h2);
		h2_current = h2;
				
		flip('hoursLeft',h1);
		h1_current = h1;
    }
       
	if( m2 != m2_current,m2){
		flip('minutesRight',m2);
		m2_current = m2;

		flip('minutesLeft',m1);
		m1_current = m1;
	}
}
function retroDate(){

	now = new Date();
	weekday = now.getDay();
	day = now.getDate();
	month = now.getMonth();
	year = now.getFullYear();

	var day_str=new Array(); 
		day_str[0]="Zondag";
		day_str[1]="Maandag";       
		day_str[2]="Dinsdag";
		day_str[3]="Woensdag";
		day_str[4]="Donderdag";       
		day_str[5]="Vrijdag";
		day_str[6]="Zaterdag";
		
	
	var month_str=new Array(); 
		month_str[1]="januari";       
		month_str[2]="februari";
		month_str[3]="maart";
		month_str[4]="april";       
		month_str[5]="mei";
		month_str[6]="juni";
		month_str[7]="juli";
		month_str[8]="augustus";
		month_str[9]="september";       
		month_str[10]="oktober";
		month_str[11]="november";
		month_str[12]="december";
	
	var str =  day_str[weekday] + " " + day.toString() + " " + month_str[month] + " " + year.toString();
	
	date = document.getElementById('date');
	date.innerHTML = str;
}
function sleep(miliseconds) {
	var currentTime = new Date().getTime();

	while (currentTime + miliseconds >= new Date().getTime()) {
	}
}

window.onload = function(){
	retroClock();
	retroDate();
};

setInterval('retroClock()', 30000);
setInterval('retroDate()', 60000);