#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.solar_cday
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates potential solar irradiation
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates corrected solar irradiation.
#% keywords: solar irradiation
#%end
#%option
#% key: dayfrom
#% type: integer
#% options: 1-365
#% answer: 1
#% description: Day from (1 - 365)
#% required : yes
#%end
#%option
#% key: dayto
#% type: integer
#% options: 1-365
#% answer: 365
#% description: Day to (1 - 365)
#% required : yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib


def main():   
    dayFromStr = options["dayfrom"]
    dayToStr = options["dayto"]

    dayFrom = int(dayFromStr)
    dayTo = int(dayToStr)
    
    targetMapset = bboLib.solarMapset
    md_gsrFN = "md_gsr_1.txt"

    shpMapsetName =bboLib.shpMapset
    meteostationName = bboLib.setRasterMapset(bboLib.shpMeteostation, shpMapsetName)
    valFieldName = "val"

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))
    dayTo += 1

    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset = targetMapset)
   
    #bboLib.deleteDaySeries(solarPrefix)

    gsrSeries = bboLib.loadDataSeries(md_gsrFN)
    grass.message("corrections of solar irradiation")
    for iDay in range(dayFrom, dayTo):
        psrName = bboLib.rasterDay(bboLib.psrdayPrefix, iDay) + "@" + targetMapset
        if grass.find_file(psrName)["file"]:
            srName = bboLib.rasterDay(bboLib.srdayPrefix, iDay)
            srVal = bboLib.linearInterpolation(gsrSeries, iDay)
            if (srVal == None):
                grass.message("day: {0}   no corrections, missing meteo data".format(iDay))
                grass.mapcalc("$sr = $psr", overwrite=True, sr=srName, psr=psrName)
            else:
                grass.run_command("g.mapset", mapset = shpMapsetName)
                grass.run_command("v.what.rast", map=meteostationName, raster=psrName, column=valFieldName)
                grass.run_command("g.mapset", mapset = targetMapset)
                params = grass.parse_command("v.db.select", map=meteostationName, columns=valFieldName, flags="v", separator="=", quiet=True)
                psrVal = float(params["val"].strip())
                k = srVal / psrVal
                grass.message("day: {0}   coeficient: {1}".format(iDay, k))
                grass.mapcalc("$sr = $k * $psr", overwrite=True, sr=srName, k=k, psr=psrName)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
