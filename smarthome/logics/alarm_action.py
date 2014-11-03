	
	
	
logger.warning(trigger['source'])
logger.warning(trigger['value'])

item = sh.return_item(trigger['source'])
# check if the item exists
if item:
	item(trigger['value'])