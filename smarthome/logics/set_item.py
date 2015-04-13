# sets the item in trigger['source'] to value in trigger['value']
	
logger.info(trigger['source'])
logger.info(trigger['value'])

item = sh.return_item(trigger['source'])

# check if the item exists
#if item:
item(trigger['value'])
