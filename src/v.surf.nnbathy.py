#!/usr/bin/env python

############################################################################
#
# MODULE:     v.surf.nnbathy.py
#
# AUTHOR(S):  Adam Laza (mentor: Martin Landa)
#             (based on v.surf.nnbathy from GRASS 6)
#
# PURPOSE:    Interpolate raster surface using the "nnbathy" natural
#             neighbor interpolation program.
#
# COPYRIGHT:  (c) 2014 Adam Laza, and the GRASS Development Team
#
# LICENSE:    This program is free software under the GNU General Public
#             License (>=v2). Read the file COPYING that comes with
#             GRASS for details.
#
#############################################################################

# NOTES:
#
# 1. Requires nnbathy executable v 1.75 or later. Follow the instruction in
#    html manual page to obtain it.
#
# 2. When creating the input raster map, make sure it's extents cover
#    your whole region of interest, the cells you wish to interplate on are
#    NULL, and the resolution is correct. Same as most GRASS raster modules
#    this one is region sensitive too.

#%module
#% description: Interpolates a raster map using the nnbathy natural neighbor interpolation program.
#%end
#%option G_OPT_V_INPUT
#% key: input
#% description: Name of input vector points map
#% guisection: Input data
#% required : no
#%end
#%option G_OPT_V_FIELD
#% key: layer
#% label: Layer number
#% description: If set to 0, z coordinates are used. (3D vector only)
#% guisection: Selection
#%end
#%option G_OPT_F_INPUT
#% key: file
#% description: Containing x,y,z data as three space separated columns
#% guisection: Input data
#% required : no
#%end
#%option G_OPT_R_OUTPUT
#%end
#%option G_OPT_DB_COLUMN
#% key: zcolumn
#% description: Name of the attribute column with values to be used for approximation (if layer>0)
#% guisection: Settings
#%end
#%option G_OPT_DB_WHERE
#% key: kwhere
#% guisection: Selection
#%end
#%option
#% key: algorithm
#% type: string
#% options: l,nn,ns
#% answer: nn
#% descriptions: l;Linear;nn;Sibson natural neighbor;ns;Non-Sibsonian natural neighbor
#% description: Settings
#%end

import os
import atexit
import sys

from grass.script.core import parser
import grass.script as grass

### kod z http://trac.osgeo.org/grass/browser/grass-addons/grass6/vector/v.surf.nnbathy/v.surf.nnbathy

TMP=None
TMPcat=None
TMPXYZ=None
XYZout=None

