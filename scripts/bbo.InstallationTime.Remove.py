#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.drought_clean
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Clean drought database
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Removes drought index files
#% keywords: clean drought index
#% keywords:TANABBO
#%end
#%option
#% key: dayfrom
#% type: integer
#% options: 1-365
#% answer: 100
#% description: Day from (1 - 365)
#% required : yes
#%end
#%option
#% key: dayto
#% type: integer
#% options: 1-365
#% answer: 115
#% description: Day to (1 - 365)
#% required : yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
import bboLib
import bboDroughtLib


def main():
    targetMapset = bboLib.phenipsMapset

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))

    def RemoveForecast(dayFrom, dayTo, targetMapset, forecastDDPrefix):
      # Use the targetMapset parameter instead of directly referring to bboLib
      userMapset = grass.gisenv()["MAPSET"]
      if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

      for iDay in range(dayFrom, dayTo + 1):
        grass.message("clean day {0}".format(iDay))
        # Use the forecastDDPrefix parameter instead of directly referring to bboLib
        bboLib.deleteRaster(bboLib.rasterDay(forecastDDPrefix, iDay))

      if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)

    RemoveForecast(dayFrom, dayTo, bboLib.infestationMapset, bboLib.phenipsFORECASTDDPrefix)
    RemoveForecast(dayFrom, dayTo, bboLib.infestationMapset, bboLib.ForecastMeanPrefix)
    RemoveForecast(dayFrom, dayTo, bboLib.infestationMapset, bboLib.ForecastMaxPrefix)
    RemoveForecast(dayFrom, dayTo, bboLib.atMapset, bboLib.ForecastMeanPrefix)
    RemoveForecast(dayFrom, dayTo, bboLib.atMapset, bboLib.ForecastMaxPrefix)
    bboLib.deleteRaster("_forecast_swarming_trap_installation01")
    bboLib.deleteRaster("_real_swarming01")

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)

    grass.message(_("Done."))    



if __name__ == "__main__":
    options, flags = grass.parser()
    main()
