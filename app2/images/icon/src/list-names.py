import os
import subprocess


list = {'scene':[],
		'light':[],
		'fts':[],
		'it':[],
		'audio':[],
		'control':[],
		'sani':[],
		'measure':[],
		'message':[],
		'phone':[],
		'status':[],
		'temp':[],
		'text':[],
		'time':[],
		'vent':[],
		'weather':[]}

for file in os.listdir('.'):

	# check if the file ends with .svg
	if file[-4:] == '.svg':
		for key in list:
			if file.startswith(key):

				list[key].append('\'' + file[0:-4] + '\'')
for key in list:
	print(key)
	print('')
	print( '[' + ','.join( sorted(list[key]) ) + ']' )
	print('')
	print('')
	print('')
