#!/usr/bin/env python
import grass.script as grass
import time

# Set up iteration, points
pts = 1000
i = 50
inp = "v_test"+"%s" % pts
outp = "v_vystup"+"%s" % pts

# Generate vector input
grass.run_command("v.random", output=inp, n=pts, zmin=0.0, zmax=2000, column="value", column_type="double precision", overwrite=True)

# Testing
print("Executing. It may take some time, depends on the iteration (%d times)..." % i)
start = time.time()
for i in range(i):
    grass.run_command("v.surf.nnbathy.py", input=inp, output=outp, zcolumn='value', overwrite=True, quiet=True)
end = time.time()
run_time = (end-start)/i

print("==============================================")
print("v.surf.nnbathy.py run time: %f s (%d points)" % (run_time, pts))
print("==============================================")
