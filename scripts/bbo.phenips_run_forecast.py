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
#% answer: 120
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
    #air
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

    #bark
    atempMapset = bboLib.atMapset
    atMeanPrefix = bboLib.ForecastMeanPrefix
    atMaxPrefix = bboLib.ForecastMaxPrefix

    targetMapset2 = bboLib.btMapset
    btMeanPrefix = bboLib.ForecastbtMeanPrefix 
    btMaxPrefix = bboLib.ForecastbtMaxPrefix   
    btEffPrefix = bboLib.ForecastbtEffPrefix   

    solarMapset = bboLib.solarMapset
    srPrefix = bboLib.srdayPrefix

    s50maskName = bboLib.forestS50Mask + "@" + bboLib.forestMapset

    mean_a1 = -0.173
    mean_a2 = 0.0008518
    mean_a3 = 1.054
    
    max_a1 = 1.656
    max_a2 = 0.002955
    max_a3 = 0.534
    max_a4 = 0.01884

    eff_a1 = -310.667
    eff_a2 = 9.603

    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    #air
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

    #bark

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset2:
        grass.run_command("g.mapset", mapset=targetMapset2)

    dayTo += 1
    for iDay in range(dayFrom, dayTo):
        grass.message("bark temperature day " + str(iDay))
        srName = bboLib.validateRaster(bboLib.rasterDayMapset(srPrefix,  iDay, solarMapset))
        atmeanName = bboLib.validateRaster(bboLib.rasterDayMapset(atMeanPrefix,  iDay, atempMapset))
        atmaxName = bboLib.validateRaster(bboLib.rasterDayMapset(atMaxPrefix, iDay, atempMapset))
        #
        meanName = bboLib.rasterDay(btMeanPrefix, iDay)
        maxName = bboLib.rasterDay(btMaxPrefix, iDay)
        effName = bboLib.rasterDay(btEffPrefix,  iDay)
        bboLib.deleteRaster(meanName)
        bboLib.deleteRaster(maxName)
        bboLib.deleteRaster(effName)

        if (srName != None and atmeanName != None and atmaxName != None):
            #grass.mapcalc("$output = $s50mask * ($a1 + ($a2 * $sol) + ($a3 * $atmean))", 
            #              output=meanName, s50mask=s50maskName,
            #              a1=mean_a1, a2=mean_a2, a3=mean_a3, sol=srName, atmean=atmeanName, overwrite=True)
            #grass.mapcalc("$output = $s50mask * ($a1 + ($a2 * $sol) + ($a3 * $atmax) + ($a4 * $atmean))",
            #              output=maxName, s50mask=s50maskName,
            #              a1=max_a1, a2=max_a2, a3=max_a3, a4=max_a4, sol=srName, atmax=atmaxName, atmean=atmeanName, overwrite=True)
            #grass.mapcalc("$output = ($a1 + $a2*$btmax) / 24.0",
            #              output=effName,
            #              a1=eff_a1, a2=eff_a2, btmax=maxName, overwrite=True)
            grass.mapcalc("$output = ($a1 + ($a2 * $sol) + ($a3 * $atmean))", 
                          output=meanName,
                          a1=mean_a1, a2=mean_a2, a3=mean_a3, sol=srName, atmean=atmeanName, overwrite=True)
            grass.mapcalc("$output = ($a1 + ($a2 * $sol) + ($a3 * $atmax) + ($a4 * $atmean))",
                          output=maxName,
                          a1=max_a1, a2=max_a2, a3=max_a3, a4=max_a4, sol=srName, atmax=atmaxName, atmean=atmeanName, overwrite=True)
            grass.mapcalc("$output = ($a1 + $a2*$btmax) / 24.0",
                          output=effName,
                          a1=eff_a1, a2=eff_a2, btmax=maxName, overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    

if __name__ == "__main__":
    options, flags = grass.parser()
    main()

def main():
    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    bboPhenipsLib.atDDCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                           bboLib.phenipsDDThreshold, 
                           bboLib.phenipsMapset, bboLib.phenipsATDDPrefix)
    
    bboPhenipsLib.ForecastDDCalc(dayFrom, dayTo,
                           bboLib.phenipsDDThreshold, 
                           bboLib.phenipsMapset, bboLib.phenipsFORECASTDDPrefix)
    
    developmentName0 = "tmp_phenips_dev3"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == bboLib.phenipsMapset:
        grass.run_command("g.mapset", mapset=bboLib.phenipsMapset)

    # first day of within tree development
    grass.mapcalc("$output = if(0 < $val, $val + 1, 0)",
                  output=developmentName0, val=bboLib.rasterMonth(bboLib.phenipsInfestationName, 1), overwrite=True)
    
   # bboPhenipsLib.ForecastbtDDCalc(dayFrom, dayTo, bboLib.phenipsDDThreshold, bboLib.phenipsMapset, developmentName0, bboLib.phenipsFORECASTBTDDPrefix)

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
                 swarmingName=bboLib.rasterMonth(bboLib.phenipsForecast2SwarmingName, 1), 
                 atDDPrefix=bboLib.phenipsATDDPrefix,
                 forecastDDPrefix=bboLib.phenipsFORECASTDDPrefix,
                 atMaxPrefix = bboLib.atMaxPrefix, 
                 forecastMaxPrefix = bboLib.ForecastMaxPrefix)
    grass.message(_("Swarming 1")) 

    bboPhenipsLib.infestationCalcForecast(bboLib.phenipsFromDay, dayFrom, dayTo,
                 bboLib.phenipsInfestationDDThreshold, bboLib.phenipsFlightThreshold, 
                 targetMapset=bboLib.phenipsMapset, 
                 swarmingName=bboLib.rasterMonth(bboLib.phenipsForecast2SwarmingName, 1), 
                 infestationName=bboLib.rasterMonth(bboLib.phenipsForecastInfestationName, 1),
                 infestationSpan=bboLib.rasterMonth(bboLib.phenipsForecastInfestationSpan, 1),
                 atDDPrefix=bboLib.phenipsATDDPrefix,
                 forecastDDPrefix=bboLib.phenipsFORECASTDDPrefix,
                 atMaxPrefix = bboLib.atMaxPrefix, 
                 forecastMaxPrefix = bboLib.ForecastMaxPrefix)
    grass.message(_("Infestation 1"))  

    bboPhenipsLib.developmentCalcForecast(bboLib.phenipsFromDay, dayFrom, dayTo,
                                  bboLib.phenipsDDThreshold, 
                                  bboLib.phenipsInfestationDDThreshold, bboLib.phenipsFlightThreshold,
                                  bboLib.phenipsDevelopmentSumThreshold,
                                  bboLib.phenipsMapset, 
                                  bboLib.rasterMonth(bboLib.phenipsForecastInfestationName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsForecastDevelopmentName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsForecastDevelopmentSpanName, 1),
                                  bboLib.phenipsBTDDPrefix, bboLib.phenipsFORECASTBTDDPrefix)
    grass.message(_("Development 1"))

    bboLib.deleteDaySeries(bboLib.phenipsATDDPrefix)
    bboLib.deleteDaySeries(bboLib.phenipsFORECASTDDPrefix)

    bboPhenipsLib.calcGenerationsForecast(dayFrom, dayTo, bboLib.phenipsToDay)
    bboPhenipsLib.stageCalc(dayFrom, dayTo,
                            bboLib.phenipsMapset, 
                            bboLib.phenipsForecast2SwarmingName,
                            bboLib.phenipsForecastInfestationName,
                            bboLib.phenipsForecastDevelopmentName,
                            bboLib.phenipsForecastStagePrefix)
    
    grass.message(_("Stage calculation"))

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
