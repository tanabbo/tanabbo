#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_expdst
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Export spot distances
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Export bark beetle spot distances.
#% keywords: bark beetle spot distance export
#%end
#%option
#% key: yearfrom
#% type: integer
#% answer: 1980
#% description: First year
#% required: yes
#%end
#%option
#% key: yearto
#% type: integer
#% answer: 2015
#% description: Last year
#% required: yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib

def main():
    targetMapset = "forest"

    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])

    if (yearTo < yearFrom):
        grass.fatal("YearFrom must be less or equal to YearTo")

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.message("year e_count e_min e_max e_avg e_std f_count f_min f_max f_avg f_std e_im f_im s_im")
    ec0 = 0.0
    fc0 = 0.0

    y0 = yearFrom
    while (y0 <= yearTo):
        rasterName = bboLib.rasterYear(bboLib.fdstPrefix, y0)
        if grass.find_file(rasterName)['file']:
            fdst = grass.parse_command("r.univar", flags="g", map=rasterName, quiet=True)
        else:
            fdst = {}
        rasterName = bboLib.rasterYear(bboLib.edstPrefix, y0)
        if grass.find_file(rasterName)['file']:
            edst = grass.parse_command("r.univar", flags="g", map=rasterName, quiet=True)
        else:
            edst = {}
        if (0 < len(fdst) and 0 < len(edst)):
            ec1 = float(edst["n"])
            fc1 = float(fdst["n"])
            #if (0.0 < ec0):
            #    e_im = ec1 / ec0
            #else:
            #    e_im = 1.0
            #if (0.0 < fc0):
            #    f_im = fc1 / fc0
            #else:
            #    f_im = 1.0
            if (0.0 < (ec0 + fc0)):
                e_im = ec1 / (ec0 + fc0)
                f_im = fc1 / (ec0 + fc0)
                s_im = (ec1 + fc1) / (ec0 + fc0)
            else:
                e_im = 0.0
                f_im = 0.0
                s_im = 0.0
            ec0 = ec1
            fc0 = fc1
            grass.message("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11} {12} {13}".format(y0, edst["n"], edst["min"], edst["max"], edst["mean"], edst["stddev"], fdst["n"], fdst["min"], fdst["max"], fdst["mean"], fdst["stddev"], e_im, f_im, s_im))
        y0 = y0 + 1

    # finish calculation, restore settings
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
