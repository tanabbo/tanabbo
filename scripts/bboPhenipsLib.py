#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bboPhenipsLib
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      PHENIPS library
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

import sys
import os
import grass.script as grass
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib


def cleanMapset():
    targetMapset = bboLib.phenipsMapset
    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    bboLib.deleteDaySeries(bboLib.phenipsATDDPrefix)
    bboLib.deleteDaySeries(bboLib.phenipsBTDDPrefix)
    bboLib.deleteMonthSeries(bboLib.phenipsSwarmingName)
    bboLib.deleteMonthSeries(bboLib.phenipsInfestationName)
    bboLib.deleteMonthSeries(bboLib.phenipsInfestationSpan)
    bboLib.deleteMonthSeries(bboLib.phenipsDevelopmentName)
    bboLib.deleteMonthSeries(bboLib.phenipsDevelopmentSpanName)
    bboLib.deleteDaySeries(bboLib.phenipsStagePrefix)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)



def atDDCalc(fromDay, toDay, ddThreshold, targetMapset, atDDPrefix):
    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # dd for the first day
    atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, fromDay, bboLib.atMapset)
    ddName = bboLib.rasterDay(atDDPrefix, fromDay)
    grass.mapcalc("$output = if($ddThreshold <= $atMax, $atMax - $ddThreshold, 0)",
                  output=ddName, atMax=atMaxName, ddThreshold=ddThreshold,
                  overwrite=True)
    grass.run_command("r.null", map=ddName, null=0, quiet=True)

    # calculate dd for max air temperature
    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("dd for max air temperature " + str(iDay))
        atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, iDay, bboLib.atMapset)
        ddName1 = bboLib.rasterDay(atDDPrefix, iDay - 1)
        ddName = bboLib.rasterDay(atDDPrefix, iDay)
        grass.mapcalc("$output = $ddName1 + if($ddThreshold < $atMax, $atMax - $ddThreshold, 0)",
                      output=ddName, ddName1=ddName1, atMax=atMaxName, ddThreshold=ddThreshold,
                      overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)   


