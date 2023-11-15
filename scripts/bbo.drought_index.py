#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.drought_index
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Computes NSC2 index for Landsat scene
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Computes drought index
#% keywords: drought index
#% keywords:TANABBO
#%end
#%option
#% key: dayfrom
#% type: integer
#% options: 1-365
#% answer: 92
#% description: Day from (1 - 365)
#% required : yes
#%end
#%option
#% key: dayto
#% type: integer
#% options: 1-365
#% answer: 204
#% description: Day to (1 - 365)
#% required : yes
#%end
#%option G_OPT_R_INPUT
#% answer: swc@hydro
#% key: iswc
#% description: Initial soil water content (iswc)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% answer: swc@hydro
#% key: swc
#% description: Soil water content (swc)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% answer: pda@hydro
#% key: pda
#% description: Point of decreased availability (pda)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% answer: pwp@hydro
#% key: pwp
#% description: Permanent wilting point
#% required: yes
#%end
#%option
#% key: intercept
#% type: integer
#% answer: 5
#% options: 0-99
#% description: Interception (intercept)
#% required: yes
#%end
#%option
#% key: rcd
#% type: integer
#% answer: 4
#% options: 2-99
#% description: Reset of cumulative deficit
#% required: yes
#%end

import sys
import os
import numpy
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboDroughtLib


def printValues(dayFrom, dayTo, airTemperature, realPrecipitation, solarRadiation,
                potentialTransp, realTransp, dzvpSeries, deficitSeries, cumDefSeries, droughtIdx):
    i = 0
    grass.message("day temp precip radiat ptransp rtransp swc deficit cumdeficit di")
    for iDay in range(dayFrom, dayTo):
        grass.message("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(iDay, airTemperature[i][1], realPrecipitation[i][1], solarRadiation[i][1],
                      potentialTransp[i][1], realTransp[i][1], dzvpSeries[i][1], deficitSeries[i][1], cumDefSeries[i][1], droughtIdx[i][1]))
        i += 1


def writeMap(iDay, valR, mapPrefix, nullVal):
    mapFN = (bboLib.rasterDay(mapPrefix, iDay))
    valR.write(mapFN, overwrite=True, null=nullVal)
    grass.run_command("r.null", map=mapFN, setnull=nullVal, quiet=True)
    grass.message(str.format("{3} day={0} min={1} max={2}", iDay, bboLib.getMinValue(mapFN), bboLib.getMaxValue(mapFN), mapFN))


def main():
    targetMapset = bboLib.hydroMapset
    nullVal = -999999

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)
    
    iswcFN = bboLib.checkInputRaster(options, 'iswc')
    swcFN = bboLib.checkInputRaster(options, 'swc')
    pdaFN = bboLib.checkInputRaster(options, 'pda')
    pwpFN = bboLib.checkInputRaster(options, 'pwp')
    interceptionVal = int(options['intercept'])
    resetOfCumDeficit = int(options['rcd'])
   
    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))

    solarRadiation = bboLib.loadDataSeries(bboLib.solarRadiationFN)
    realPrecipitation = bboLib.loadDataSeries(bboLib.realPrecipitationFN)
    airTemperature = bboLib.loadDataSeries(bboLib.airTemperatureFN)

    minDay = bboLib.seriesMinDay(solarRadiation)
    maxDay = bboLib.seriesMaxDay(solarRadiation)

    n = maxDay - minDay + 1
    while (bboLib.garray3DMaxRows < n):
        i = len(solarRadiation) - 1
        solarRadiation.remove(solarRadiation[i])
        realPrecipitation.remove(realPrecipitation[i])
        airTemperature.remove(airTemperature[i])
        minDay = bboLib.seriesMinDay(solarRadiation)
        maxDay = bboLib.seriesMaxDay(solarRadiation)
        n = maxDay - minDay + 1
    
    grass.message("min day {0}   max day {1}   series length {2}".format(minDay, maxDay, maxDay - minDay + 1))
    grass.message("day from {0}   day to {1}   days {2}".format(dayFrom, dayTo, dayTo - dayFrom + 1))

    if ((maxDay - minDay + 1) < 7):
        grass.fatal("The data series is too short")

    if dayFrom < minDay:
        grass.fatal("Parameter <dayfrom> is out of series ({0})".format(minDay))

    if maxDay < dayTo:
        grass.fatal("Parameter <dayto> is out of series ({0})".format(maxDay))

    gregion = grass.region()
    nRows = gregion['rows']
    nCols = gregion['cols']
    
    iswc = bboLib.garray(iswcFN)
    swc = bboLib.garray(swcFN)
    pda = bboLib.garray(pdaFN)
    pwp = bboLib.garray(pwpFN)

    nLays = dayFrom - dayTo + 1
    solarA = bboLib.garray3d(nLays)
    solarA.readMapSeries(bboLib.srdayPrefix, minDay, maxDay)

    for iDay in range(dayFrom, dayTo+1):
    #for iDay in (146,138,157,159):
        diR = bboLib.garray(None)
        defR = bboLib.garray(None)
        cdefR = bboLib.garray(None)
        for r in range(nRows):
            if ((r % 10) == 0):
                grass.message(str.format("day: {0}   row: {1}", iDay, r))
            for c in range(nCols):
                diR[r, c] = nullVal
                defR[r, c] = nullVal
                cdefR[r, c] = nullVal
                if (0 < iswc[r, c] and 0 < swc[r, c] and 0 < pda[r, c] and 0 < pwp[r, c]):
                    #radiationSer = bboLib.readMapSeries(bboLib.srdayPrefix, dayFrom, dayTo, r, c)
                    radiationSer = solarA.getSeries(minDay, maxDay, r, c)
                    potentialTransp, realTransp, dzvpSeries, droughtIdx, deficitSeries, cumDefSeries = bboDroughtLib.calculateDroughtIndex(
                                        minDay, maxDay, 
                                        airTemperature, radiationSer, realPrecipitation,
                                        iswc[r, c], swc[r, c], pda[r, c], pwp[r, c], interceptionVal,resetOfCumDeficit)
                    i = iDay - minDay
                    diR[r, c] = droughtIdx[i][1]
                    defR[r, c] = deficitSeries[i][1]
                    cdefR[r, c] = cumDefSeries[i][1]
                    #printValues(dayFrom, dayTo, airTemperature, realPrecipitation, solarRadiation,
                    #            potentialTransp, realTransp, dzvpSeries, deficitSeries, cumDefSeries, droughtIdx)
        writeMap(iDay, diR, bboLib.diPrefix, nullVal)
        writeMap(iDay, defR, bboLib.deficitPrefix, nullVal)
        writeMap(iDay, cdefR, bboLib.cumDefPrefix, nullVal)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
