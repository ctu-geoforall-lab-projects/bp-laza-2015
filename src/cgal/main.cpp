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

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangulation_2.h>
#include <CGAL/Delaunay_triangulation_2.h>

#include <CGAL/Interpolation_traits_2.h>
#include <CGAL/natural_neighbor_coordinates_2.h>
#include <CGAL/interpolation_functions.h>

extern "C" {
#include <grass/vector.h>
#include <grass/glocale.h>
#include <grass/raster.h>
#include <grass/gis.h>
}

#include "local_proto.h"

int main(int argc, char *argv[])
{
    char field;
    int npoints;
    char *column;

    int fd, maskfd;
    CELL *mask;
    DCELL *dcell;

    struct History history;    

    double ewres, nsres;

    struct GModule *module;
    
    struct {
        struct Option *input, *field, *output, *column;
    } opt;

    struct Map_info In;

    static struct Cell_head window;
    
    std::vector<K::Point_2> points;
    std::map<Point, Coord_type, K::Less_xy_2> function_values;

    G_gisinit(argv[0]);
    
    module = G_define_module();
    G_add_keyword(_("vector"));
    G_add_keyword(_("geometry"));
    G_add_keyword(_("interpolation"));
    module->description = _("Performs natural neighbor interpolation from an input vector map containing points.");

    opt.input = G_define_standard_option(G_OPT_V_INPUT);

    opt.field = G_define_standard_option(G_OPT_V_FIELD_ALL);

    opt.output = G_define_standard_option(G_OPT_V_OUTPUT);
    
    opt.column = G_define_standard_option(G_OPT_DB_COLUMN);
    opt.column->required = NO;
    opt.column->label = _("Name of attribute column with values to interpolate");
    opt.column->description = _("If not given and input is 2D vector map then category values are used. "
                               "If input is 3D vector map then z-coordinates are used.");
    opt.column->guisection = _("Values");

    if (G_parser(argc, argv)) {
        exit(EXIT_FAILURE);
    }

    /* open input map */
    Vect_open_old2(&In, opt.input->answer, "", opt.field->answer);
    Vect_set_error_handler_io(&In, NULL);

    field = Vect_get_field_number(&In, opt.field->answer);
    column = opt.column->answer;

    /* read points */
    npoints = read_points(opt.input->answer, opt.field->answer,
	       opt.column->answer, function_values, points);
    Vect_close(&In);

    /* get the window */
    G_get_window(&window);
    nsres = window.ns_res;
    ewres = window.ew_res;
    //G_message("cols %i, rows %i", window.cols, window.rows);

    /* allocate buffers, etc. */
    dcell = Rast_allocate_d_buf();

    if ((maskfd = Rast_maskfd()) >= 0)
        mask = Rast_allocate_c_buf();
    else
        mask = NULL;
    fd = Rast_open_new(opt.output->answer, DCELL_TYPE);

    /* perform NN interpolation */
    G_message(_("Computing..."));


    /* triangulation */
    Delaunay_triangulation T;
    typedef CGAL::Data_access< std::map<Point, Coord_type, K::Less_xy_2 > >
                                            Value_access;
    T.insert(points.begin(), points.end());


     //coordinate computation in grid
    double coor_x, coor_y;
    coor_x = window.west;
    coor_y = window.north;        

    for (int rows=0 ; rows<window.rows ; rows++) {
        G_percent(rows, window.rows, 2);

        if (mask)
            Rast_get_c_row(maskfd, mask, rows);

        coor_x = window.west;
        for (int cols=0 ; cols<window.cols ; cols++) {

            /* don't interpolate outside of the mask */
            if (mask && mask[cols] == 0) {
            Rast_set_d_null_value(&dcell[cols], 1);
            continue;}

            K::Point_2 p(coor_x,coor_y);
            std::vector< std::pair< Point, Coord_type > > coords;
            Coord_type norm = CGAL::natural_neighbor_coordinates_2(T, p,std::back_inserter(coords)).second;
            Coord_type res =  CGAL::linear_interpolation(coords.begin(), coords.end(), norm, Value_access(function_values));
            G_debug(5, "x: %f y: %f -> res: %f (row=%d; col=%d)",
                    coor_x, coor_y, res, rows, cols);
            coor_x += ewres;
            //std::cout << res << " ";
            dcell[cols] = (DCELL) res;
        }
        coor_y -= nsres;
        //std::cout << std::endl;

        Rast_put_d_row(fd, dcell);
    }
    G_percent(1, 1, 1);
    
    Rast_close(fd);

    /* writing history file */
    Rast_short_history(opt.output->answer, "raster", &history);
    Rast_command_history(&history);
    Rast_write_history(opt.output->answer, &history);


    G_done_msg("Raster map %s created.", opt.output->answer);
   
    exit(EXIT_SUCCESS);
}
