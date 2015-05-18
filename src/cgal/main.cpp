/***************************************************************
 *
 * MODULE:       v.surf.nn
 *
 * AUTHOR(S):    Adam Laza
 *
 * PURPOSE:      Performs natural neighbor interpolation using CGAL library
 *
 * COPYRIGHT:    (C) 2015 by Adam Laza, and the GRASS Development Team
 *
 *               This program is free software under the GNU General
 *               Public License (>=v2). Read the file COPYING that
 *               comes with GRASS for details.
 *
 ****************************************************************/

#include <cstdlib>
#include <vector>

extern "C" {
#include <grass/vector.h>
#include <grass/glocale.h>
}

#include "local_proto.h"

int main(int argc, char *argv[])
{
    int field;
    int npoints;

    struct GModule *module;
    
    struct {
        struct Option *input, *field, *output;
    } opt;

    struct Map_info In;

    static struct Cell_head window;
    
    std::vector<Point> points;
    
    G_gisinit(argv[0]);
    
    module = G_define_module();
    G_add_keyword(_("vector"));
    G_add_keyword(_("geometry"));
    G_add_keyword(_("interpolation"));
    module->description = _("Performs natural neighbor interpolation from an input vector map containing points.");

    opt.input = G_define_standard_option(G_OPT_V_INPUT);

    opt.field = G_define_standard_option(G_OPT_V_FIELD_ALL);

    // opt.output = G_define_standard_option(G_OPT_V_OUTPUT);

    if (G_parser(argc, argv)) {
        exit(EXIT_FAILURE);
    }

    /* open input map */
    Vect_open_old2(&In, opt.input->answer, "", opt.field->answer);
    Vect_set_error_handler_io(&In, NULL);

    field = Vect_get_field_number(&In, opt.field->answer);

    /* read points */
    npoints = read_points(&In, field, points);
    Vect_close(&In);

    /* get the window */
    G_get_window(&window);
    G_message("Rows: %i, Cols: %i, nsres: %.2f, weres: %.2f", window.rows, 
    window.cols, window.ns_res, window.ew_res);
    nsres = window.ns_res;
    ewres = window.ew_res;


    /* perform NN interpolation */
    G_message(_("Computing..."));

    Delaunay_triangulation T;
    std::map<Point, Coord_type, K::Less_xy_2> function_values;
    typedef CGAL::Data_access< std::map<Point, Coord_type, K::Less_xy_2 > >
                                            Value_access;

    T.insert(points.begin(), points.end());

    //Hodnoty k interpolaci zatim nahodne vygenerovane
    std::vector<double> values;    
    for (int i=0; i<npoints; i++){
        double value=rand() % 100 + 1;
        values.push_back(value);}

    //Problem s parovanim
    function_values.insert(std::make_pair((points.begin(),points.end()),(values.begin(),values.end())));


     //coordinate computation in grid
    /*
    double coor_x, coor_y;
    coor_x = window.west;
    coor_y = window.north;        

    for (int rows=0 ; rows<window.rows ; rows++)
        for (int cols=0 ; cols<window.cols ; cols++){
            K::Point_2 p(coor_x,coor_y);
            std::vector< std::pair< Point, Coord_type > > coords;
            Coord_type norm = CGAL::natural_neighbor_coordinates_2(T, p,std::back_inserter(coords)).second;
            Coord_type res =  CGAL::linear_interpolation(coords.begin(), coords.end(), norm, Value_access(function_values));

            coor_x += ewres;
            coor_y -= nsres;
            } 

    */
    /* create output */
    /* TODO */

    exit(EXIT_SUCCESS);
}
