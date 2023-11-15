#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.ie_bbspot
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
#%option G_OPT_R_INPUT
#% key: s50mask
#% answer: s50Mask@forest
#% description: Spruce forest mask (s50mask)
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
    sourceMapset = "permanent"
    sourceSpotPrefix = "ohniska_"
    targetMapset = "forest"
    tmpRaster = "tmp_ie_spotsum"

    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])
    s50Mask = bboLib.checkInputRaster(options, "s50mask")

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    y0 = yearFrom
    while (y0 <= yearTo):
        srcSpot = bboLib.rasterYear(sourceSpotPrefix, y0) + "@" + sourceMapset
        tgtSpot = bboLib.rasterYear(bboLib.spotPrefix, y0)
        bboLib.deleteRaster(tgtSpot)
        if grass.find_file(srcSpot)['file']:
            grass.message(str.format("copy {0} {1}", srcSpot, tgtSpot))
            grass.mapcalc("$tgt = $src * $s50mask", overwrite=True, tgt=tgtSpot, src=srcSpot, s50mask=s50Mask)
            grass.run_command("r.null", map=tgtSpot, null=0, quiet=True) 
        y0 = y0 + 1

    y0 = yearFrom
    while (y0 <= yearTo):
        prevSpot = bboLib.rasterYear(bboLib.spotPrefix, y0)
        if grass.find_file(prevSpot + "@" + targetMapset)['file']:
            break;
        y0 = y0 + 1

    while (y0 < yearTo):
        y1 = y0 + 1
        while (y1 <= yearTo):
            actSpot = bboLib.rasterYear(bboLib.spotPrefix, y1)
            if grass.find_file(actSpot + "@" + targetMapset)['file']:
                break;
            y1 = y1 + 1
        if (y1 <= yearTo):
            grass.message(str.format("update {0} {1}", prevSpot, actSpot))
            grass.mapcalc("$tmp = $r1 + $r2", tmp=tmpRaster, r1=prevSpot, r2=actSpot, overwrite=True)
            grass.mapcalc("$r2 = if(0 < $tmp, 1, 0)", tmp=tmpRaster, r2=actSpot, overwrite=True)
            y0 = y1
            prevSpot = actSpot
        else:
            y0 = yearTo

    y0 = yearFrom
    while (y0 <= yearTo):
        prevSpot = bboLib.rasterYear(bboLib.spotPrefix, y0)
        if grass.find_file(prevSpot + "@" + targetMapset)['file']:
            grass.message(str.format("setnull {0}", prevSpot))
            grass.run_command("r.null", map=prevSpot, setnull=0, quiet=True)
        y0 = y0 + 1

    bboLib.deleteRaster(tmpRaster)

    # finish calculation, restore settings
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done.")) 



if __name__ == "__main__":
    options, flags = grass.parser()
    main()
