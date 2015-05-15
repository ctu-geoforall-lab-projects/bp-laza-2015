#!/usr/bin/env python
import grass.script as grass
import time

# Set up iteration, points
pts = 1000
i = 50
inp = "r_test"+"%s" % pts
outp = "r_vystup"+"%s" % pts

# Generate raster map
grass.run_command("r.random", raster_output=inp, n=pts, input="raster_map", overwrite=True)

# Testing
print("Executing. It may take some time, depends on the iteration (%d times)..." % i)
start = time.time()
for i in range(i):
    grass.run_command("r.surf.nnbathy.py", input=inp, out=outp, overwrite=True, quiet=True)
end = time.time()
run_time = (end-start)/i

print("==============================================")
print("r.surf.nnbathy.py run time: %f s (%d points)" % (run_time, pts))
print("==============================================")