def btDDCalc(fromDay, toDay, ddThreshold, targetMapset, developmentName0, btDDPrefix):
    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # dd for the first day
    ddName = bboLib.rasterDay(btDDPrefix, fromDay)
    btMaxName = bboLib.rasterDayMapset(bboLib.btMaxPrefix, fromDay, bboLib.btMapset)
    grass.mapcalc("$output = if($beginDay <= $iDay, $btMaxDay - $ddThreshold, 0)",
                  output=ddName, beginDay=developmentName0, btMaxDay=btMaxName, ddThreshold=ddThreshold, iDay=fromDay,
                  overwrite=True)
    grass.run_command("r.null", map=ddName, null=0, quiet=True)

    # mask for the other days
    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("effective bark temperature day " + str(iDay))
        btMaxName = bboLib.rasterDayMapset(bboLib.btMaxPrefix, iDay, bboLib.btMapset)
        ddName1 = bboLib.rasterDay(btDDPrefix, iDay - 1)
        ddName = bboLib.rasterDay(btDDPrefix, iDay)
        grass.mapcalc("$output = $ddPrevious + if($beginDay <= $iDay, $btMaxTemperature - $ddThreshold, 0)",
                      output=ddName, beginDay=developmentName0, btMaxTemperature=btMaxName, ddThreshold=ddThreshold,
                      ddPrevious=ddName1, iDay=iDay, overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def swarmingCalc(fromDay, toDay,
                 swarmingDDThreshold, flightThreshold,
                 targetMapset, swarmingName, atDDPrefix):
    tmpName1 = "tmp_phenips_infestation1"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # swarming day
    atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, fromDay, bboLib.atMapset)
    ddName = bboLib.rasterDay(atDDPrefix, fromDay)
    grass.mapcalc("$output = if($flightThreshold <= $atMax && $swarmingDDThreshold <= $dd, $iday, 0)",
                  output=swarmingName, atMax=atMaxName, flightThreshold=flightThreshold, 
                  swarmingDDThreshold=swarmingDDThreshold, dd=ddName, iday=fromDay, overwrite=True)

    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("day of swarming " + str(iDay))
        atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, iDay, bboLib.atMapset)
        ddName = bboLib.rasterDay(atDDPrefix, iDay)
        grass.mapcalc("$output = $val", output=tmpName1, val=swarmingName, overwrite=True)
        grass.mapcalc("$output = if(0 < $tmp, $tmp, if($flightThreshold <= $atMax && $swarmingDDThreshold <= $dd, $iday, 0))",
                      output=swarmingName, tmp=tmpName1, atMax=atMaxName, flightThreshold=flightThreshold, 
                      swarmingDDThreshold=swarmingDDThreshold, dd=ddName, iday=iDay, overwrite=True)

    bboLib.deleteRaster(tmpName1)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def infestationCalc(fromDay, toDay,
                    infestationDDThreshold, flightThreshold,
                    targetMapset, swarmingName, infestationName, infestationSpan, atDDPrefix):
    tmpName1 = "tmp_phenips_infestation2"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # infestation day
    atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, fromDay, bboLib.atMapset)
    ddName = bboLib.rasterDay(atDDPrefix, fromDay)
    grass.mapcalc("$output = if($flightThreshold <= $atMax && $infestationDDThreshold <= $dd, $iday, 0)",
                  output=infestationName, atMax=atMaxName, flightThreshold=flightThreshold, 
                  infestationDDThreshold=infestationDDThreshold, dd=ddName, iday=fromDay, overwrite=True) 

    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("day of infestation " + str(iDay))
        atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, iDay, bboLib.atMapset)
        ddName = bboLib.rasterDay(atDDPrefix, iDay)
        grass.mapcalc("$output = $val", output=tmpName1, val=infestationName, overwrite=True)
        grass.mapcalc("$output = if($tmp, $tmp, if($flightThreshold <= $atMax && $infestationDDThreshold <= $dd, $iday, 0))",
                      output=infestationName, tmp=tmpName1, atMax=atMaxName, flightThreshold=flightThreshold, 
                      infestationDDThreshold=infestationDDThreshold, dd=ddName, iday=iDay, overwrite=True)
    
    bboLib.deleteRaster(tmpName1)

    grass.mapcalc("$span = if(0 < $swarming, if(0 < $infestation, $infestation - $swarming, 0), 0)",
                  span=infestationSpan, swarming=swarmingName, infestation=infestationName, overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def developmentCalc(fromDay, toDay,
                    ddThreshold, infestationDDThreshold, flightThreshold, developmentSumThreshold, 
                    targetMapset, infestationName, developmentName, 
                    developmentSpanName, btDDPrefix):
    tmpName = "tmp_phenips_infestation3"
    developmentName0 = "tmp_phenips_dev3"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # first day of within tree development
    grass.mapcalc("$output = if(0 < $val, $val + 1, 0)",
                  output=developmentName0, val=infestationName, overwrite=True)

    btDDCalc(fromDay, toDay, ddThreshold, targetMapset, developmentName0, btDDPrefix)

    ddName = bboLib.rasterDay(btDDPrefix, fromDay)
    grass.mapcalc("$output = if($startDay == $iDay, if($sumThreshold <= $dd, $iDay), 0)", 
                  output=developmentName, iDay=fromDay, startDay=developmentName0, sumThreshold=developmentSumThreshold, 
                  dd=ddName, overwrite=True)
    
    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("development day " + str(iDay))
        ddName = bboLib.rasterDay(btDDPrefix, iDay)
        grass.mapcalc("$output = $val", output=tmpName, val=developmentName, overwrite=True)
        grass.mapcalc("$output = if(0 < $val, $val, if(0 < $startDay, if($startDay <= $iDay, if($sumThreshold <= $dd, $iDay, 0), 0), 0))", 
                      output=developmentName, iDay=iDay, startDay=developmentName0, 
                      sumThreshold=developmentSumThreshold, dd=ddName, val=tmpName, overwrite=True)

    grass.mapcalc("$spanDay = if(0 < $beginDay, if(0 < $finishDay, $finishDay - $beginDay, 0), 0)",
                  spanDay=developmentSpanName, beginDay=infestationName, finishDay=developmentName, overwrite=True)

    bboLib.deleteRaster(tmpName)
    bboLib.deleteRaster(developmentName0)
    bboLib.deleteDaySeries(btDDPrefix, False)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)



