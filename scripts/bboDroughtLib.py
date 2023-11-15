#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bboPrognosisLib
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Bark beetle prognosis library
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


# potential transpiration calculated by Turc
# output: potential transpiration
def potentialTranspiration(dayFrom, dayTo, airTemperature, solarRadiation):
    potentialTransp = []
    i = 0
    for iDay in range (dayFrom, dayTo + 1):
        if (iDay != airTemperature[i][0]):
            grass.fatal("Input data error (airTemperature iDay={0} {1})".format(iDay, airTemperature[i][0]))
        if (iDay != solarRadiation[i][0]):
            grass.fatal("Input data error (solarRadiation iDay={0} {1})".format(iDay, solarRadiation[i][0]))
        t = airTemperature[i][1]
        gr = solarRadiation[i][1]
        prec = None
        if (t != None and gr != None):
            if (0 < gr):
                prec = 0.013 * (t / (15.0 + t)) * ((gr / 41867.2807201172) + 50.0)
                prec = prec * 24.0 * 0.78
        potentialTransp.append((iDay, prec))
        i += 1
    return potentialTransp


# soil water capacity
# output: real transpiration, soil water capacity
def availableWaterReserve(dayFrom, dayTo, 
                          realPrecipitation, potentialTransp, 
                          initWaterReserve, interceptionVal, maxCappCapacity, reducedCappAttraction, wiltingPoint):
    i = 0
    realTransp = []
    dzvpSeries = []
    iValS = interceptionVal
    aboveRCA = False
    for iDay in range(dayFrom, dayTo + 1):
        iDay1 = iDay + 1
        zn = realPrecipitation[i][1]
        if (zn < iValS):
            iVal = zn
        else:
            iVal = iValS
        if (iDay == dayFrom):
            realTransp.append((iDay, None))
            dzvpSeries.append((iDay, None))
        elif (iDay == (dayFrom + 1)):
            zn1 = realPrecipitation[i-1][1]
            dzvpN = initWaterReserve + zn1 - iVal
            if (maxCappCapacity < dzvpN):
                dzvpN = maxCappCapacity
            dzvpN1 = dzvpN
            dzvpSeries.append((iDay, dzvpN))
            ptrN = potentialTransp[i][1]
            if (reducedCappAttraction < dzvpN):
                strN = ptrN
                realTransp.append((iDay, strN))
            else:
                realTransp.append((iDay, 0))
        else:
            zn1 = realPrecipitation[i-1][1]
            strN1 = realTransp[i-1][1]
            ptrN = potentialTransp[i][1]
            dzvpN = dzvpN1 + zn1 - iVal - strN1
            if (maxCappCapacity < dzvpN):
                dzvpN = maxCappCapacity
            if (dzvpN < wiltingPoint):
                dzvpN = wiltingPoint
            dzvpN1 = dzvpN
            dzvpSeries.append((iDay, dzvpN))
            if (reducedCappAttraction < dzvpN):
                strN = ptrN
            else:
                smer = ptrN / (reducedCappAttraction - wiltingPoint)
                if (0 < (dzvpN - wiltingPoint)):
                    strN = smer * (dzvpN - wiltingPoint)
                else:
                    strN = 0
            if (strN < 0):
                strN = 0
            realTransp.append((iDay, strN))
        i += 1
    return (realTransp, dzvpSeries)


# output: drought index
def droughtIndex(dayFrom, dayTo, potentialTransp, realTransp):
    droughtIdx = []
    i = 0
    for iDay in range (dayFrom, dayTo + 1):
        if (iDay != potentialTransp[i][0]):
            grass.fatal("Input data error")
        if (iDay != realTransp[i][0]):
            grass.fatal("Input data error")
        pt = potentialTransp[i][1]
        rt = realTransp[i][1]
        didx = None
        if (pt != None and rt != None):
            if (0 != pt):
                didx = (1.0 - (rt / pt))
            else:
                didx = 0
        droughtIdx.append((iDay, didx))
        i += 1
    return droughtIdx


# output: water deficit, cumulative water deficit
def waterDeficit(dayFrom, dayTo, potentialTransp, realTransp, restartCumDeficit):
    maxDays = 365
    deficitSeries = []
    cumDefSeries = []
    iIdx = []
    for i in range(0, maxDays):
        iIdx.append(0)
    cumDef = 0.0
    nDays = 0
    iRow = 1
    deficitSeries.append((dayFrom, None))
    cumDefSeries.append((dayFrom, None))
    for iDay in range(dayFrom + 1, dayTo + 1):
        ptrN = potentialTransp[iRow][1]
        strN = realTransp[iRow][1]
        defN = ptrN - strN
        deficitSeries.append((iDay, defN))
        cumDef += defN
        if (defN == 0 ):
            iIdx[nDays] = iRow
            nDays += 1
            flg = True
            if (nDays == restartCumDeficit):
                for i in range(0, restartCumDeficit - 1):
                    if (iIdx[i+1] != (iIdx[i] + 1)):
                        flg = False
                        for j in range (i+1, restartCumDeficit):
                            iIdx[j - i - 1] = iIdx[j]
                        nDays = restartCumDeficit - i - 1
                        break
                if (flg):
                    nDays = 0
                    cumDef = 0.0
                    for i in range(0, maxDays):
                        iIdx[i] = 0
        cumDefSeries.append((iDay, cumDef))
        iRow += 1
    return (deficitSeries, cumDefSeries)



