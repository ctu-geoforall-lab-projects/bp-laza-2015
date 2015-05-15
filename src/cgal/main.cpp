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
    
    /* create output */
    /* TODO */

    /* read points */
    npoints = read_points(&In, field, points);
    Vect_close(&In);
    
    /* perform NN interpolation */
    G_message(_("Computing..."));

    exit(EXIT_SUCCESS);
}
