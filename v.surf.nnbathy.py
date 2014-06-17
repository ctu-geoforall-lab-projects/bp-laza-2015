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
	print options
	print options['input']
### vypocetni region
	reg = grass.read_command("g.region", flags='p')    ### r.reclass.area.py  ??flags='p'
	kv = grass.parse_key_val(reg, sep=':')
	reg_N = float(kv['north'])
	reg_W = float(kv['west'])
	reg_S = float(kv['south'])
	reg_E = float(kv['east'])
	reg=(reg_N, reg_W, reg_S, reg_E)
	area=(reg_N-reg_S)*(reg_E-reg_W)

	if area == 0:
		grass.fatal(_("xy-locations are not supported"))
		grass.fatal(_("Need projected data with grids in meters"))
	if not file :
		TMPXYZ='input_xyz'
		
		if int(options['layer']) == 0:
			LAYER=''
			COLUMN=''
		else:
			LAYER=int(options['layer'])
			if options['zcolumn']:
				COLUMN=options['zcolumn']
			else:
				g.message('Name of z column required for 2D vector maps.')

		#if options['kwhere']:
		#	v.out.ascii -r input=options['input'] output=TMPXYZ format=point fs=space dp=15 where=options['kwhere'] LAYER COLUMN
		#else:
		#	v.out.ascii -r input=options['input'] output=TMPXYZ format=point fs=space dp=15 LAYER COLUMN

		if int(options['layer']) > 0:
			#http://stackoverflow.com/questions/2491222/how-to-rename-a-file-using-python
			#http://stackoverflow.com/questions/2499746/extracting-columns-from-text-file-using-perl-one-liner-similar-to-unix-cut
			#cut -f1,2,4 -d' ' "$TMPXYZ.cat" > "$TMPXYZ"			
			#os.rename('TMPXYZ','TMPXYZ.cat')
			#TMPXYZ.cat.split.(" ")[1,2,4]
			#os.remove(TMPXYZ.cat)
			for line in open("TMPXYZ"):
				parts = line.split(" ")
    			print " ".join(parts[0,1,3])
	else:
		TMPXYZ=options['file']
	print TMPXYZ

	# set the working region for nnbathy (it's cell-center oriented)
	
	return 0

options, flags = parser()
main()




