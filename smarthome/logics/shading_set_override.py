###########################################################################
# set override of the calling item to true
###########################################################################
#
#
override = True
now = sh.now()

trigger_str = trigger['source'].split('.')
trigger_str = trigger_str[-1]

source_str = sh.return_item(trigger['source']).changed_by()
source_str = source_str.split(':')
source_str = source_str[0]


if source_str=='KNX' and trigger_str=='pos' and (now.minute==0 or now.minute==30):
	override = False

if source_str=='KNX' and trigger_str=='pos' and sh.building.rain():
	override = False
	
if source_str=='Logic':
	override = False
	
if override:
	shading = sh.return_item(trigger['source']).return_parent()
	logger.warning(shading)
	logger.warning('trigger: '+ trigger['source'])
	logger.warning('changed by: '+ source_str)
	shading.override(True)