def atDDCalc1(fromLayer1, toDay, ddThreshold, targetMapset, atDDPrefix):
    tmpName = "tmp_phenips_atddcalc1"

    userMapset = grass.gisenv()["MAPSET"] 
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.mapcalc("$tmp = $fromLayer1", tmp=tmpName, fromLayer1=fromLayer1, overwrite=True)
    grass.run_command("r.null", map=tmpName, setnull=0, quiet=True)
    fromDay = int(bboLib.getMinValue(tmpName)) + 1
    bboLib.deleteRaster(tmpName)

    # dd for the first day
    atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, fromDay, bboLib.atMapset)
    ddName = bboLib.rasterDay(atDDPrefix, fromDay)
    grass.mapcalc("$output = if(($fromLayer1 + 1) == $fromDay, if($ddThreshold <= $atMax, $atMax - $ddThreshold, 0), 0)",
                  output=ddName, atMax=atMaxName, ddThreshold=ddThreshold, fromLayer1=fromLayer1, fromDay=fromDay,
                  overwrite=True)

    # calculate dd for max air temperature
    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("dd for max air temperature " + str(iDay))
        atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, iDay, bboLib.atMapset)
        ddName1 = bboLib.rasterDay(atDDPrefix, iDay - 1)
        ddName = bboLib.rasterDay(atDDPrefix, iDay)
        grass.mapcalc("$output = if($fromLayer1 < $iDay, if(($fromLayer1 + 1) == $iDay, if($ddThreshold <= $atMax, $atMax - $ddThreshold, 0), $ddName1 + if($ddThreshold < $atMax, $atMax - $ddThreshold, 0)), 0)",
                        output=ddName, atMax=atMaxName, ddThreshold=ddThreshold, fromLayer1=fromLayer1, iDay=iDay, ddName1=ddName1,
                        overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)  


