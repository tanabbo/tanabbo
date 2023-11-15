#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.solar_day
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates potential solar irradiation
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates potential solar irradiation.
#% keywords: solar irradiation
#%end
#%option G_OPT_R_INPUT
#% key: dem
#% description: Name of raster to use as DEM
#% answer: dem@dem
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: slope
#% description: Name of raster to use as slope
#% answer: slope@dem
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: aspect
#% description: Name of raster to use as aspect
#% answer: aspect@dem
#% required: yes
#%end
#%option
#% key: latitudedeg
#% type: double
#% answer: 48.5
#% gisprompt: -90.0-90.0
#% description: Latitude of region in decimal degrees (-90.0 - 90.0)
#% required: yes
#%end
#%option
#% key: longitudedeg
#% type: double
#% answer: 19.0
#% gisprompt: -180.0-180.0
#% description: Longitude of region in decimal degrees (-180.0 - 180.0)
#% required: yes
#%end
#%option
#% key: dayfrom
#% type: integer
#% options: 1-365
#% answer: 1
#% description: Day from (1 - 365)
#% required: yes
#%end
#%option
#% key: dayto
#% type: integer
#% options: 1-365
#% answer: 365
#% description: Day to (1 - 365)
#% required: yes
#%end
#%option
#% key: calcstep
#% type: double
#% answer: 1.0
#% gisprompt: 0-24
#% description: Calculation step in hours
#% required: yes
#%end
#%flag
#% key: c
#% description: Clean mapset
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboSolarLib


def main():
    demName = bboLib.checkInputRaster(options, "dem")
    slopeName = bboLib.checkInputRaster(options, "slope")
    aspectName = bboLib.checkInputRaster(options, "aspect")
    latitudeDeg = options["latitudedeg"]
    longitudeDeg = options["longitudedeg"]
    dayFromStr = options["dayfrom"]
    dayToStr = options["dayto"]
    calcStepStr = options["calcstep"]
    cleanMapset = flags["c"]

    dayFrom = int(dayFromStr)
    dayTo = int(dayToStr)
    calcStep = float(calcStepStr)
    
    targetMapset = bboLib.solarMapset
    tmpLongitude = "tmp_longitude"
    tmpLatitude = "tmp_latitude"

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))
    if calcStep <= 0.0:
        grass.fatal(_("Parameter <calcstep> must be greater than 0"))
    if 24.0 <= calcStep:
        grass.fatal(_("Parameter <calcstep> must be less than 24"))

    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset = targetMapset)

    grass.mapcalc("$output = $value", overwrite=True, output=tmpLatitude, value=latitudeDeg)
    grass.mapcalc("$output = $value", overwrite=True, output=tmpLongitude, value=longitudeDeg)
    
    if (cleanMapset):
        bboLib.deleteDaySeries(bboSolarLib.psrdayPrefix)

    dayTo = dayTo + 1
    for iDay in range(dayFrom, dayTo):
        grass.message("potential solar irradiation day {0}".format(iDay))
        psrName = bboLib.rasterDay(bboLib.psrdayPrefix, iDay)
        grass.run_command("r.sun", elevation=demName, aspect=aspectName, slope=slopeName, lat=tmpLatitude, long=tmpLongitude,
                           glob_rad=psrName, day=iDay, step=calcStep, overwrite=True)

    bboLib.deleteRaster(tmpLatitude)
    bboLib.deleteRaster(tmpLongitude)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
