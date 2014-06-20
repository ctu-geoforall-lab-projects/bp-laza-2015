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

from grass.script.core import parser
import grass.script as grass

### kod z http://trac.osgeo.org/grass/browser/grass-addons/grass6/vector/v.surf.nnbathy/v.surf.nnbathy

def main():
	print options['input']
	### vypocetni region
	reg = grass.read_command("g.region", flags='p')    ### r.reclass.area.py  ??flags='p'
	kv = grass.parse_key_val(reg, sep=':')
	reg_N = float(kv['north'])
	reg_W = float(kv['west'])
	reg_S = float(kv['south'])
	reg_E = float(kv['east'])
	cols = float(kv['cols'])
	rows = float(kv['rows'])
	nsres = float(kv['nsres'])
	ewres = float(kv['ewres'])
	reg=(reg_N, reg_W, reg_S, reg_E)
	area=(reg_N-reg_S)*(reg_E-reg_W)

	if area == 0:
		grass.fatal(_("xy-locations are not supported"))
		grass.fatal(_("Need projected data with grids in meters"))
	
	if not options['file'] :
		TMPXYZ='input_xyz'
		XYZout='output_xyz'
				
		if int(options['layer']) == 0:
			LAYER=''
			COLUMN=''
		else:
			LAYER=int(options['layer'])
			if options['zcolumn']:
				COLUMN=options['zcolumn']
			else:
				grass.message('Name of z column required for 2D vector maps.')	
		TMP='output_4c'
		if options['kwhere']:
			grass.run_command("v.out.ascii",flags='r', overwrite=1, input=options['input'], output=TMP, format="point", separator="space",dp=15, where=options['kwhere'], layer=LAYER, columns=COLUMN)
		else:
			grass.run_command("v.out.ascii",flags='r', overwrite=1, input=options['input'], output=TMP, format="point", separator="space", dp=15, layer=LAYER, columns=COLUMN)
		if int(options['layer']) > 0:
			#http://stackoverflow.com/questions/2491222/how-to-rename-a-file-using-python
			#http://stackoverflow.com/questions/2499746/extracting-columns-from-text-file-using-perl-one-liner-similar-to-unix-cut
			#cut -f1,2,4 -d' ' "$TMPXYZ.cat" > "$TMPXYZ"			
			#os.rename('TMPXYZ','TMPXYZ.cat')
			#TMPXYZ.cat.split.(" ")[1,2,4]
			#os.remove(TMPXYZ.cat)
			fin=open(TMP, 'r')
			fout=open(TMPXYZ, 'w')
			for line in fin:
				parts = line.split(" ")
				#print parts[0]+' '+parts[1]+' '+parts[3]
				fout.write(parts[0]+' '+parts[1]+' '+parts[3])
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
	#grass.call('nnbathy, -i=TMPXYZ, -n=cols*rows, -o=XYZout')

	# Y in "r.stats -1gn" output is in descending order, thus -y must be in
	# MAX MIN order, not MIN MAX, for nnbathy not to produce a grid upside-down

	# convert the X,Y,Z nnbathy output into a GRASS ASCII grid, then import with r.in.ascii:
	
	# 1 create header
	TMP='output_grd'
	header=open(TMP,'w')
	header.write('north: '+str(nn_n)+'\n'+'south: '+str(nn_s)+'\n'+'west: '+str(nn_w)+'\n'+'east: '+str(nn_e)+'\n'+'rows: '+str(rows)+'\n'+'cols: '+str(cols)+'\n'+'type: '+type+'\n'+'null: '+null)
	
	# 2 do the conversion
	grass.message("Converting nnbathy output to GRASS raster ...")
	print 'cols='+str(cols)
	for i in xrange(1,10):
		pass
	
	# 3 import
	grass.run_command('r.in.ascii',input="$TMP.$PROG.output_grd", output="$OUTPUT", quiet=1)

	# store comand history in raster's metadata
	if options['input']:
		grass.run_command('r.support',map=options['output'],history="v.surf.nnbathy alg="+options['algorithm']+" input="+options['input']+" output="+options['output'])
	else:grass.run_command('r.support',map=options['output'],history="v.surf.nnbathy alg="+options['algorithm']+" input="+options['file']+" output="+options['output'])
	
	grass.run_command('r.support', map=options['output'], history="")
	grass.run_command('r.support', map=options['output'], history="nnbathy run syntax:")
	grass.run_command('r.support', map=options['output'], history="")
	grass.run_command('r.support', map=options['output'], history="nnbathy -W 0 -P alg=$ALG -n ${cols}x$rows )
	grass.run_command('r.support', map=options['output'], history="-x $nn_w $nn_e ")
	grass.run_command('r.support', map=options['output'], history="-y $nn_n $nn_s ")
	grass.run_command('r.support', map=options['output'], history="-i tmp_in > tmp_out")
	grass.run_command('r.support', map=options['output'], history="")

	grass.message("Done. "+options['output']+" created.")

	return 0

options, flags = parser()
main()




