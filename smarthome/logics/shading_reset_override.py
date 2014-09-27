###########################################################################
# reset overrides to false runs at 0h
###########################################################################
#
#

logger.warning('reset')
sh.logics.reset_override('off')

for override in sh.match_items('*.override'):
	override(False)

