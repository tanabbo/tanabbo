#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.risk_clean
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Clean drought risk database
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Prediction of first swarming and trap installation time
#% keywords: clean drought risk
#% keywords:TANABBO
#%end
#%option G_OPT_R_INPUT
#% key: dem
#% description: DEM raster
#% answer: dem@dem
#% required: yes
#%end
#%option G_OPT_V_INPUT
#% key: meteo
#% description: Meteo station layer
#% answer: meteo_station@shp
#% required: yes
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
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPhenipsLib

def main():   
    targetMapset = bboLib.atMapset
    solarMapset = bboLib.solarMapset
    demName = "dem@dem"

    shpMapset = bboLib.shpMapset
    meteostationName = bboLib.shpMeteostation + "@" + bboLib.shpMapset
    valFieldName = bboLib.shpMeteostationValField

    demName = bboLib.checkInputRaster(options, "dem")
    meteostationName = options["meteo"]

    tgradSeries = bboLib.loadDataSeries("tgrad_std_forecast.txt")
    tmeanSeries = bboLib.loadDataSeries("md_tmean_forecast.txt")
    tmaxSeries = bboLib.loadDataSeries("md_tmax_forecast.txt")
    srSeries = bboLib.loadDataSeries("md_gsr_forecast.txt")

    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # meteo station parameters
    grass.run_command("g.mapset", mapset=shpMapset)
   # grass.run_command("v.what.rast", map=meteostationName, raster=demName, column=valFieldName)
    grass.run_command("g.mapset", mapset=targetMapset)
  #  params = grass.parse_command("v.db.select", map=meteostationName, columns=valFieldName, flags="v", separator="=", quiet=True)
    msElev = 1050 #float(params["val"].strip())

    dayTo += 1
    for iDay in range(dayFrom, dayTo):
        grass.message("forecast air temperature day {0}".format(iDay))
        srName = bboLib.rasterDayMapset(bboLib.srdayPrefix, iDay, solarMapset)

        meanName = bboLib.rasterDay(bboLib.ForecastMeanPrefix, iDay)
        maxName = bboLib.rasterDay(bboLib.ForecastMaxPrefix,  iDay)
        bboLib.deleteRaster(meanName)
        bboLib.deleteRaster(maxName)

        dt = bboLib.linearInterpolation(tmeanSeries, iDay)
        dc = bboLib.linearInterpolation(tgradSeries, iDay)
        if (dt != None and dc != None):
            grass.mapcalc("$output = $dc * ($dem - $mselev) + $dt", 
                          output=meanName,
                          dem=demName, dc=dc, dt=dt, mselev=msElev, overwrite=True)
        
        dm = bboLib.linearInterpolation(tmaxSeries, iDay)
        msSR = bboLib.linearInterpolation(srSeries, iDay)
        if (dm != None and msSR != None):
            grass.mapcalc("$output = $dc * ($dem - $mselev) * ($sr / $mssr) + $dm", 
                          output=maxName,
                          dem=demName, dc=dc, mselev=msElev, dm=dm, sr=srName, mssr=msSR, overwrite=True)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    


if __name__ == "__main__":
    options, flags = grass.parser()
    main()

def main():
    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    bboPhenipsLib.atDDCalc(bboLib.phenipsFromDay, dayTo,
                           bboLib.phenipsDDThreshold, 
                           bboLib.phenipsMapset, bboLib.phenipsATDDPrefix)
    
    bboPhenipsLib.ForecastDDCalc(dayFrom, dayTo,
                           bboLib.phenipsDDThreshold, 
                           bboLib.phenipsMapset, bboLib.phenipsFORECASTDDPrefix)
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()

def main():
    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])
    bboPhenipsLib.swarmingCalcForecast(bboLib.phenipsFromDay, dayFrom, dayTo,
                 swarmingDDThreshold=bboLib.phenipsSwarmingDDThreshold, 
                 flightThreshold=bboLib.phenipsFlightThreshold,
                 targetMapset=bboLib.phenipsMapset, 
                 swarmingName=bboLib.rasterMonth(bboLib.phenipsForecastSwarmingName, 1), 
                 atDDPrefix=bboLib.phenipsATDDPrefix,
                 forecastDDPrefix=bboLib.phenipsFORECASTDDPrefix,
                 atMaxPrefix = bboLib.atMaxPrefix, 
                 forecastMaxPrefix = bboLib.ForecastMaxPrefix)
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()

def main():
    dayTo = int(options["dayto"])
    bboPhenipsLib.swarmingCalc(bboLib.phenipsFromDay, dayTo,
                               bboLib.phenipsSwarmingDDThreshold, bboLib.phenipsFlightThreshold,
                               bboLib.phenipsMapset, 
                               bboLib.rasterMonth(bboLib.phenipsRealSwarmingName, 1), 
                               bboLib.phenipsATDDPrefix)
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
