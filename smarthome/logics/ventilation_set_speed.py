###########################################################################
# sets ventilation speed
###########################################################################
#
# 
#

# check if the speed was set by visu manual setting
logger.warning(sh.building.ventilation.speedcontrol.changed_by())
if sh.building.ventilation.speedcontrol.changed_by() == 'Visu':
	logger.warning('ventilation speed set manually')

# set the actual fan speed
if not(sh.building.ventilation.speedcontrol() == sh.building.ventilation.speedcontrol.prev_value()):
	logger.warning('speed set to %s' %(sh.building.ventilation.speedcontrol()) )

speeditems = []
for item in sh.building.ventilation.speeds:
	speeditems.append(sh.return_item(item.conf['item']))

if sh.building.ventilation.speedcontrol() == 0:
	speeditems[0](1)
	speeditems[1](0)
	speeditems[2](0)
	speeditems[3](0)
	
elif sh.building.ventilation.speedcontrol() == 1:
	speeditems[0](0)
	speeditems[1](1)
	speeditems[2](0)
	speeditems[3](0)
	
elif sh.building.ventilation.speedcontrol() == 2:
	speeditems[0](0)
	speeditems[1](0)
	speeditems[2](1)
	speeditems[3](0)
	
elif sh.building.ventilation.speedcontrol() == 3:
	speeditems[0](0)
	speeditems[1](0)
	speeditems[2](0)
	speeditems[3](1)
