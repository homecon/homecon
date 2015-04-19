

alles_uit = 1

for item in sh.find_items('light_check_off'):
	if item():
		alles_uit = 0
		
if alles_uit:
	sh.centraal.lights.status('off')
else:
	sh.centraal.lights.status('on')