def main():
	### uvodni kontroly
	if (options['input'] and options['file']):
		grass.message("Please specify either the 'input' or 'file' option, not both.")
	
	if not(options['input'] or options['file']):
		grass.message("Please specify either the 'input' or 'file' option.")

	if (options['file'] and os.path.isfile(options['file'])):
		grass.message("File "+options['file']+" does not exist.")

	
	### vypocetni region
	reg = grass.read_command("g.region", flags='p')    ### r.reclass.area.py  ??flags='p'
	kv = grass.parse_key_val(reg, sep=':')
	reg_N = float(kv['north'])
	reg_W = float(kv['west'])
	reg_S = float(kv['south'])
	reg_E = float(kv['east'])
	cols = int(kv['cols'])
	rows = int(kv['rows'])
	nsres = float(kv['nsres'])
	ewres = float(kv['ewres'])
	reg=(reg_N, reg_W, reg_S, reg_E)
	area=(reg_N-reg_S)*(reg_E-reg_W)
	ALG=options['algorithm']

	if area == 0:
		grass.fatal(_("xy-locations are not supported"))
		grass.fatal(_("Need projected data with grids in meters"))
	
	global TMPXYZ
	TMPXYZ=grass.tempfile()
		
	if not options['file'] :
		TMPcat=grass.tempfile()		
			
		if int(options['layer']) == 0:
			LAYER=''
			COLUMN=''
		else:
			LAYER=int(options['layer'])
			if options['zcolumn']:
				COLUMN=options['zcolumn']
			else:
				grass.message('Name of z column required for 2D vector maps.')	
				
		if options['kwhere']:
			grass.run_command("v.out.ascii",flags='r', overwrite=1, input=options['input'], output=TMPcat, format="point", separator="space",dp=15, where=options['kwhere'], layer=LAYER, columns=COLUMN)
		else:
			grass.run_command("v.out.ascii",flags='r', overwrite=1, input=options['input'], output=TMPcat, format="point", separator="space", dp=15, layer=LAYER, columns=COLUMN)
		
		if int(options['layer']) > 0:
			fin=open(TMPcat, 'r')
			fout=open(TMPXYZ, 'w')
			# TODO: try block... ???? duvod? co vlastne zkousim?
			try:
				for line in fin:
					parts = line.split(" ")
					#print parts[0]+' '+parts[1]+' '+parts[3]
					fout.write(parts[0]+' '+parts[1]+' '+parts[3])
			except:
				# print "Invalid input!"
				grass.message("Invalid input!")	
			fin.close()
			fout.close()
		else:
			# TODO: chyba ?
			grass.message("Z coordinates are used.")
	else:
		TMPXYZ=options['file']
	
	# set the working region for nnbathy (it's cell-center oriented)
	nn_n=reg_N - nsres/2
	nn_s=reg_S + nsres/2
	nn_w=reg_W + ewres/2
	nn_e=reg_E - ewres/2
	
	null="NaN"
	type="double"

	####interpolate
	grass.message('"nnbathy" is performing the interpolation now. This may take some time.')
	grass.message("Once it completes an 'All done.' message will be printed.")
	
	###volani nnbathy
	global XYZout
	XYZout=grass.tempfile()
	#saveout=sys.stdout
	#fsock=open(XYZout, 'w')
	#sys.stdout=fsock
	grass.call(['nnbathy', '-W', '%d' % 0, '-i', '%s' % TMPXYZ, '-o', '%s' % XYZout, '-x', '%d' % nn_w, '%d' % nn_e, '-y', '%d' % nn_n, '%d' % nn_s, '-P', '%s' % ALG, '-n', '%dx%d' % (cols,rows)])
	#sys.stdout=saveout
	#fsock.close()
	# Y in "r.stats -1gn" output is in descending order, thus -y must be in
	# MAX MIN order, not MIN MAX, for nnbathy not to produce a grid upside-down

	

	# convert the X,Y,Z nnbathy output into a GRASS ASCII grid, then import with r.in.ascii:
	# 1 create header
	TMP=grass.tempfile()	
	header=open(TMP,'w')
	header.write('north: %s\nsouth: %s\neast: %s\nwest: %s\nrows: %s\ncols: %s\ntype: %s\nnull: %s\n\n'% (nn_n, nn_s, nn_e, nn_w, rows, cols, type, null))
	header.close()
	
	# 2 do the conversion
	grass.message("Converting nnbathy output to GRASS raster ...")
	fin=open(TMPXYZ,'r')	
	fout=open(TMP,'a')
	cur_col=1;
	for line in fin:
		parts = line.split(" ")
		if cur_col==cols:
			cur_col=0
			fout.write(str(parts[2]))
		else:	
			fout.write(str(parts[2]).rstrip('\n')+' ')
		cur_col+=1
	
	fin.close()
	fout.close()
	
	# 3 import
	grass.run_command('r.in.ascii',input=TMP, output=options['output'], quiet=1)

	# store comand history in raster's metadata
	
	if options['input']:
		grass.run_command('r.support',map=options['output'],history="v.surf.nnbathy alg="+options['algorithm']+" input="+options['input']+" output="+options['output'])
	else:grass.run_command('r.support',map=options['output'],history="v.surf.nnbathy alg="+options['algorithm']+" input="+options['file']+" output="+options['output'])
	
	grass.run_command('r.support', map=options['output'], history="")
	grass.run_command('r.support', map=options['output'], history="nnbathy run syntax:")
	grass.run_command('r.support', map=options['output'], history="")
	grass.run_command('r.support', map=options['output'], history="nnbathy -W 0 -P alg=$ALG -n ${cols}x$rows" )
	grass.run_command('r.support', map=options['output'], history="-x $nn_w $nn_e ")
	grass.run_command('r.support', map=options['output'], history="-y $nn_n $nn_s ")
	grass.run_command('r.support', map=options['output'], history="-i tmp_in > tmp_out")
	grass.run_command('r.support', map=options['output'], history="")

	grass.message("Done. "+options['output']+" created.")

	return 0

def cleanup():
	if TMP:
		os.remove(TMP)
	if TMPXYZ:
		os.remove(TMPXYZ)
	if XYZout:
		os.remove(XYZout)

if __name__ == "__main__":
	options, flags = parser()
	atexit.register(cleanup)
	main()
