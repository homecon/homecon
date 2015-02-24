import os
import subprocess


cols = {'b': '#000000', 'w': '#ffffff', 'o': '#f79a1f'}

for file in os.listdir("svg"):
	print file
	
	for key in cols:
		f1 = open("svg/"+file, 'r')
		f2 = open("svg/"+file+".tmp", 'w')
		for line in f1:
			f2.write(line.replace('#000000', cols[key]))
		f2.close()
		f1.close()
		
		# export
		subprocess.call('inkscape svg/'+file+'.tmp --export-width=200 --export-png='+key+'/'+file[0:-4]+'.png')
		
		# remove tmp file
		os.remove("svg/"+file+".tmp")
	
	f1.close()