def btDDCalc1(fromLayer1, toDay, ddThreshold, targetMapset, developmentName0, btDDPrefix):
    tmpName = "tmp_phenips_btddcalc1"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.mapcalc("$tmp = $fromLayer1", tmp=tmpName, fromLayer1=fromLayer1, overwrite=True)
    grass.run_command("r.null", map=tmpName, setnull=0, quiet=True)
    fromDay = int(bboLib.getMinValue(tmpName)) + 1
    bboLib.deleteRaster(tmpName)

    # dd for the first day
    ddName = bboLib.rasterDay(btDDPrefix, fromDay)
    btMaxName = bboLib.rasterDayMapset(bboLib.btMaxPrefix, fromDay, bboLib.btMapset)
    grass.mapcalc("$output = if(($fromLayer1 + 1) == $iDay, if($beginDay <= $iDay, $btMaxDay - $ddThreshold, 0), 0)",
                  output=ddName, beginDay=developmentName0, btMaxDay=btMaxName, ddThreshold=ddThreshold, iDay=fromDay,
                  fromLayer1=fromLayer1, overwrite=True)
    grass.run_command("r.null", map=ddName, null=0, quiet=True)

    # mask for the other days
    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("effective bark temperature day " + str(iDay))
        btMaxName = bboLib.rasterDayMapset(bboLib.btMaxPrefix, iDay, bboLib.btMapset)
        ddName1 = bboLib.rasterDay(btDDPrefix, iDay - 1)
        ddName = bboLib.rasterDay(btDDPrefix, iDay)
        grass.mapcalc("$output = if($fromLayer1 < $iDay, $ddPrevious + if($beginDay <= $iDay, $btmaxTemperature - $ddThreshold, 0), $ddPrevious)",
                      output=ddName, beginDay=developmentName0, btmaxTemperature=btMaxName, ddThreshold=ddThreshold, fromLayer1=fromLayer1,
                      ddPrevious=ddName1, iDay=iDay, overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def swarmingCalc1(fromLayer1, toDay,
                  swarmingDDThreshold, flightThreshold,
                  targetMapset, swarmingName, atDDPrefix):
    tmpName = "tmp_phenips_infestation11"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.mapcalc("$tmp = $fromLayer1", tmp=tmpName, fromLayer1=fromLayer1, overwrite=True)
    grass.run_command("r.null", map=tmpName, setnull=0, quiet=True)
    fromDay = int(bboLib.getMinValue(tmpName)) + 1
    bboLib.deleteRaster(tmpName)

    # swarming day
    atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, fromDay, bboLib.atMapset)
    ddName = bboLib.rasterDay(atDDPrefix, fromDay)
    grass.mapcalc("$output = if(($fromLayer1 + 1) == $iDay, if($flightThreshold <= $atMax && $swarmingDDThreshold <= $dd, $iDay, 0), 0)",
                  output=swarmingName, atMax=atMaxName, flightThreshold=flightThreshold, 
                  swarmingDDThreshold=swarmingDDThreshold, dd=ddName, iDay=fromDay, fromLayer1=fromLayer1, overwrite=True)

    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("day of swarming " + str(iDay))
        atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, iDay, bboLib.atMapset)
        ddName = bboLib.rasterDay(atDDPrefix, iDay)
        grass.mapcalc("$output = $val", output=tmpName, val=swarmingName, overwrite=True)
        grass.mapcalc("$output = if($fromLayer1 < $iDay, if(0 < $tmp, $tmp, if($flightThreshold <= $atMax && $swarmingDDThreshold <= $dd, $iDay, 0)), $tmp)",
                      output=swarmingName, tmp=tmpName, atMax=atMaxName, flightThreshold=flightThreshold, fromLayer1=fromLayer1,
                      swarmingDDThreshold=swarmingDDThreshold, dd=ddName, iDay=iDay, overwrite=True)

    bboLib.deleteRaster(tmpName)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def infestationCalc1(fromLayer1, toDay,
                     infestationDDThreshold, flightThreshold,
                     targetMapset, swarmingName, infestationName, infestationSpan, atDDPrefix):
    tmpName = "tmp_phenips_infestation12"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.mapcalc("$tmp = $fromLayer1", tmp=tmpName, fromLayer1=fromLayer1, overwrite=True)
    grass.run_command("r.null", map=tmpName, setnull=0, quiet=True)
    fromDay = int(bboLib.getMinValue(tmpName)) + 1
    bboLib.deleteRaster(tmpName)

    # infestation day
    atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, fromDay, bboLib.atMapset)
    ddName = bboLib.rasterDay(atDDPrefix, fromDay)
    grass.mapcalc("$output = if(($fromLayer1 + 1) == $iDay, if($flightThreshold <= $atMax && $infestationDDThreshold <= $dd, $iDay, 0), 0)",
                  output=infestationName, atMax=atMaxName, flightThreshold=flightThreshold, fromLayer1=fromLayer1,
                  infestationDDThreshold=infestationDDThreshold, dd=ddName, iDay=fromDay, overwrite=True) 

    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("day of infestation " + str(iDay))
        atMaxName = bboLib.rasterDayMapset(bboLib.atMaxPrefix, iDay, bboLib.atMapset)
        ddName = bboLib.rasterDay(atDDPrefix, iDay)
        grass.mapcalc("$output = $val", output=tmpName, val=infestationName, overwrite=True)
        grass.mapcalc("$output = if($fromLayer1 < $iDay, if($tmp, $tmp, if($flightThreshold <= $atMax && $infestationDDThreshold <= $dd, $iDay, 0)), $tmp)",
                      output=infestationName, tmp=tmpName, atMax=atMaxName, flightThreshold=flightThreshold, fromLayer1=fromLayer1,
                      infestationDDThreshold=infestationDDThreshold, dd=ddName, iDay=iDay, overwrite=True)
    
    bboLib.deleteRaster(tmpName)

    grass.mapcalc("$span = if(0 < $swarming, if(0 < $infestation, $infestation - $swarming, 0), 0)",
                  span=infestationSpan, swarming=swarmingName, infestation=infestationName, overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def developmentCalc1(fromLayer1, toDay,
                     ddThreshold, infestationDDThreshold, flightThreshold, developmentSumThreshold, 
                     targetMapset, infestationName, developmentName, 
                     developmentSpanName, btDDPrefix):
    tmpName = "tmp_phenips_infestation13"
    developmentName0 = "tmp_phenips_dev13"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    # first day of within tree development
    grass.mapcalc("$output = if(0 < $val, $val + 1, 0)",
                  output=developmentName0, val=infestationName, overwrite=True)

    grass.mapcalc("$tmp = $fromLayer1", tmp=tmpName, fromLayer1=fromLayer1, overwrite=True)
    grass.run_command("r.null", map=tmpName, setnull=0, quiet=True)
    fromDay = int(bboLib.getMinValue(tmpName)) + 1
    bboLib.deleteRaster(tmpName)

    btDDCalc1(fromLayer1, toDay, ddThreshold, targetMapset, developmentName0, btDDPrefix)

    ddName = bboLib.rasterDay(btDDPrefix, fromDay)
    grass.mapcalc("$output = if($startDay == $iDay, if($sumThreshold <= $dd, $iDay), 0)", 
                  output=developmentName, iDay=fromDay, startDay=developmentName0, sumThreshold=developmentSumThreshold, 
                  dd=ddName, overwrite=True)
    
    for iDay in range(fromDay + 1, toDay + 1):
        if ((iDay % 10) == 0):
            grass.message("development day " + str(iDay))
        ddName = bboLib.rasterDay(btDDPrefix, iDay)
        grass.mapcalc("$output = $val", output=tmpName, val=developmentName, overwrite=True)
        grass.mapcalc("$output = if(0 < $val, $val, if(0 < $startDay, if($startDay <= $iDay, if($sumThreshold <= $dd, $iDay, 0), 0), 0))", 
                      output=developmentName, iDay=iDay, startDay=developmentName0, 
                      sumThreshold=developmentSumThreshold, dd=ddName, val=tmpName, overwrite=True)

    grass.mapcalc("$spanDay = if(0 < $beginDay, if(0 < $finishDay, $finishDay - $beginDay, 0), 0)",
                  spanDay=developmentSpanName, beginDay=infestationName, finishDay=developmentName, overwrite=True)

    bboLib.deleteRaster(tmpName)
    bboLib.deleteRaster(developmentName0)
    bboLib.deleteDaySeries(btDDPrefix, False)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def calcGenerations(dayTo):
    targetMapset = bboLib.phenipsMapset
    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    i = 2
    cont = True
    while (cont):
        grass.message("bark beetle generation {0}".format(i))

        atDDCalc1(bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i - 1), 
                  dayTo,
                  bboLib.phenipsDDThreshold, 
                  bboLib.phenipsMapset, 
                  bboLib.phenipsATDDPrefix)

        swarmingCalc1(bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i - 1), 
                      dayTo,
                      bboLib.phenipsSwarmingDDThreshold, 
                      bboLib.phenipsFlightThreshold,
                      bboLib.phenipsMapset, 
                      bboLib.rasterMonth(bboLib.phenipsSwarmingName, i), 
                      bboLib.phenipsATDDPrefix)

        infestationCalc1(bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i - 1), 
                         dayTo,
                         bboLib.phenipsInfestationDDThreshold, 
                         bboLib.phenipsFlightThreshold,
                         bboLib.phenipsMapset, 
                         bboLib.rasterMonth(bboLib.phenipsSwarmingName, i),
                         bboLib.rasterMonth(bboLib.phenipsInfestationName, i),
                         bboLib.rasterMonth(bboLib.phenipsInfestationSpan, i),
                         bboLib.phenipsATDDPrefix)

        developmentCalc1(bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i - 1), 
                         dayTo,
                         bboLib.phenipsDDThreshold, 
                         bboLib.phenipsInfestationDDThreshold, 
                         bboLib.phenipsFlightThreshold,
                         bboLib.phenipsDevelopmentSumThreshold,
                         bboLib.phenipsMapset, 
                         bboLib.rasterMonth(bboLib.phenipsInfestationName, i),
                         bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i),
                         bboLib.rasterMonth(bboLib.phenipsDevelopmentSpanName, i),
                         bboLib.phenipsBTDDPrefix)
        
        minVal = int(bboLib.getMinValue(bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i)))
        maxVal = int(bboLib.getMaxValue(bboLib.rasterMonth(bboLib.phenipsDevelopmentName, i)))

        cont = (0 < maxVal) and (minVal < dayTo)
        i += 1

    bboLib.deleteDaySeries(bboLib.phenipsATDDPrefix)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)



