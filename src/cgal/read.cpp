#include <stdlib.h>

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

int read_points(const char *name, const char *field_name, const char *col, std::map<Point, Coord_type, K::Less_xy_2>& function_values,
    std::vector<K::Point_2>& OutPoints)
{
    int nrec, ctype = 0, npoints, field, with_z;
    double x, y, z;
    Point p;

    struct Map_info Map;    
    struct field_info *Fi;
    struct line_pnts *Points;
    struct line_cats *Cats;
    dbDriver *Driver;
    dbCatValArray cvarr;



    Vect_set_open_level(1);	/* without topology */
    if (Vect_open_old2(&Map, name, "", field_name) < 0)
	G_fatal_error(_("Unable to open vector map <%s>"), name);

    field = Vect_get_field_number(&Map, field_name);
    with_z = col == NULL && Vect_is_3d(&Map); /* read z-coordinates
                                                 only when column is
                                                 not defined */

    if (!col) {
        if (!with_z)
            G_important_message(_("Input vector map <%s> is 2D - using categories to interpolate"),
                                Vect_get_full_name(&Map));
        else
            G_important_message(_("Input vector map <%s> is 3D - using z-coordinates to interpolate"),
                                Vect_get_full_name(&Map));
    }

    if (col) {
        db_CatValArray_init(&cvarr);

        Fi = Vect_get_field(&Map, field);
        if (Fi == NULL)
            G_fatal_error(_("Database connection not defined for layer %s"), field_name);

        Driver = db_start_driver_open_database(Fi->driver, Fi->database);
        if (Driver == NULL)
            G_fatal_error(_("Unable to open database <%s> by driver <%s>"), Fi->database, Fi->driver);

        nrec = db_select_CatValArray(Driver, Fi->table, Fi->key, col, NULL, &cvarr);
        G_debug(3, "nrec = %d", nrec);

        ctype = cvarr.ctype;
        if (ctype != DB_C_TYPE_INT && ctype != DB_C_TYPE_DOUBLE)
            G_fatal_error(_("Column type not supported"));

        if (nrec < 0)
            G_fatal_error(_("Unable to select data from table"));

        G_verbose_message("One record selected from table %d records selected from table", nrec);

        db_close_database_shutdown_driver(Driver);
    }

    Points = Vect_new_line_struct();
    Cats = Vect_new_cats_struct();


    /* set constraints */
    Vect_set_constraint_type(&Map, GV_POINTS);
    if (field > 0)
        Vect_set_constraint_field(&Map, field);
    
    /* read points */
    npoints = 0;
    G_message(_("Reading points..."));
    while(TRUE) {
        double dval;
        if (Vect_read_next_line(&Map, Points, NULL) < 0)
            break;

        G_progress(npoints, 1e3);
        
        if (Points->n_points != 1) {
            G_warning(_("Invalid point skipped"));
            continue;
        }
        
        if (!with_z) {
            int cat, ival, ret;

            /* TODO: what to do with multiple cats */
            Vect_cat_get(Cats, field, &cat);
            if (cat < 0) /* skip features without category */
                continue;

            if (col) {
                if (ctype == DB_C_TYPE_INT) {
                    ret = db_CatValArray_get_value_int(&cvarr, cat, &ival);
                    dval = ival;
                }
                else {		/* DB_C_TYPE_DOUBLE */
                    ret = db_CatValArray_get_value_double(&cvarr, cat, &dval);
                }
            }
            else {
                dval = cat;
            }

            if (ret != DB_OK) {
                G_warning(_("No record for point (cat = %d)"), cat);
                continue;
            }
        }
        else
            dval = Points->z[0];

        x = Points->x[0];
        y = Points->y[0];
        
        p = Point(x,y);
        OutPoints.push_back(p);
        function_values.insert(std::make_pair(p, dval));       
        
        G_debug(3, "new point added: %f, %f, %f", x, y, z);
        //G_message("new point added: %f, %f, %f", x, y, z);
        npoints++;
    }
    G_progress(1, 1);

    if (col)
        db_CatValArray_free(&cvarr);

    Vect_set_release_support(&Map);
    Vect_close(&Map);
    Vect_destroy_line_struct(Points);

    G_debug(1, "read_points(): %d", npoints);
    G_message("%d point loaded", npoints);
    
    return npoints;
}
