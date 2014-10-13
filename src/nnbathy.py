class nnbathy:
    def __init__(self, name):
        self.name = name
        self.temp = grass.tempfile
        # ...
    
    def __del__(self):
        # cleanup
        
    def compute():
        # volat nnbathy
        pass

    def create_output():
        # vytvori vystupni rastr
        pass

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


class nnbathy_raster(nnbathy):
    def __init__(self, name):
         nnbathy.__init__(name)
        self._load()

    def _load():
        # nacte vstupni raster
        # r.out.ascii input=self.name
        self.region()
        print self.null
        pass

class nnbathy_vector:
    def __init__(self, name):
        self._load()

    def _load():
        # nacte vstupni vektor
        pass

class nnbathy_file:
    def __init__(self, name):
        self._load()

    def _load():
        # nacte vstupni soubor
        pass
            

    
