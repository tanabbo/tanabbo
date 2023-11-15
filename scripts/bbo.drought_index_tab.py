#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.drought_index_tab
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Computes NSC2 index for Landsat scene
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Computes drought index into table
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
#%option
#% key: iswc
#% type: integer
#% answer: 199
#% options: 1-999
#% description: Initial soil water content (iswc)
#% required: yes
#%end
#%option
#% key: swc
#% type: integer
#% answer: 199
#% options: 1-999
#% description: Soil water content (swc)
#% required: yes
#%end
#%option
#% key: pda
#% type: double
#% answer: 155.5
#% options: 1-999
#% description: Point of decreased availability (pda)
#% required: yes
#%end
#%option
#% key: pwp
#% type: double
#% answer: 96.25
#% options: 1-999
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
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboDroughtLib


def main():
    initSoilWaterCont = int(options['iswc'])
    soilWaterCont = int(options['swc'])
    pointOfDecrAvail = float(options['pda'])
    permWiltingPoint = float(options['pwp'])
    interceptionVal = int(options['intercept'])
    resetOfCumDeficit = int(options['rcd'])
   
    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    if dayTo < dayFrom:
        grass.fatal("Parameter <dayfrom> must be less or equal than <dayto>")

    solarRadiation = bboLib.loadDataSeries(bboLib.solarRadiationFN)
    realPrecipitation = bboLib.loadDataSeries(bboLib.realPrecipitationFN)
    airTemperature = bboLib.loadDataSeries(bboLib.airTemperatureFN)

    minDay = bboLib.seriesMinDay(solarRadiation)
    maxDay = bboLib.seriesMaxDay(solarRadiation)

    if dayFrom < minDay:
        grass.fatal("Parameter <dayfrom> is out of series ({0})".format(minDay))

    if maxDay < dayTo:
        grass.fatal("Parameter <dayto> is out of series ({0})".format(maxDay))

    i = 0
    while (i < len(solarRadiation)):
        rem = 0
        if (solarRadiation[i][0] < dayFrom):
            rem = 1
        elif (dayTo < solarRadiation[i][0]):
            rem = 1
        if (rem):
            solarRadiation.remove(solarRadiation[i])
            realPrecipitation.remove(realPrecipitation[i])
            airTemperature.remove(airTemperature[i])
        else:
            i += 1

    potentialTransp, realTransp, dzvpSeries, droughtIdx, deficitSeries, cumDefSeries = bboDroughtLib.calculateDroughtIndex(dayFrom, dayTo, 
        airTemperature, solarRadiation, realPrecipitation,
        initSoilWaterCont, soilWaterCont, pointOfDecrAvail, permWiltingPoint, interceptionVal,resetOfCumDeficit)

    i = 0
    grass.message("day temp precip radiat ptransp rtransp swc deficit cumdeficit di")
    for iDay in range(dayFrom, dayTo):
        grass.message("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(iDay, airTemperature[i][1], realPrecipitation[i][1], solarRadiation[i][1],
                      potentialTransp[i][1], realTransp[i][1], dzvpSeries[i][1], deficitSeries[i][1], cumDefSeries[i][1], droughtIdx[i][1]))
        i += 1

    # set history for site map
    grass.message(_("Done."))    

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
