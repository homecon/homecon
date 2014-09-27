
function set_alarm(id,page){
		alert(id);
		$.post( 'data/set_alarm.php', { 'id': id , 'page': page } );
}
