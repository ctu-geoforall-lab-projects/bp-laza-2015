MODULE_TOPDIR = /home/adam/src/grass_trunk/dist.x86_64-unknown-linux-gnu

PGM = v.surf.nn

LIBES = $(GPROJLIB) $(VECTORLIB) $(GISLIB) $(RASTERLIB)
DEPENDENCIES = $(GPROJDEP) $(VECTORDEP) $(GISDEP) $(RASTERDEP)
EXTRA_INC = $(VECT_INC) $(PROJINC)
EXTRA_CFLAGS = $(VECT_CFLAGS)

include $(MODULE_TOPDIR)/include/Make/Module.make

EXTRA_CFLAGS = -frounding-math
EXTRA_LDFLAGS = -lCGAL -lgmp
LINK = $(CXX)

ifneq ($(strip $(CXX)),)
default: cmd
endif
