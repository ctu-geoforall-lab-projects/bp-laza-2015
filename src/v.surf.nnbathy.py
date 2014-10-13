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
#
# NOTES:
#
# 1. Requires nnbathy executable v 1.75 or later. Follow the instruction in
#    html manual page to obtain it.
#
# 2. When creating the input raster map, make sure it's extents cover
#    your whole region of interest, the cells you wish to interplate on are
#    NULL, and the resolution is correct. Same as most GRASS raster modules
#    this one is region sensitive too.

#%Module
#% description: Interpolates a raster map using the nnbathy natural neighbor interpolation program.
#% keywords: vector
#% keywords: surface
#% keywords: interpolation
#% keywords: natural
#% keywords: neighbor
#%end
#%option G_OPT_V_INPUT
#% key: input
#% type: string
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
#% key: output
#% description: Name of output raster map
#%end
#%option G_OPT_DB_COLUMN
#% key: zcolumn
#% description: Name of the attribute column with values to be used for approximation (if layer>0)
#% guisection: Settings
#%end
#%option G_OPT_DB_WHERE
#% key: kwhere
#% type: string
#% label: WHERE conditions of SQL query statement without 'where' keyword
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

# from nnbathy import nnbathy_vector, nnbathy_file

TMP = None
TMPcat = None
TMPXYZ = None
XYZout = None

# def main():
#     if vector: 
#         obj = nnbathy_vector(nazev vektor)
#     else:
#         obj = nnbathy_file(cesta k souboru)

#     obj.compute()
#     obj.create_output()

