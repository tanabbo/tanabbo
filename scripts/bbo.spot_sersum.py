#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_sersum
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Summary of bark beetle spots
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates summary of bark beetle spots.
#% keywords: bark beetle spot summary
#%end
#%option
#% key: yearfrom
#% type: integer
#% answer: 2007
#% description: First year
#% required: yes
#%end
#%option
#% key: yearto
#% type: integer
#% answer: 2011
#% description: Last year
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: spotsum
#% answer: ss_2007_2011
#% description: Output raster of bark beetle spot summary (spotsum)
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
    targetMapset = bboLib.forestMapset
    tmp0 = "tmp_bb_spot_sersum0"
    tmp1 = "tmp_bb_spot_sersum1"

    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])
    spotSum = bboLib.checkOutputRaster(options, "spotsum")

    if (yearTo < yearFrom):
        grass.fatal("YearFrom must be less or equal to YearTo")

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    y0 = yearTo
    while (yearFrom <= y0):
        prevSpot = bboLib.rasterYear(bboLib.spotPrefix, y0)
        if grass.find_file(prevSpot)['file']:
            grass.message("year: {0}".format(y0))
            grass.mapcalc("$spotSum = if(0 < $prevSpot, $y, null())", overwrite=True, spotSum=spotSum, prevSpot=prevSpot, y=y0)
            grass.run_command("r.null", map=spotSum, null=0, quiet=True)
            break;
        y0 = y0 - 1

    while (yearFrom < y0):
        y0 = y0 - 1
        prevSpot = bboLib.rasterYear(bboLib.spotPrefix, y0)
        if grass.find_file(prevSpot)['file']:
            grass.message("year: {0}".format(y0))
            grass.mapcalc("$tmp = if(0 < $prevSpot, $y, 0)", overwrite=True, tmp=tmp0, prevSpot=prevSpot, y=y0)
            grass.run_command("r.null", map=tmp0, null=0, quiet=True)
            grass.mapcalc("$tmp1 = if(0 < $tmp0, $tmp0, $spotSum)", overwrite=True, spotSum=spotSum, tmp0=tmp0, tmp1=tmp1)
            grass.mapcalc("$spotSum = $tmp1", overwrite=True, spotSum=spotSum, tmp1=tmp1)

    grass.run_command("r.null", map=spotSum, setnull=0, quiet=True)

    bboLib.deleteRaster(tmp1)
    bboLib.deleteRaster(tmp0)

    # finish calculation, restore settings
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
