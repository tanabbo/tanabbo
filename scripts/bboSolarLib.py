#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bboSolarLib
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Functions for solar radiation calculations
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib


def sumMonth(mapsetName, solarDayPrefix, solarMonthPrefix, grassMessage):
    solarTmp = "tmp_solar_m"

    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == mapsetName:
        grass.run_command("g.mapset", mapset = mapsetName)

    monthDay = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    iDay = 1
    nMonths = len(monthDay)
    iOut = 1
    for iMonth in range(0, nMonths):
        grass.message(grassMessage + " {0}".format(iMonth + 1))
        monthName = bboLib.rasterMonth(solarMonthPrefix, iMonth + 1)
        bboLib.deleteRaster(monthName)
        strCmd = solarTmp + str(iOut) + " = " + bboLib.rasterDay(solarDayPrefix,  iDay)
        iOut = 3 - iOut
        grass.mapcalc(strCmd, overwrite=True)
        iDay = iDay + 1
        nDays = monthDay[iMonth]
        for i in range(1, nDays):
            strCmd = solarTmp + str(iOut) + " = " + solarTmp + str(3 - iOut) + " + " + bboLib.rasterDay(solarDayPrefix, iDay)
            iOut = 3 - iOut
            grass.mapcalc(strCmd, overwrite=True)
            iDay = iDay + 1
        strCmd = "$output = " + solarTmp + str(3 - iOut)
        grass.mapcalc(strCmd, overwrite=True, output=monthName)
    
    bboLib.deleteRaster(solarTmp + "1")
    bboLib.deleteRaster(solarTmp + "2")

    if not userMapset == mapsetName:
        grass.run_command("g.mapset", mapset=userMapset)


def sumYear(mapsetName, solarMonthPrefix, solarYear, grassMessage):
    solarTmp = "tmp_solar_y"

    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == mapsetName:
        grass.run_command("g.mapset", mapset = mapsetName)

    grass.message(grassMessage)

    bboLib.deleteRaster(solarYear)

    strCmd = solarTmp + "1 = " + bboLib.rasterMonth(solarMonthPrefix, 1) + " + " + bboLib.rasterMonth(solarMonthPrefix, 2)
    grass.mapcalc(strCmd, overwrite=True)
    iOut = 2
    for iMonth in range(3, 13):
        monthName = bboLib.rasterMonth(solarMonthPrefix, iMonth)
        strCmd = solarTmp + str(iOut) + " = " + solarTmp + str(3 - iOut) + " + " + monthName
        iOut = 3 - iOut
        grass.message(strCmd)
        grass.mapcalc(strCmd, overwrite=True)

    strCmd = solarYear + " = " + solarTmp + str(3 - iOut)
    grass.mapcalc(strCmd, overwrite=True)
    bboLib.deleteRaster(solarTmp + "1")
    bboLib.deleteRaster(solarTmp + "2")

    if not userMapset == mapsetName:
        grass.run_command("g.mapset", mapset=userMapset)
