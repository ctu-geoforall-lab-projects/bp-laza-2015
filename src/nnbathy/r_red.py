#!/usr/bin/env python
####################################################################
# MODULE:     r.surf.nnbathy.py
#
# AUTHOR(S):  Adam Laza (mentor: Martin Landa)
#             (based on v.surf.nnbathy from GRASS 6)
####################################################################
from nnbathy import Nnbathy_raster

def main():
    obj = Nnbathy_raster(options)
    obj.compute()
    obj.create_output()

if __name__ == "__main__":
    options, flags = parser()
    main()
