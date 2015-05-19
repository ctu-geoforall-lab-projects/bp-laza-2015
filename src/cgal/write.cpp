#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangulation_2.h>
#include <CGAL/Delaunay_triangulation_2.h>

#include <CGAL/Interpolation_traits_2.h>
#include <CGAL/natural_neighbor_coordinates_2.h>
#include <CGAL/interpolation_functions.h>

extern "C" {
#include <grass/vector.h>
#include <grass/glocale.h>
}

#include "local_proto.h"

void write_raster()
{
  /* print to stdout */
}
