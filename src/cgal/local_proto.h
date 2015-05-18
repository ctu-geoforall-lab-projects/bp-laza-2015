#ifndef __LOCAL_PROTO_H__

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangulation_2.h>
#include <CGAL/Delaunay_triangulation_2.h>

#include <CGAL/Interpolation_traits_2.h>
#include <CGAL/natural_neighbor_coordinates_2.h>
#include <CGAL/interpolation_functions.h>

typedef CGAL::Exact_predicates_inexact_constructions_kernel K;
typedef CGAL::Triangulation_2<K>      Triangulation;
typedef Triangulation::Point          Point;

typedef CGAL::Delaunay_triangulation_2<K>             Delaunay_triangulation;
typedef CGAL::Interpolation_traits_2<K>               Traits;
typedef K::FT                                         Coord_type;
typedef K::Point_2                                    Point;

/* read.cpp */
int read_points(struct Map_info *, int, std::vector<Point>&);

/* write.cpp */
void write_lines();
#endif
