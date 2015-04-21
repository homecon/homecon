#!/usr/bin/python3
######################################################################################
#    Copyright 2015 Brecht Baeten
#    This file is part of KNXControl.
#
#    KNXControl is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KNXControl is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################



# fill in items with an 'sh_listen' attribute
for item in sh.match_items('*:sh_listen'):
	if item.conf['sh_listen'] != '':


		# try to parse linear combinations
		sum_value = 0;

		for prod in item.conf['sh_listen'].split('+'):
			prod_value = 1;
			for fact in prod.split('*'):

				source_item=sh.return_item(fact.replace(' ',''))
				if source_item is None:
					try:
						prod_value = prod_value*float(fact)
					except:
						logger.warning('failed to set %s to %s' % (item.id(),fact))
				else:
					prod_value = prod_value*source_item()

			sum_value = sum_value + prod_value

		# set the value of the new item
		item(sum_value)


# estimate direct and diffuse irradiation

# trigger the saving of measurements to mysql
sh.trigger(name='mysql_measurements')
