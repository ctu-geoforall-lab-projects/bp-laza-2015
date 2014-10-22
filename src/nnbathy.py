class nnbathy:
    def __init__(self, name):
        self.name = name
        # self.temp = grass.tempfile
        self.TMPXYZ = grass.tempfile()
        self.XYZout = grass.tempfile()
        self.TMP = grass.tempfile()	
        self.TMPcat = grass.tempfile()


    def region(self):
        reg = grass.read_command("g.region", flags='p')
        kv = grass.parse_key_val(reg, sep=':')
        reg_N = float(kv['north'])
        reg_W = float(kv['west'])
        reg_S = float(kv['south'])
        reg_E = float(kv['east'])
        self.cols = int(kv['cols'])
        self.rows = int(kv['rows'])
        nsres = float(kv['nsres'])
        ewres = float(kv['ewres'])
        reg = (reg_N, reg_W, reg_S, reg_E)
        self.area = (reg_N-reg_S)*(reg_E-reg_W)
        self.ALG = options['algorithm']

        # set the working region for nnbathy (it's cell-center oriented)
        self.nn_n = reg_N - nsres/2
        self.nn_s = reg_S + nsres/2
        self.nn_w = reg_W + ewres/2
        self.nn_e = reg_E - ewres/2
        self.null = "NaN"
        self.ctype = "double"
    
    def compute(self):
        # volat nnbathy
        grass.message('"nnbathy" is performing the interpolation now. This may take some time...')
        grass.verbose("Once it completes an 'All done.' message will be printed.")

        #nnbathy calling
        fsock = open(self.XYZout, 'w')
        #TODO zkontrolovat zarovnani
        grass.call(['nnbathy',
                    '-W', '%d' % 0,
                    '-i', '%s' % self.TMPXYZ,
                    '-x', '%d' % self.nn_w, '%d' % self.nn_e,
                    '-y', '%d' % self.nn_n, '%d' % self.nn_s,
                    '-P', '%s' % self.ALG,
                    '-n', '%dx%d' % (self.cols, self.rows)],
                   stdout=fsock)
        fsock.close()


    def create_output(self):
        # vytvori vystupni rastr
        # convert the X,Y,Z nnbathy output into a GRASS ASCII grid, then import with r.in.ascii
        # 1 create header
        header = open(self.TMP, 'w')
        header.write('north: %s\nsouth: %s\neast: %s\nwest: %s\nrows: %s\ncols: %s\ntype: %s\nnull: %s\n\n' % \
                         (self.nn_n, self.nn_s, self.nn_e,  self.nn_w, self.rows, self.cols, self.ctype, self.null))
        header.close()

        # 2 do the conversion
        grass.message("Converting nnbathy output to GRASS raster ...")
        fin = open(self.XYZout, 'r')
        fout = open(self.TMP, 'a')
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

        # 3 import to raster
        grass.run_command('r.in.ascii', input=self.TMP, output=options['output'], quiet=True)
        pass

    def __del__(self):
        # cleanup
        if self.TMP:
            os.remove(self.TMP)
        if self.TMPXYZ:
            os.remove(self.TMPXYZ)
        if self.XYZout:
            os.remove(self.XYZout)    
        if self.TMPcat:
            os.remove(self.TMPcat)    

class nnbathy_raster(nnbathy):
    #__init__(self, name):
    def __init__(name):
        self._load()

    def _load(self):
        # nacte vstupni raster
        # r.out.ascii input=self.name
        self.region()
        grass.run_command('r.stats', flags='1gn', input=self.name, output=self.TMPXYZ, quiet=True)
        # print self.null

class nnbathy_vector(nnbathy):
    def __init__(self, name):
        self._load()

    def _load(self):
        # nacte vstupni vektor
        self.region()

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
            grass.run_command("v.out.ascii", flags='r', overwrite=1, input=options['input'], output=TMPcat, \
                              format="point", separator="space", dp=15, where=options['kwhere'], layer=LAYER, columns=COLUMN)
        else:
            grass.run_command("v.out.ascii", flags='r', overwrite=1, input=options['input'], output=TMPcat, \
                              format="point", separator="space", dp=15, layer=LAYER, columns=COLUMN)

        if int(options['layer']) > 0:
            fin = open(TMPcat, 'r')
            fout = open(TMPXYZ, 'w')
            try:
                for line in fin:
                    parts = line.split(" ")
                    fout.write(parts[0]+' '+parts[1]+' '+parts[3])
            except StandardError, e:
                grass.fatal_error("Invalid input: %s" % e)
            fin.close()
            fout.close()
        else:
            # TODO: chyba ?
            grass.message("Z coordinates are used.")


class nnbathy_file:
    def __init__(self, name):
        self._load()

    def _load(self):
        # nacte vstupni soubor
        self.TMPXYZ=self.name