def calculateDroughtIndex(dayFrom, dayTo, 
                          airTemperature, solarRadiation, realPrecipitation,
                          initWaterReserve, maxCappCapacity, reducedCappAttraction, wiltingPoint, interceptionVal, restartCumDeficit):
    potentialTransp = potentialTranspiration(dayFrom, dayTo, airTemperature, solarRadiation)

    realTransp, dzvpSeries = availableWaterReserve(dayFrom, dayTo, 
                                                   realPrecipitation, potentialTransp, 
                                                   initWaterReserve, interceptionVal, maxCappCapacity, reducedCappAttraction, wiltingPoint)

    droughtIdx = droughtIndex(dayFrom, dayTo, potentialTransp, realTransp)

    deficitSeries, cumDefSeries = waterDeficit(dayFrom, dayTo, potentialTransp, realTransp, restartCumDeficit)

    return (potentialTransp, realTransp, dzvpSeries, droughtIdx, deficitSeries, cumDefSeries)



def calcRiskDI(dayFrom, dayTo, riskThreshold):
    targetMapset = bboLib.hydroMapset
    stageTmp = "tmp_dlib_crdi_stage"
    diTmp = "tmp_dlib_crdi_di"

    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    for iDay in range(dayFrom, dayTo + 1):
        grass.message("drought risk day {0}".format(iDay))
        diName = bboLib.rasterDay(bboLib.diPrefix, iDay)
        stageName = bboLib.rasterDayMapset(bboLib.phenipsStagePrefix, iDay, bboLib.phenipsMapset)
        riskDIName = bboLib.rasterDay(bboLib.riskDIPrefix, iDay)

        if (bboLib.validateRaster(stageName)):
            grass.mapcalc("$output = if($stage == 1, 1, 0)", output=stageTmp, stage=stageName, overwrite=True)
            grass.run_command("r.null", map=stageTmp, null=0, quiet=True)

            if (bboLib.validateRaster(diName)):
                grass.mapcalc("$output = if($diThreshold <= $di, 1, 0)", output=diTmp, di=diName, diThreshold=riskThreshold, overwrite=True)
                grass.run_command("r.null", map=diTmp, null=0, quiet=True)
                grass.mapcalc("$output = $di + $stage", output=riskDIName, di=diTmp, stage=stageTmp, overwrite=True)

    bboLib.deleteRaster(stageTmp)
    bboLib.deleteRaster(diTmp)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)



def calcRiskCDEF(dayFrom, dayTo, riskThreshold):
    targetMapset = bboLib.hydroMapset
    stageTmp = "tmp_dlib_crdi_stage"
    cdefTmp = "tmp_dlib_crdi_cdef"

    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    for iDay in range(dayFrom, dayTo + 1):
        grass.message("cumulative deficit risk day {0}".format(iDay))
        cdefName = bboLib.rasterDay(bboLib.cumDefPrefix, iDay)
        stageName = bboLib.rasterDayMapset(bboLib.phenipsStagePrefix, iDay, bboLib.phenipsMapset)
        riskCDEFName = bboLib.rasterDay(bboLib.riskCDEFPrefix, iDay)

        if (bboLib.validateRaster(stageName)):
            grass.mapcalc("$output = if($stage == 1, 1, 0)", output=stageTmp, stage=stageName, overwrite=True)
            grass.run_command("r.null", map=stageTmp, null=0, quiet=True)

            if (bboLib.validateRaster(cdefName)):
                grass.mapcalc("$output = if($cdefThreshold < $cdef, 1, 0)", output=cdefTmp, cdef=cdefName, cdefThreshold=riskThreshold, overwrite=True)
                grass.run_command("r.null", map=cdefTmp, null=0, quiet=True)
                grass.mapcalc("$output = $cdef + $stage", output=riskCDEFName, cdef=cdefTmp, stage=stageTmp, overwrite=True)

    bboLib.deleteRaster(stageTmp)
    bboLib.deleteRaster(cdefTmp)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)



def cleanRisk(dayFrom, dayTo):
    targetMapset = bboLib.hydroMapset
    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    for iDay in range(dayFrom, dayTo + 1):
        grass.message("clean risk day {0}".format(iDay))
        riskDIName = bboLib.rasterDay(bboLib.riskDIPrefix, iDay)
        riskCDEFName = bboLib.rasterDay(bboLib.riskCDEFPrefix, iDay)
        bboLib.deleteRaster(riskDIName)
        bboLib.deleteRaster(riskCDEFName)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)



def cleanDrought(dayFrom, dayTo):
    targetMapset = bboLib.hydroMapset
    userMapset = grass.gisenv()["MAPSET"]
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    for iDay in range(dayFrom, dayTo + 1):
        grass.message("clean drought day {0}".format(iDay))
        bboLib.deleteRaster(bboLib.rasterDay(bboLib.diPrefix, iDay))
        bboLib.deleteRaster(bboLib.rasterDay(bboLib.deficitPrefix, iDay))
        bboLib.deleteRaster(bboLib.rasterDay(bboLib.cumDefPrefix, iDay))

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
