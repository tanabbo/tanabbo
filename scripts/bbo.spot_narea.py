#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_narea
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates new spot areas in hectares
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates new spot areas in hectares
#% keywords: bark beetle spot area
#%end
#%option
#% key: yearfrom
#% type: integer
#% answer: 1994
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

import sys
import os
import grass.script as grass
import atexit
import string
import math
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPrognosisLib

def main():
    targetMapset = "forest"
    intervalLength = 2
    nullVal = -999999

    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])
    yearMin = 999999
    yearMax = -999999

    if (yearTo < yearFrom):
        grass.fatal("yearfrom must be less or equal to yearto")

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    area = []
    aMax = []
    aMin = []
    aMinLength = []
    aMaxLength = []

    areaList = bboPrognosisLib._getSpotAreasHa(bboLib.forestMapset, bboLib.spotTemplate, bboLib.updatedS50MaskTemplate, yearFrom, yearTo)

    y0 = 0
    while ((yearFrom + y0) <= yearTo):
        area.append(areaList[y0][bboPrognosisLib.NEW_SPOTCODE])
        if (area[y0]):
            if (yearMin==999999):
                yearMin = areaList[y0][0]
            yearMax = areaList[y0][0]
        y0 = y0 + 1

    y0 = 0
    while ((yearFrom + y0) <= yearTo):
        if (y0 < intervalLength):
            isAMin = False
            isAMax = False
        else:
            if (area[y0]):
                isAMin = True
                isAMax = True
                for y1 in range(y0 - intervalLength, y0 + intervalLength):
                    if (y1 != 0 and 0 <= (y1 + yearFrom) and (y1 + yearFrom) <= yearTo):
                        if (area[y1]):
                            if (area[y1] < area[y0]):
                                isAMin = False
                            if (area[y0] < area[y1]):
                                isAMax = False
            else:
                isAMin = False
                isAMax = False
        aMin.append(isAMin)
        aMax.append(isAMax)
        y0 = y0 + 1

    y0 = 0
    i0 = -1
    while ((yearFrom + y0) <= yearTo):
        il = 0
        if (aMin[y0]):
            if (-1 < i0):
                il = y0 - i0
            i0 = y0
        aMinLength.append(il)
        y0 = y0 + 1

    y0 = 0
    i0 = -1
    while ((yearFrom + y0) <= yearTo):
        il = 0
        if (aMax[y0]):
            if (-1 < i0):
                il = y0 - i0
            i0 = y0
        aMaxLength.append(il)
        y0 = y0 + 1

    y0 = 0
    bboLib.logMessage("year newArea isMin perMin isMax perMax spreadArea initArea r oldArea s50Area")
    while ((yearFrom + y0) <= yearTo):
        if (yearMin <= (yearFrom + y0) and (yearFrom + y0) <= yearMax):
            if ((areaList[y0][bboPrognosisLib.INIT_SPOTCODE] is not None) and (areaList[y0][bboPrognosisLib.SPREAD_SPOTCODE] is not None)):
                r = areaList[y0][bboPrognosisLib.SPREAD_SPOTCODE] / areaList[y0][bboPrognosisLib.INIT_SPOTCODE]
            else:
                r = None
            bboLib.logMessage("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}".format(yearMin + y0, area[y0], aMin[y0], aMinLength[y0], aMax[y0], aMaxLength[y0], areaList[y0][bboPrognosisLib.SPREAD_SPOTCODE], areaList[y0][bboPrognosisLib.INIT_SPOTCODE], r, areaList[y0][bboPrognosisLib.OLD_SPOTCODE], areaList[y0][6]))
        y0 = y0 + 1

    y0 = 0
    lcYear = -1
    while ((yearFrom + y0) <= yearTo):
        if (aMin[y0]):
            lcYear = y0
        y0 = y0 + 1
    lcYear = yearFrom + lcYear

    perLength = 4
    progYear = yearMax + 1
    perY = progYear - lcYear
    if (perLength <= perY):
        perY = 0

    minA = 999999.0
    maxA = -999999.0
    sumVal = 0.0
    sumVal2 = 0.0
    countVal = 0

    y0 = progYear - yearFrom
    while (0 <= y0):
        if ((yearFrom + y0) <= yearTo):
            if (area[y0]):
                countVal = countVal + 1
                sumVal = sumVal + area[y0]
                sumVal2 = sumVal2 + area[y0] * area[y0]
                if (area[y0] < minA):
                    minA = area[y0]
                if (maxA < area[y0]):
                    maxA = area[y0]
        y0 = y0 - perLength

    avgA = 0
    stdA = 0
    if (0 < countVal):
        avgA = sumVal / countVal
        stdA = sumVal2 / countVal - avgA * avgA
        stdA = math.sqrt(stdA)

    grass.message("***")
    grass.message(str.format("prognose year: {0}", progYear))
    grass.message(str.format("period beginning: {0}", lcYear))
    grass.message(str.format("period length: {0}", perLength))
    grass.message(str.format("period year: {0}", perY))
    grass.message("---")
    grass.message("spot area")
    grass.message(str.format("minimum: {0}", minA))
    grass.message(str.format("maximum: {0}", maxA))
    grass.message(str.format("average: {0}", avgA))
    grass.message(str.format("standard deviation: {0}", stdA))
    grass.message(str.format("optimistic: {0}", avgA - stdA))
    grass.message(str.format("pesimistic: {0}", avgA + stdA))

    # finish calculation, restore settings
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