def stageCalc(fromDay, toDay, 
              targetMapset, swarmingPrefix, infestationPrefix, developmentPrefix, 
              stagePrefix, showMessage=True):
    tmpName = "tmp_phenips_stage1"

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    maxGen = 0
    i = 1
    cont = True
    while (cont):
        devName = bboLib.rasterMonth(developmentPrefix, i)
        if (bboLib.validateRaster(devName)):
            maxGen = i
            i += 1
        else:
            cont = False

    if (0 < maxGen):
        for iDay in range(fromDay, toDay + 1):
            stageName = bboLib.rasterDay(stagePrefix, iDay)
            grass.mapcalc("$stage = 0", stage=stageName, overwrite=True)

    i = maxGen
    while (0 < i):
        grass.message("update stage generation {0}".format(i))
        swarmingName = bboLib.rasterMonth(swarmingPrefix, i)
        infestationName = bboLib.rasterMonth(infestationPrefix, i)
        developmentName = bboLib.rasterMonth(developmentPrefix, i)

        for iDay in range(fromDay, toDay + 1):
            if (((iDay % 10) == 0) and showMessage):
                grass.message("update stage day {0}".format(iDay))
            stageName = bboLib.rasterDay(stagePrefix, iDay)
            grass.mapcalc("$tmp = $stage", tmp=tmpName, stage=stageName, overwrite=True)
            grass.mapcalc("$stage = if(0 < $tmp, $tmp, if(0 < $development && $development < $iDay, 3, if(0 < $infestation && $infestation < $iDay , 2, if(0 < $swarming && $swarming < $iDay, 1, 0))))",
                            stage=stageName, tmp=tmpName,
                            swarming=swarmingName, infestation=infestationName, development=developmentName,
                            iDay=iDay, overwrite=True)
        i -= 1

    bboLib.deleteRaster(tmpName)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
