	
	
	
logger.warning(trigger['source'])
logger.warning(trigger['value'])

item = sh.return_item(trigger['source'])
item(trigger['value'])