def main():
    def region():
        # set the region
        # TODO globalni promenne?
        global area, ALG, nn_n, nn_s, nn_w, nn_e, null, ctype, cols, rows
        reg = grass.read_command("g.region", flags='p')
        kv = grass.parse_key_val(reg, sep=':')
        reg_N = float(kv['north'])
        reg_W = float(kv['west'])
        reg_S = float(kv['south'])
        reg_E = float(kv['east'])
        cols = int(kv['cols'])
        rows = int(kv['rows'])
        nsres = float(kv['nsres'])
        ewres = float(kv['ewres'])
        reg = (reg_N, reg_W, reg_S, reg_E)
        area = (reg_N-reg_S)*(reg_E-reg_W)
        ALG = options['algorithm']

        # set the working region for nnbathy (it's cell-center oriented)
        nn_n = reg_N - nsres/2
        nn_s = reg_S + nsres/2
        nn_w = reg_W + ewres/2
        nn_e = reg_E - ewres/2
        null = "NaN"
        ctype = "double"

    def initial_controls():
        # setup temporary files
        global TMP, TMPcat, TMPXYZ, XYZout
        TMP = grass.tempfile()
        TMPcat = grass.tempfile()
        TMPXYZ = grass.tempfile()
        XYZout = grass.tempfile()

        if (TMPcat or TMPXYZ or XYZout or TMP) is None:
            grass.fatal("Unable to create temporary files.")

        # other controls
        if not grass.find_program('nnbathy'):
            grass.fatal('nnbathy is not available')

        if (options['input'] and options['file']):
            grass.message("Please specify either the 'input' or 'file' option, not both.")

        if not(options['input'] or options['file']):
            grass.message("Please specify either the 'input' or 'file' option.")

        if (options['file'] and os.path.isfile(options['file'])):
            grass.message("File "+options['file']+" does not exist.")

        if area == 0:
            grass.fatal(_("xy-locations are not supported"))
            grass.fatal(_("Need projected data with grids in meters"))

        if not options['file']:
            if int(options['layer']) == 0:
                LAYER = ''
                COLUMN = ''
            else:
                LAYER = int(options['layer'])
                if options['zcolumn']:
                    COLUMN = options['zcolumn']
                else:
                    grass.message('Name of z column required for 2D vector maps.')

            if options['kwhere']:
                grass.run_command("v.out.ascii", flags='r', overwrite=1, input=options['input'], output=TMPcat,
                                  format="point", separator="space", dp=15, where=options['kwhere'], layer=LAYER, columns=COLUMN)
            else:
                grass.run_command("v.out.ascii", flags='r', overwrite=1, input=options['input'], output=TMPcat,
                                  format="point", separator="space", dp=15, layer=LAYER, columns=COLUMN)

            if int(options['layer']) > 0:
                fin = open(TMPcat, 'r')
                fout = open(TMPXYZ, 'w')
                # TODO: try block... ???? duvod? co vlastne zkousim?
                try:
                    for line in fin:
                        parts = line.split(" ")
                        fout.write(parts[0]+' '+parts[1]+' '+parts[3])
                except:
                    grass.message("Invalid input!")
                fin.close()
                fout.close()
            else:
                # TODO: chyba ?
                grass.message("Z coordinates are used.")
        else:
            TMPXYZ = options['file']

    def compute():
        grass.message('"nnbathy" is performing the interpolation now. This may take some time...')
        grass.verbose("Once it completes an 'All done.' message will be printed.")

        #nnbathy calling
        fsock = open(XYZout, 'w')
        #TODO zkontrolovat zarovnani
        grass.call(['nnbathy',
                    '-W', '%d' % 0,
                    '-i', '%s' % TMPXYZ,
                    '-x', '%d' % nn_w, '%d' % nn_e,
                    '-y', '%d' % nn_n, '%d' % nn_s,
                    '-P', '%s' % ALG,
                    '-n', '%dx%d' % (cols, rows)],
                   stdout=fsock)
        fsock.close()

        #TODO
        # Y in "r.stats -1gn" output is in descending order, thus -y must be in
        # MAX MIN order, not MIN MAX, for nnbathy not to produce a grid upside-down

    def convert():
        # convert the X,Y,Z nnbathy output into a GRASS ASCII grid, then import with r.in.ascii
        # 1 create header
        header = open(TMP, 'w')
        header.write('north: %s\nsouth: %s\neast: %s\nwest: %s\nrows: %s\ncols: %s\ntype: %s\nnull: %s\n\n' % \
                         (nn_n, nn_s, nn_e,  nn_w, rows, cols, ctype, null))
        header.close()

        # 2 do the conversion
        grass.message("Converting nnbathy output to GRASS raster ...")
        fin = open(XYZout, 'r')
        fout = open(TMP, 'a')
        cur_col = 1
        for line in fin:
            parts = line.split(" ")
            if cur_col == cols:
                cur_col = 0
                fout.write(str(parts[2]))
            else:
                fout.write(str(parts[2]).rstrip('\n')+' ')
            cur_col += 1
        fin.close()
        fout.close()

    def import_to_raster():
        grass.run_command('r.in.ascii', input=TMP, output=options['output'], quiet=True)

        # store comand history in raster's metadata
        # TODO formatovani
        if options['input']:
            grass.run_command('r.support', map=options['output'],
                              history="v.surf.nnbathy alg=%s input=%s output=%s" % \
                                  (options['algorithm'], options['input'], options['output']))
        else:
            grass.run_command('r.support', map=options['output'],
                              history="v.surf.nnbathy alg=%s input=%s output=%s" % \
                                  (options['algorithm'], options['file'], options['output']))

        grass.run_command('r.support', map=options['output'],
                          history="\nnnbathy run syntax:\nnbathy -W %d -i %s -x '%d %d' -y '%d %d' -P %s -n %dx%d" % \
                              (0, TMPXYZ, nn_w, nn_e, nn_n, nn_s, ALG, cols,rows))
        grass.message("Done. Raster map <%s> created." % options['output'])

    region()
    initial_controls()
    compute()
    convert()
    import_to_raster()
        # TODO UPOZORNeNi: nevhodny typ pole, pouzivam cele cislo

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
