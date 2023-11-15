#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bboLib
# AUTHOR(S):	Milan Koren, Rastislav Jakus, Miroslav Blazenec
# PURPOSE:      Bark beetle outbreak library
# COPYRIGHT:	This program is free software under the GNU General Public
#		        License (>=v2). Read the file COPYING that comes with GRASS
#		        for details.
#
#############################################################################

import os
import numpy
import grass.script as grass
import collections


#region #################### PARAMETERS ####################

DEBUG_ON = False

defaultYearFrom = 1980
defaultYearTo = 2025

# infestation mapset
infestationMapset = "bb_infestation"
infestationDDPrefix = "at_dd_d"

# forest mapset
forestMapset = "forest"
forestS50Mask = "s50mask"
s50MaskTemplate = "s50mask"
s50DstTemplate = "s50dst_%Y"
updatedS50MaskTemplate = "us50mask_%Y"
updatedS50DstTemplate = "us50dst_%Y"

# bark beetle spot, mapset forest
spotPrefix = "bb_spot_"
spotidPrefix = "bb_spotid_"
fdstPrefix = "bb_fdst_"
edstPrefix = "bb_edst_"
eidPrefix = "bb_eid_"
fidPrefix = "bb_fid_"
spotTemplate = "bb_spot_%Y"
spotidTemplate = "bb_spotid_%Y"
fdstTemplate = "bb_fdst_%Y"
edstTemplate = "bb_edst_%Y"
eidTemplate = "bb_eid_%Y"
fidTemplate = "bb_fid_%Y"
activespotdstTemplate = "bb_xdst_%Y"
activespotdstidTemplate = "bb_xdstid_%Y"
allspotdstTemplate = "bb_adst_%Y"
allspotdstidTemplate = "bb_adstid_%Y"
oldspotdstTemplate = "bb_odst_%Y"
oldspotdstidTemplate = "bb_odstid_%Y"
spotAreaTemplate = "bb_spotarea_%Y"
eactiveSpotTemplate = "bb_eactive_%Y"
factiveSpotTemplate = "bb_factive_%Y"

# bark beetle spot, mapset bb_prognosis
spotProgPrefix = "bbp_spot_"
spotidProgPrefix = "bbp_spotid_"
fdstProgPrefix = "bbp_fdst_"
edstProgPrefix = "bbp_edst_"
eidProgPrefix = "bbp_eid_"
fidProgPrefix = "bbp_fid_"

# solar mapset, solar radiation
solarMapset = "solar"
psrdayPrefix = "psr_d"
psrmonthPrefix = "psr_m"
psryearPrefix = "psr_y"
srdayPrefix = "sr_d"
srmonthPrefix = "sr_m"
sryearPrefix = "sr_y"

# hydro mapset, drought index
hydroMapset = "hydro"
diPrefix = "di_d"
deficitPrefix = "def_d"
cumDefPrefix = "cdef_d"
solarRadiationFN = "md_gsr_di.txt"
realPrecipitationFN = "md_prec_di.txt"
airTemperatureFN = "md_tmean_di.txt"
riskDIPrefix = "risk_di_d"
riskCDEFPrefix = "risk_cdef_d"

# air temperature prefix
atMapset = "temperature_air"
atMeanPrefix = "at_mean_d"
atMaxPrefix = "at_max_d"

# bark temperature
btMapset = "temperature_bark"
btMeanPrefix = "bt_mean_d"
btMaxPrefix = "bt_max_d"
btEffPrefix = "bt_eff_d"

# shp mapset
shpMapset = "shp"
shpMeteostation = "meteo_station"
shpMeteostationValField = "val"
shpBBTrap = "bbtrap"

# dem mapset
demMapset = "dem"
demLayer = "dem"
aspectLayer = "aspect"
slopeLayer = "slope"

# PHENIPS mapset
phenipsMapset = "bb_infestation"
phenipsFlightThreshold = 16.5
phenipsDDThreshold = 8.3
phenipsSwarmingDDThreshold = 60
phenipsInfestationDDThreshold = 140
phenipsFromDay = 92     #01.04. / 92
phenipsToDay = 304      #30.09. / 274        30.10. / 304
phenipsSwarmingName = "_swarming"
phenipsInfestationName = "_infestation"
phenipsInfestationSpan = "_infestation_span"
phenipsDevelopmentName = "_development"
phenipsDevelopmentSpanName = "_development_span"
phenipsStagePrefix = "stage_d"
phenipsATDDPrefix = "at_dd_d"
phenipsBTDDPrefix = "bt_dd_d"
phenipsDevelopmentSumThreshold = 557

# garray3D
garray3DMaxRows = 220

#endregion



#region #################### MESSAGES ####################
def doneMessage():
    grass.message("\n*** DONE ***\n\n")


def debugMessage(msg, printMessage=False):
    if (printMessage):
        grass.message(msg)
    else:
        if (DEBUG_ON):
            grass.message("DEBUG: " + msg)


def setDebug(project=None):
    global DEBUG_ON
    if (project):
        DEBUG_ON = project["debugOn"]
    else:
        DEBUG_ON = True


def errorMessage(msg):
    grass.message("ERROR: " + msg)


def warningMessage(msg):
    grass.message("WARNING: " + msg)


def logMessage(msg, logFile=None):
    grass.message(msg)
    if (logFile):
        logFile.writelines(msg + "\n")


def deleteFile(fileName):
    if (fileName):
        if (os.path.exists(fileName)):
            os.remove(fileName)


def deleteFileSeries(fileTemplate, yearFrom, yearTo):
    for year in range(yearFrom, yearTo + 1):
        fileName = replaceYearParameter(fileTemplate, year)
        deleteFile(fileName)


def getFullLogFileName(logFN):
    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    return os.path.join(dbName, locName, "_data\\prognoses", logFN)

#endregion



#region #################### VECTOR UTILITIES ####################
def validateVector(vectorName, targetMapset=None, printMsg=False):  
    if (not vectorName):
        debugMessage("bboLib.validateVector: vector name is None")
        return None

    debugMessage("bboLib.validateVector {0}".format(vectorName))
    if (grass.find_file(vectorName, "vector", targetMapset)['file']):
        return vectorName
    
    msg = "Vector is not valid: {0}".format(getLayerWithMapset(vectorName, targetMapset))
    debugMessage(msg, printMsg)

    return None    


def deleteVector(vectorName):
    if (validateVector(vectorName)):
        grass.run_command("g.remove", name=vectorName, type="vector", flags="fb", quiet=True)
#endregion



#region #################### RASTER UTILITIES ####################
def getLayerWithMapset(layerName, mapsetName):
    if (mapsetName):
        return layerName + "@" + mapsetName
    return layerName


def deleteRaster(rasterName):
    if (validateRaster(rasterName)):
        grass.run_command("g.remove", name=rasterName, type="raster", flags="fb", quiet=True)


def deleteGroup(groupName):
    try:
        grass.run_command("g.remove", name=groupName, type="group", flags="f", quiet=True)
    except:
        return


def copyRaster(inFN, outFN):
    try:
        grass.run_command("g.copy", raster="{0},{1}".format(inFN, outFN), overwrite=True, quiet=True)
    except:
        return


def checkInputRaster(options, paramName):
    rasterName = options[paramName]
    if not rasterName:
        grass.fatal("Required parameter <%s> not set".format(paramName))
    if not grass.find_file(rasterName)['file']:
        grass.fatal("{0} does not exist.".format(rasterName))
    return rasterName


def checkOptionalRaster(options, paramName):
    rasterName = options[paramName]
    if rasterName:
        if grass.find_file(rasterName)['file']:
            return rasterName
    return None


def checkOutputRaster(options, paramName):
    rasterName = options[paramName]
    if not rasterName:
        grass.fatal("Required parameter {0} not set".format(paramName))
    return rasterName


def checkRaster(rasterName, targetMapset=None):
    if not rasterName:
        grass.fatal("Raster name is empty")
    if (targetMapset):
        fullRasterName = rasterName + "@" + targetMapset
    else:
        fullRasterName = rasterName
    if not grass.find_file(fullRasterName)['file']:
        grass.fatal("{0} does not exist.".format(fullRasterName))
    return True


def validateRaster(rasterName, targetMapset=None, printMsg=False):
    if (not rasterName):
        debugMessage("bboLib.Raster name is None")
        return None

    debugMessage("bboLib.validateRaster {0}".format(rasterName))
    if (grass.find_file(rasterName, "cell", targetMapset)['file']):
        return rasterName
    
    msg = "Raster is not valid: {0}".format(getLayerWithMapset(rasterName, targetMapset))
    debugMessage(msg, printMsg)

    return None


def validateRasters(layerList):
    if (len(layerList) == 0):
        return False
    for lay in layerList:
        if (validateRaster(lay) == None):
            return False
    return True


def validateRastersStringList(rasterStringList):
    rastersLst = rasterStringList.split(",")
    return validateRasters(rastersLst)



def formatNum(numString, numLength):
    while len(numString) < numLength:
        numString = "0" + numString
    return numString


def rasterDay(rasterPrefix, iDay, mapsetName = None):
    if (mapsetName):
        return rasterPrefix + formatNum(str(iDay), 3) + "@" + mapsetName
    else:
        return rasterPrefix + formatNum(str(iDay), 3)


def rasterMonth(rasterPrefix, iMonth, mapsetName = None):
    if (mapsetName):
        return rasterPrefix + formatNum(str(iMonth), 2) + "@" + mapsetName
    else:
        return rasterPrefix + formatNum(str(iMonth), 2)


def rasterYear(rasterPrefix, iYear, mapsetName = None):
    if (mapsetName):
        return rasterPrefix + formatNum(str(iYear), 4)  + "@" + mapsetName
    else:
        return rasterPrefix + formatNum(str(iYear), 4)


def rasterDayMapset(rasterPrefix, iDay, mapsetName):
    return rasterDay(rasterPrefix, iDay) + "@" + mapsetName


def replaceYearParameter(nameTemplate, year, targetMapset=None):
    l = nameTemplate.replace("%Y-1", str(year - 1))
    l = l.replace("%Y+1", str(year + 1))
    l = l.replace("%Y", str(year))
    l = l.replace("%", str(year))
    return getLayerWithMapset(l, targetMapset)


def replaceYearMonthParameter(nameTemplate, year, month, targetMapset=None):
    l = nameTemplate.replace("%Y-1", str(year - 1))
    l = l.replace("%Y+1", str(year + 1))
    l = l.replace("%Y", str(year))
    l = l.replace("%M", str(month))
    l = l.replace("%", str(year))
    return getLayerWithMapset(l, targetMapset)


def replaceYearDayParameter(nameTemplate, year, day, targetMapset=None):
    l = nameTemplate.replace("%Y-1", str(year - 1))
    l = l.replace("%Y+1", str(year + 1))
    l = l.replace("%Y", str(year))
    l = l.replace("%D", str(day))
    l = l.replace("%", str(year))
    return getLayerWithMapset(l, targetMapset)


def replaceYearBandParameter(template, year, band, mapset=None):
    l = template.replace("%Y-1", str(year - 1))
    l = l.replace("%Y+1", str(year + 1))
    l = l.replace("%Y", str(year))
    l = l.replace("%B-1", formatNum(str(band - 1), 2))
    l = l.replace("%B+1", formatNum(str(band + 1), 2))
    l = l.replace("%B", formatNum(str(band), 2))
    l = l.replace("%b-1", str(band - 1))
    l = l.replace("%b+1", str(band + 1))
    l = l.replace("%b", str(band))
    l = l.replace("%", str(year))
    return getLayerWithMapset(l, mapset)


def replaceDayParameter(nameTemplate, day, targetMapset=None):
    l = nameTemplate.replace("%D", str(day))
    l = l.replace("%", str(day))
    return getLayerWithMapset(l, targetMapset)


def rescaleRaster(inGrid, outGrid, vmin=0.0, vmax=1.0):
    debugMessage("bboLib.rescaleRaster")
    tmp1 = "tmp_rescaleraster1"
    tmp2 = "tmp_rescaleraster2"
    p = grass.parse_command("r.info", flags="r", map=inGrid)
    dmin = float(p["min"])
    dmax = float(p["max"])
    debugMessage("bboLib.rescaleRaster grid={0}   dmin={1}   dmax={2}".format(inGrid, dmin, dmax))
    if (dmin < dmax):
        if (vmin < vmax):
            d = (vmax - vmin) / (dmax - dmin)
            grass.mapcalc("$tmp1 = $d * ($inGrid - $dmin) + $vmin", tmp1=tmp1, inGrid=inGrid, vmin=vmin, d=d, dmin=dmin, overwrite=True)
            grass.mapcalc("$tmp2 = if($tmp1 < $vmin, $vmin, $tmp1)", tmp2=tmp2, tmp1=tmp1, vmin=vmin, overwrite=True)
            grass.mapcalc("$outGrid = if($vmax < $tmp2, $vmax, $tmp2)", outGrid=outGrid, tmp2=tmp2, vmax=vmax, overwrite=True)
            deleteRaster(tmp2)
            deleteRaster(tmp1)
        else:
            d = vmin
            vmin = vmax
            vmax = d
            d = (vmax - vmin) / (dmax - dmin)
            grass.mapcalc("$tmp1 = $d * ($dmax - $inGrid) + $vmin", tmp1=tmp1, inGrid=inGrid, vmin=vmin, d=d, dmax=dmax, overwrite=True)
            grass.mapcalc("$tmp2 = if($tmp1 < $vmin, $vmin, $tmp1)", tmp2=tmp2, tmp1=tmp1, vmin=vmin, overwrite=True)
            grass.mapcalc("$outGrid = if($vmax < $tmp2, $vmax, $tmp2)", outGrid=outGrid, tmp2=tmp2, vmax=vmax, overwrite=True)
            deleteRaster(tmp2)
            deleteRaster(tmp1)
    else:
        grass.mapcalc("$outGrid = if($inGrid <= $dmax, $vmin)", outGrid=outGrid, inGrid=inGrid, dmax=dmax, vmin=vmin, overwrite=True)


def exportRasterToAAI(sourceFN, targetDir, targetFN):
    if (validateRaster(sourceFN, None, False)):
        debugMessage("bboLib.exportRasterToAAI raster {0}".format(sourceFN))
        targetFFN = "{0}\\{1}.asc".format(targetDir, targetFN)
        grass.run_command("r.out.gdal", input=sourceFN, output=targetFFN, nodata="-9999", type="Float32", format="AAIGrid", overwrite=True)

def exportRasterYearToAAI(sourceMapset, sourceTemplate, yearFrom, yearTo, targetDir):
    debugMessage("bboLib.exportRasterYearToAAI")
    for year in range(yearFrom, yearTo + 1):
        sourceFN = replaceYearParameter(sourceTemplate, year, sourceMapset)
        targetFN = replaceYearParameter(sourceTemplate, year)
        exportRasterToAAI(sourceFN, targetDir, targetFN)

#endregion



#region #################### RASTER AREA ####################
def getRasterArea(rasterName):
    p = grass.read_command("r.stats", flags="an", input=rasterName, quiet=True)
    if (p == ""):
        return 0.0
    return float(p.split(" ")[1])

def getCellsNumber(rasterName, value=None):
    tmp = "tmp_bbolib_cellsnumber_1"
    if (value is None):
        rasterFN = rasterName
    else:
        grass.mapcalc("$tmp = if($valRaster == $val, 1, null())", tmp=tmp, valRaster=rasterName, val=value, overwrite=True)
        rasterFN = tmp
    p = grass.read_command("r.stats", flags="cn", input=rasterFN, quiet=True)
    deleteRaster(tmp)
    if (p == ""):
        return 0
    return int(p.split(" ")[1])

def getNotNullCellsNumber(rasterName):
    p = grass.parse_command("r.univar", flags="g", map=rasterName, quiet=True)
    if (0 < len(p)):
        return int(p["n"].strip())
    return 0

def getMinValue(rasterName):
    p = grass.parse_command("r.univar", flags="g", map=rasterName, quiet=True)
    if (0 < len(p)):
        return float(p["min"].strip())
    return 0

def getMaxValue(rasterName):
    p = grass.parse_command("r.univar", flags="g", map=rasterName, quiet=True)
    if (0 < len(p)):
        return float(p["max"].strip())
    return 0


def getValueStatistics(rasterNames):
    p = grass.parse_command("r.univar", flags="g", map=rasterNames, quiet=True)

    if (0 < len(p)):
        cells = int(p["cells"].strip())
        minVal = float(p["min"].strip())
        maxVal = float(p["max"].strip())
        avgVal = float(p["mean"].strip())
        stdVal = float(p["stddev"].strip())
        valStat = collections.namedtuple("valSatistics", "cells min max avg std")
        return valStat(cells, minVal, maxVal, avgVal, stdVal)

    return None

def getCellArea():
    p = grass.parse_command("g.region", flags="m")
    if (0 < len(p)):
        sx = float(p["ewres"].strip())
        sy = float(p["nsres"].strip())
        return sx*sy
    return 0.0

#endregion



#region #################### DATA SERIES PROCESSING ####################
def loadDataSeries(fileName):
    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    fileName = os.path.join(dbName, locName, "_data", fileName)
    s = list()
    txtFile = open(fileName, "r")
    for l in txtFile:
        if (2 < len(l)):
            d, v = l.split()
            s.append((int(d), float(v)))
    txtFile.close()
    return s


def linearInterpolation(valSeries, iDay):
    i1 = 0
    n = len(valSeries)
    while (i1 < n and valSeries[i1][0] <= iDay):
        i1 = i1 + 1
    if (n <= i1):
        c = None
    elif (0 < i1):
        i0 = i1 - 1
        if (valSeries[i0][0] == iDay):
            c = valSeries[i0][1]
        else:
            c = (iDay - valSeries[i0][0]) * (valSeries[i1][1] - valSeries[i0][1])/(valSeries[i1][0] - valSeries[i0][0]) + valSeries[i0][1]
    else:
        c = None
    return c


def seriesMinDay(valSeries):
    iDay = 999999
    for s in valSeries:
        if (s[0] < iDay):
            iDay = s[0]
    return iDay

def seriesMaxDay(valSeries):
    iDay = 0
    for s in valSeries:
        if (iDay < s[0]):
            iDay = s[0]
    return iDay


def deleteDaySeries(seriesPrefix, showMessage=True):
    debugMessage("bboLib.deleteDaySeries")
    for iDay in range(1, 367):
        if (((iDay % 20) == 0) and showMessage):
            grass.message("deleting day series: " + rasterDay(seriesPrefix, iDay))
        deleteRaster(rasterDay(seriesPrefix, iDay))


def deleteMonthSeries(seriesPrefix):
    debugMessage("bboLib.deleteMonthSeries")
    for iMonth in range(1, 13):
        deleteRaster(rasterMonth(seriesPrefix, iMonth))


def deleteYearSeries(targetMapset, seriesTemplate, yearFrom, yearTo, printMessage=False):
    debugMessage("bboLib.deleteYearSeries")

    if (printMessage):
        grass.message("delete raster series {0} from {1} to {2}".format(seriesTemplate, yearFrom, yearTo))

    if (seriesTemplate):
        userMapset = grass.gisenv()["MAPSET"]  
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)

        for iYear in range(yearFrom, yearTo + 1):
            deleteRaster(replaceYearParameter(seriesTemplate, iYear))
    
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)


def deleteVectorYearSeries(targetMapset, seriesTemplate, yearFrom, yearTo, printMessage=False):
    debugMessage("bboLib.deleteVectorYearSeries")

    if (printMessage):
        grass.message("delete vector series {0} from {1} to {2}".format(seriesTemplate, yearFrom, yearTo))

    if (seriesTemplate):
        userMapset = grass.gisenv()["MAPSET"]
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)

        for iYear in range(yearFrom, yearTo + 1):
            deleteVector(replaceYearParameter(seriesTemplate, iYear, targetMapset))
    
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)


def getSeriesStatistics(targetMapset, maskTemplate, rasterTemplate, yearFrom, yearTo):
    debugMessage("bboLib.getSeriesStatistics")

    tmpTemplate = "tmp_bbolib_serstat_%Y"
    valStat = None
    rasterNames = None

    if (yearTo < yearFrom):
        return None

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    for iYear in range(yearFrom, yearTo + 1):
        maskFN = replaceYearParameter(maskTemplate, iYear)
        valFN = replaceYearParameter(rasterTemplate, iYear)
        tmpFN = replaceYearParameter(tmpTemplate, iYear)
        if (validateRaster(maskFN) and validateRaster(valFN)):
            grass.mapcalc("$outVal = $mask*$val", outVal=tmpFN, mask=maskFN, val=valFN, overwrite=True)
            if (rasterNames):
                rasterNames = rasterNames + "," + tmpFN
            else:
                rasterNames = tmpFN

    if (rasterNames):
        valStat = getValueStatistics(rasterNames)

    deleteYearSeries(targetMapset, tmpTemplate, yearFrom, yearTo)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return valStat


def showSeriesStatistics(rasterTemplate, yearFrom, yearTo, valStat, logFile=None):
    logMessage("\n", logFile)
    logMessage("value statistics for series {0}".format(rasterTemplate), logFile)
    logMessage("years: {0} - {1}".format(yearFrom, yearTo), logFile)
    logMessage("cells: {0}".format(valStat.cells), logFile)
    logMessage("min: {0}".format(valStat.min), logFile)
    logMessage("max: {0}".format(valStat.max), logFile)
    logMessage("avg: {0}".format(valStat.avg), logFile)
    logMessage("std: {0}".format(valStat.std), logFile)

#endregion



#region #################### GROUP CELLS ####################
def groupCells(srcRaster, grpRaster):
    tmp0 = "tmp_bbolib_groupCells_0"
    tmp1 = "tmp_bbolib_groupCells_1"
    tmp2 = "tmp_bbolib_groupCells_2"
    tmp3 = "tmp_bbolib_groupCells_3"
    
    grass.message("group cells: {0}".format(grpRaster))
    grass.mapcalc("$tmp0 = if(0 < $srcRaster, 1, null())", overwrite=True, tmp0=tmp0, srcRaster=srcRaster)
    grass.run_command("r.clump", overwrite=True, input=tmp0, output=tmp1, flags="d", quiet=True)
    grass.mapcalc("$tmp2 = $tmp0 * $tmp1", tmp0=tmp0, tmp1=tmp1, tmp2=tmp2, overwrite=True)

    deltaArea = 1
    while (0.0 < deltaArea):
        grass.run_command("r.neighbors", input=tmp2, output=tmp1, method="minimum", quiet=True, overwrite=True)
        grass.mapcalc("$tmp3 = $tmp0 * $tmp1", tmp0=tmp0, tmp1=tmp1, tmp3=tmp3, overwrite=True)
        grass.mapcalc("$tmp1 = $tmp2 - $tmp3", tmp1=tmp1, tmp2=tmp2, tmp3=tmp3, overwrite=True)
        grass.run_command("r.null", map=tmp1, setnull=0, quiet=True)
        deltaArea = getNotNullCellsNumber(tmp1)
        grass.mapcalc("$tmp2 = $tmp3", tmp2=tmp2, tmp3=tmp3, overwrite=True)
        debugMessage(str.format("groupCells: {0}", deltaArea))

    grass.mapcalc("$grpRaster = $tmp2", grpRaster=grpRaster, tmp2=tmp2, overwrite=True)

    deleteRaster(tmp3)
    deleteRaster(tmp2)
    deleteRaster(tmp1)
    deleteRaster(tmp0)
#endregion



#region #################### SPOT CLASSIFICATION ####################
def findPreviousSpotYear(year, yearsRange=10):
    debugMessage("bboLib.findPreviousSpotYear")
    
    if (yearsRange < 1):
        return None

    userMapset = grass.gisenv()["MAPSET"]  
    if (not userMapset == forestMapset):
        grass.run_command("g.mapset", mapset=forestMapset)
    
    yearFrom10 = year - yearsRange
    
    y1 = year - 1
    cont = True
    while (cont and (yearFrom10 <= y1)):
        prevSpot = replaceYearParameter(spotTemplate, y1)
        if (validateRaster(prevSpot)):
            cont = False
        else:
            y1 = y1 - 1

    if (not userMapset == forestMapset):
        grass.run_command("g.mapset", mapset=userMapset)
    
    if (cont):
        return None
    else:
        return y1


def findPreviousSpotLayer(year, yearsRange=10):
    debugMessage("bboLib.findPreviousSpotLayer")
    
    if (yearsRange < 1):
        return None

    userMapset = grass.gisenv()["MAPSET"]  
    if (not userMapset == forestMapset):
        grass.run_command("g.mapset", mapset=forestMapset)
    
    yearFrom10 = year - yearsRange
    
    y1 = year - 1
    prevSpot = None
    while (yearFrom10 <= y1):
        prevSpot = replaceYearParameter(spotTemplate, y1)
        if (validateRaster(prevSpot)):
            y1 = yearFrom10 - 1
        else:
            prevSpot = None
        y1 = y1 - 1

    if (not userMapset == forestMapset):
        grass.run_command("g.mapset", mapset=userMapset)
    
    return prevSpot


def cleanSpotDB(yearFrom, yearTo):
    debugMessage("bboLib.cleanSpotDB")
    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == forestMapset:
        grass.run_command("g.mapset", mapset=forestMapset)

    y0 = yearFrom
    while (y0 <= yearTo):
        grass.message(str.format("clean year {0}", y0))
        deleteRaster(replaceYearParameter(eidTemplate, y0))
        deleteRaster(replaceYearParameter(edstTemplate, y0))
        deleteRaster(replaceYearParameter(fidTemplate, y0))
        deleteRaster(replaceYearParameter(fdstTemplate, y0))
        deleteRaster(replaceYearParameter(allspotdstTemplate, y0))
        deleteRaster(replaceYearParameter(allspotdstidTemplate, y0))
        deleteRaster(replaceYearParameter(activespotdstTemplate, y0))
        deleteRaster(replaceYearParameter(activespotdstidTemplate, y0))
        deleteRaster(replaceYearParameter(oldspotdstTemplate, y0))
        deleteRaster(replaceYearParameter(oldspotdstidTemplate, y0))
        deleteRaster(replaceYearParameter(updatedS50MaskTemplate, y0))
        deleteRaster(replaceYearParameter(updatedS50DstTemplate, y0))
        deleteRaster(replaceYearParameter(s50DstTemplate, y0))
        deleteRaster(replaceYearParameter(eactiveSpotTemplate, y0))
        deleteRaster(replaceYearParameter(factiveSpotTemplate, y0))
        y0 = y0 + 1
    
    cleanSpotClassification(yearFrom, yearTo)

    # finish calculation, restore settings
    if not userMapset == forestMapset:
        grass.run_command("g.mapset", mapset=userMapset)


def cleanSpotClassification(yearFrom, yearTo):
    debugMessage("bboLib.cleanSpotClassification")
    deleteYearSeries(forestMapset, spotidTemplate, yearFrom, yearTo)
    deleteYearSeries(forestMapset, updatedS50MaskTemplate, yearFrom, yearTo)


def spotClassificationDataSeries(yearFrom, yearTo):
    if (yearTo < yearFrom):
        grass.fatal("yearFrom must be less or equal to yearTo")

    spotClassificationInit(forestMapset, yearFrom, yearTo, spotPrefix, spotidPrefix)
    spotClassificationSeries(forestMapset, forestMapset, yearFrom, yearTo, spotPrefix, spotidPrefix, spotPrefix, spotidPrefix)


def spotClassificationInit(targetMapset, 
                           yearFrom, yearTo, 
                           aspotPrefix, aspotidPrefix):
    spotY0 = "tmp_bb_spotinit_i0"

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.message("spot classification init")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        actSpot = rasterYear(aspotPrefix, y0)
        if grass.find_file(actSpot + "@" + targetMapset)['file']:
            break;
        y0 = y0 + 1

    if (y0 <= yearTo):
        grass.message("spot classification init {0}".format(actSpot))
        actSpotId = rasterYear(aspotidPrefix, y0)

        grass.mapcalc("$tmp0 = if(0 < $actSpot, 3, null())", overwrite=True, tmp0=spotY0, actSpot=actSpot)
        grass.mapcalc("$actSpot = $tmp0", overwrite=True, actSpot=actSpot, tmp0=spotY0)
        groupCells(spotY0, actSpotId)

        deleteRaster(spotY0)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def spotClassificationSeries(sourceMapset, targetMapset, 
                             yearFrom, yearTo, 
                             pspotPrefix, pspotidPrefix,
                             aspotPrefix, aspotidPrefix):
    grass.message("spot series classification")

    y0 = yearTo
    while (yearFrom <= y0):
        y0Name = rasterYear(pspotidPrefix, y0, sourceMapset)
        if grass.find_file(y0Name)['file']:
            break
        y0 = y0 - 1

    while (y0 < yearTo):
        checkRaster(rasterYear(pspotPrefix, y0), sourceMapset)
        checkRaster(rasterYear(pspotidPrefix, y0), sourceMapset)

        y1 = y0 + 1
        while (y1 <= yearTo):
            y1Name = rasterYear(aspotPrefix, y1, targetMapset)
            if grass.find_file(y1Name)['file']:
                break
            y1 = y1 + 1

        if (y1 <= yearTo):
            actSpot = rasterYear(aspotPrefix, y1, targetMapset)
            checkRaster(actSpot)
            spotClassificationST(sourceMapset, targetMapset, 
                                 y0, pspotPrefix, pspotidPrefix,
                                 y1, aspotPrefix, aspotidPrefix)
        
        y0 = y1


def spotClassificationST(sourceMapset, targetMapset, 
                         y0, pspotPrefix, pspotidPrefix, 
                         y1, aspotPrefix, aspotidPrefix):
    prevSpot = rasterYear(pspotPrefix, y0, sourceMapset)
    prevSpotId = rasterYear(pspotidPrefix, y0, sourceMapset)
    actSpot = rasterYear(aspotPrefix, y1)
    actSpotId = rasterYear(aspotidPrefix, y1)
    
    spotClassificationFN(targetMapset,
                         prevSpot, prevSpotId, 
                         actSpot, actSpotId)


def spotClassificationFN(targetMapset, 
                         prevSpot, prevSpotId, 
                         actSpot, actSpotId,
                         classifySpots=True):
    debugMessage("bboLib.spotClassification")

    if (not classifySpots):
        return

    spotY0 = "tmp_bbolib_spotclass_r0"
    spotY1 = "tmp_bbolib_spotclass_r1"
    spotY2 = "tmp_bbolib_spotclass_r2"
    spotY3 = "tmp_bbolib_spotclass_r3"
    actEId = "tmp_bbolib_spotclass_r4"

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    grass.message("spot classification {0} / {1}".format(actSpot, prevSpot))
    
    grass.mapcalc("$tmp0 = if(0 < $actSpot, if(isnull($prevSpot), 1, null()))", overwrite=True, tmp0=spotY0, prevSpot=prevSpot, actSpot=actSpot)
    groupCells(spotY0, actSpotId)

    grass.mapcalc("$tmp1 = $prevSpotId", overwrite=True, tmp1=spotY1, prevSpotId=prevSpotId)
    area2 = getNotNullCellsNumber(spotY1)
    area1 = 0
    i = 1
    while (area1 != area2):
        debugMessage("iteration: {0}   cells: {1}".format(i, area2))
        area1 = area2
        grass.run_command("r.neighbors", input=spotY1, output=spotY2, method="minimum", quiet=True, overwrite=True)
        grass.mapcalc("$tmp3 = if(isnull($tmp1), $tmp2 * $tmp0, $tmp1)", tmp0=spotY0, tmp1=spotY1, tmp2=spotY2, tmp3=spotY3, overwrite=True)
        grass.mapcalc("$tmp1 = $tmp3", tmp1=spotY1, tmp3=spotY3, overwrite=True)
        area2 = getNotNullCellsNumber(spotY1)
        i = i + 1

    grass.mapcalc("$eid = $tmp1", eid=actEId, tmp1=spotY1, overwrite=True)
    grass.run_command("r.null", map=actEId, setnull=0, quiet=True)
    grass.mapcalc("$tmp0 = if(0 < $actSpot, if(isnull($prevSpot), 2, 0))", overwrite=True, tmp0=spotY0, prevSpot=prevSpot, actSpot=actSpot)
    grass.mapcalc("$tmp1 = if(0 < $actSpot, 1, 0)", overwrite=True, tmp1=spotY1, actSpot=actSpot)
    grass.mapcalc("$tmp2 = if(0 < $eid, if(isnull($prevSpot), 1, 0))", overwrite=True, tmp2=spotY2, prevSpot=prevSpot, eid=actEId)
    grass.run_command("r.null", map=spotY0, null=0, quiet=True)
    grass.run_command("r.null", map=spotY1, null=0, quiet=True)
    grass.run_command("r.null", map=spotY2, null=0, quiet=True)
    grass.mapcalc("$actSpot = $tmp1 + $tmp0 - $tmp2", tmp0=spotY0, tmp1=spotY1, tmp2=spotY2, actSpot=actSpot, overwrite=True)
    grass.run_command("r.null", map=actSpot, setnull=0, quiet=True)
    
    deleteRaster(spotY0)
    deleteRaster(spotY1)
    deleteRaster(spotY2)
    deleteRaster(spotY3)
    deleteRaster(actEId)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
#endregion



#region #################### SPOT AREAS ####################
def spotAreasSeries(yearFrom, yearTo):
    debugMessage("bboLib.spotAreasSeries")
    targetMapset = forestMapset

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    year = yearFrom
    while (year <= yearTo):
        bbSpotArea = replaceYearParameter(spotAreaTemplate, year)
        actSpot = replaceYearParameter(spotTemplate, year)
        actSpotId = replaceYearParameter(spotidTemplate, year)
        deleteRaster(bbSpotArea)
        if (validateRaster(actSpot) and validateRaster(actSpotId)):
            spotAreas(targetMapset, year)
        year = year + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def spotAreas(targetMapset, year):
    # calculates areas in hectares
    debugMessage("bboLib.spotAreas")

    tmp1 = "tmp_bbolib_spotarea_1"
    tmp2 = "tmp_bbolib_spotarea_2"
    actualNSpot = "tmp_bbolib_spotarea_3"
    actualNSpot0 = "tmp_bbolib_spotarea_4"
    actualNSpotGroup = "tmp_bbolib_spotarea_5"

    grass.message("spot areas {0}".format(year))

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    bbSpot = replaceYearParameter(spotTemplate, year)
    bbSpotArea = replaceYearParameter(spotAreaTemplate, year)

    # actual bark beetle spots
    grass.mapcalc("$actualNSpot = if(1 < $bbSpot, 1, null())", actualNSpot=actualNSpot, bbSpot=bbSpot, overwrite=True)
    grass.mapcalc("$actualNSpot0 = $actualNSpot", actualNSpot0=actualNSpot0, actualNSpot=actualNSpot, overwrite=True)
    grass.run_command("r.null", map=actualNSpot0, null=0, quiet=True)

    # size of bark beetle spots
    grass.mapcalc("$tmp1 = $v", tmp1=tmp1, v=getCellArea()/10000.0, overwrite=True)
    grass.run_command("r.clump", overwrite=True, input=actualNSpot, output=tmp2, quiet=True)
    grass.mapcalc("$actualNSpotGroup = $tmp2 * $actualNSpot", actualNSpotGroup=actualNSpotGroup, tmp2=tmp2, actualNSpot=actualNSpot, overwrite=True)
    grass.run_command("r.stats.zonal", overwrite=True, base=actualNSpotGroup, cover=tmp1, output=bbSpotArea, method="sum", quiet=True)
    
    deleteRaster(actualNSpotGroup)
    deleteRaster(actualNSpot0)
    deleteRaster(actualNSpot)
    deleteRaster(tmp2)
    deleteRaster(tmp1)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
#endregion



#region #################### DISTANCE TO SPOTS ####################
def distanceToAllSpotsSeries(targetMapset, yearFrom, yearTo):
    debugMessage("bboLib.distanceToAllSpotsSeries")
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    y = yearFrom
    while (y <= yearTo):
        actSpot = replaceYearParameter(spotTemplate, y)
        actSpotId = replaceYearParameter(spotidTemplate, y)
        spotDst = replaceYearParameter(allspotdstTemplate, y)
        spotDstId = replaceYearParameter(allspotdstidTemplate, y)
        deleteRaster(spotDst)
        deleteRaster(spotDstId)

        if (validateRaster(actSpot) and validateRaster(actSpotId)):
            prevSpot = findPreviousSpotLayer(y)
            if (prevSpot):
                distanceToAllSpots(y, prevSpot, spotDst)

        y = y + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

def distanceToAllSpots(year, prevSpot, spotDst):
    debugMessage("bboLib.distanceToAllSpots")
    
    if (validateRaster(prevSpot)):
        grass.message("distance to all spots {0}".format(year))       
        grass.run_command("r.grow.distance", input=prevSpot, distance=spotDst, quiet=True, overwrite=True)



def distanceToActiveSpotsSeries(targetMapset, yearFrom, yearTo):
    debugMessage("bboLib.distanceToActiveSpotsSeries")
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
      
    y = yearFrom
    while (y <= yearTo):
        spotFN = replaceYearParameter(spotTemplate, y)
        spotIdFN = replaceYearParameter(spotidTemplate, y)
        activespotDst = replaceYearParameter(activespotdstTemplate, y)
        activespotDstId = replaceYearParameter(activespotdstidTemplate, y)
        deleteRaster(activespotDst)
        deleteRaster(activespotDstId)

        if (validateRaster(spotFN) and validateRaster(spotIdFN)):
            prevSpot = findPreviousSpotLayer(y)
            if (prevSpot):
                distanceToActiveSpots(y, prevSpot, activespotDst)

        y = y + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

def distanceToActiveSpots(year, prevSpot, activespotDst):
    tmp1 = "tmp_bbolib_dstactive_1"
        
    if (validateRaster(prevSpot)):
        grass.message("distance to active spots {0}".format(year))

        grass.mapcalc("$tmp1 = if(1 < $prevSpot, 1, null())", overwrite=True, tmp1=tmp1, prevSpot=prevSpot)
        grass.run_command("r.grow.distance", input=tmp1, distance=activespotDst, quiet=True, overwrite=True)
     
        deleteRaster(tmp1)



def distanceToOldSpotsSeries(targetMapset, yearFrom, yearTo):
    debugMessage("bboLib.distanceToOldSpotsSeries")
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
       
    y = yearFrom
    while (y <= yearTo):
        actSpot = replaceYearParameter(spotTemplate, y)
        actSpotId = replaceYearParameter(spotidTemplate, y)
        spotDst = replaceYearParameter(oldspotdstTemplate, y)
        spotDstId = replaceYearParameter(oldspotdstidTemplate, y)
        deleteRaster(spotDst)
        deleteRaster(spotDstId)

        if (validateRaster(actSpot) and validateRaster(actSpotId)):
            prevSpot = findPreviousSpotLayer(y)
            if (prevSpot):
                distanceToOldSpots(y, prevSpot, spotDst)

        y = y + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

def distanceToOldSpots(year, prevSpot, spotDst):
    debugMessage("bboLib.distanceToOldSpots")

    spotY0 = "tmp_bbolib_dstold_y0"

    if (validateRaster(prevSpot)):
        grass.message("distance to old spots {0}".format(year))
        
        grass.mapcalc("$tmp0 = if(1 == $prevSpot, 1, null())", overwrite=True, tmp0=spotY0, prevSpot=prevSpot)
        grass.run_command("r.grow.distance", input=spotY0, distance=spotDst, quiet=True, overwrite=True)
     
        deleteRaster(spotY0)

#endregion



#region ################### FLYING DISTANCE ####################
def flyingDistanceDataSeries(yearFrom, yearTo):
    if (yearTo < yearFrom):
        grass.fatal("yearFrom must less or eaqual to yearTo")

    flyingDistanceSeries(forestMapset, forestMapset, 
                         yearFrom, yearTo, 
                         spotPrefix, spotidPrefix, 
                         spotPrefix, spotidPrefix,
                         fdstPrefix, fidPrefix)


def flyingDistanceSeries(sourceMapset, targetMapset, 
                         yearFrom, yearTo, 
                         pspotPrefix, pspotidPrefix,
                         aspotPrefix, aspotidPrefix,
                         aFDstPrefix, aFIdPrefix):
    grass.message("flying distance series")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        prevSpot = rasterYear(pspotPrefix, y0, sourceMapset)
        if grass.find_file(prevSpot)['file']:
            break;
        y0 = y0 + 1

    while (y0 < yearTo):
        checkRaster(rasterYear(pspotPrefix, y0, sourceMapset))
        checkRaster(rasterYear(pspotidPrefix, y0, sourceMapset))

        y1 = y0 + 1
        while (y1 <= yearTo):
            y1Name = rasterYear(aspotPrefix, y1, targetMapset)
            if grass.find_file(y1Name)['file']:
                break
            y1 = y1 + 1

        if (y1 <= yearTo):
            flyingDistanceST(sourceMapset, targetMapset, 
                             y0, pspotPrefix, pspotidPrefix,
                             y1, aspotPrefix, aspotidPrefix,
                             aFDstPrefix, aFIdPrefix)
        
        y0 = y1


def flyingDistanceST(sourceMapset, targetMapset, 
                     y0, pspotPrefix, pspotidPrefix, 
                     y1, aspotPrefix, aspotidPrefix,
                     aFDstPrefix, aFIdPrefix):
    prevSpot = rasterYear(pspotPrefix, y0, sourceMapset)
    prevSpotId = rasterYear(pspotidPrefix, y0, sourceMapset)
    actSpot = rasterYear(aspotPrefix, y1)
    actSpotId = rasterYear(aspotidPrefix, y1)
    actFDst = rasterYear(aFDstPrefix, y1)
    actFId = rasterYear(aFIdPrefix, y1)
    
    flyingDistanceFN(targetMapset,
                     prevSpot, prevSpotId, 
                     actSpot, actSpotId,
                     actFDst, actFId)


def flyingDistanceFN(targetMapset, 
                     prevSpot, prevSpotId, 
                     actSpot, actSpotId, 
                     actFDst, actFId):
    spotY0 = "tmp_bbolib_fdst_d0"
    spotY1 = "tmp_bbolib_fdst_d1"
    spotY2 = "tmp_bbolib_fdst_d2"
    spotY3 = "tmp_bbolib_fdst_d3"
    spotY4 = "tmp_bbolib_fdst_d4"

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    grass.message("flying distance {0} / {1}".format(actSpot, prevSpot))
     
    # flying distance
    grass.mapcalc("$tmp1 = if(3 == $actSpot, 1, null())", overwrite=True, tmp1=spotY1, actSpot=actSpot)
    grass.mapcalc("$tmp2 = if(1 < $prevSpot, 1, null())", overwrite=True, tmp2=spotY2, prevSpot=prevSpot)
    grass.mapcalc("$tmp0 = $tmp2 * $prevSpotId", overwrite=True, tmp0=spotY0, tmp2=spotY2, prevSpotId=prevSpotId)
    grass.run_command("r.grow.distance", input=spotY0, distance=spotY3, value=spotY4, quiet=True, overwrite=True)
    grass.mapcalc("$fdst = $tmp1 * $tmp3", tmp1=spotY1, tmp3=spotY3, fdst=actFDst, overwrite=True)
    grass.mapcalc("$fid = $tmp1 * $tmp4", tmp1=spotY1, tmp4=spotY4, fid=actFId, overwrite=True)
    grass.run_command("r.null", map=actFDst, setnull=0, quiet=True)
    grass.run_command("r.null", map=actFId, setnull=0, quiet=True)

    deleteRaster(spotY0)
    deleteRaster(spotY1)
    deleteRaster(spotY2)
    deleteRaster(spotY3)
    deleteRaster(spotY4)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
#endregion



#region #################### ENLARGEMENT DISTANCE ####################
def enlargementDistanceDataSeries(yearFrom, yearTo):
    if (yearTo < yearFrom):
        grass.fatal("yearFrom must less or eaqual to yearTo")

    enlargementDistanceSeries(forestMapset, forestMapset, 
                              yearFrom, yearTo, 
                              spotPrefix, spotidPrefix, 
                              spotPrefix, spotidPrefix,
                              edstPrefix, eidPrefix)


def enlargementDistanceSeries(sourceMapset, targetMapset, 
                              yearFrom, yearTo, 
                              pspotPrefix, pspotidPrefix,
                              aspotPrefix, aspotidPrefix,
                              aEDstPrefix, aEIdPrefix):
    debugMessage("bboLib.enlargement distance series")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        prevSpot = rasterYear(pspotPrefix, y0, sourceMapset)
        if grass.find_file(prevSpot)['file']:
            break;
        y0 = y0 + 1

    while (y0 < yearTo):
        checkRaster(rasterYear(pspotPrefix, y0, sourceMapset))
        checkRaster(rasterYear(pspotidPrefix, y0, sourceMapset))

        y1 = y0 + 1
        while (y1 <= yearTo):
            y1Name = rasterYear(aspotPrefix, y1, targetMapset)
            if grass.find_file(y1Name)['file']:
                break
            y1 = y1 + 1

        if (y1 <= yearTo):
            enlargementDistanceST(sourceMapset, targetMapset, 
                                  y0, pspotPrefix, pspotidPrefix,
                                  y1, aspotPrefix, aspotidPrefix,
                                  aEDstPrefix, aEIdPrefix)
        
        y0 = y1


def enlargementDistanceST(sourceMapset, targetMapset, 
                          y0, pspotPrefix, pspotidPrefix, 
                          y1, aspotPrefix, aspotidPrefix,
                          aEDstPrefix, aEIdPrefix):
    prevSpot = rasterYear(pspotPrefix, y0, sourceMapset)
    prevSpotId = rasterYear(pspotidPrefix, y0, sourceMapset)
    actSpot = rasterYear(aspotPrefix, y1)
    actSpotId = rasterYear(aspotidPrefix, y1)
    actEDst = rasterYear(aEDstPrefix, y1)
    actEId = rasterYear(aEIdPrefix, y1)
    
    enlargementDistanceFN(targetMapset,
                          prevSpot, prevSpotId, 
                          actSpot, actSpotId,
                          actEDst, actEId)


def enlargementDistanceFN(targetMapset, 
                          prevSpot, prevSpotId, 
                          actSpot, actSpotId, 
                          actEDst, actEId):
    spotY0 = "tmp_bbolib_edst_d0"
    spotY1 = "tmp_bbolib_edst_d1"
    spotY2 = "tmp_bbolib_edst_d2"
    spotY3 = "tmp_bbolib_edst_d3"

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    grass.message("enlargement distance {0} / {1}".format(actSpot, prevSpot))

    #grass.mapcalc("$tmp0 = if(0 < $actSpot, if(isnull($prevSpot), 1, null()))", overwrite=True, tmp0=spotY0, prevSpot=prevSpot, actSpot=actSpot)
    grass.mapcalc("$tmp0 = if(1 < $actSpot, 1, null())", overwrite=True, tmp0=spotY0, actSpot=actSpot)
    grass.mapcalc("$tmp1 = $prevSpotId", overwrite=True, tmp1=spotY1, prevSpotId=prevSpotId)
    area2 = getNotNullCellsNumber(spotY1)
    area1 = 0
    i = 1
    while (area1 != area2):
        debugMessage("iteration: {0}   cells: {1}".format(i, area2))
        area1 = area2
        grass.run_command("r.neighbors", input=spotY1, output=spotY2, method="minimum", quiet=True, overwrite=True)
        grass.mapcalc("$tmp3 = if(isnull($tmp1), $tmp2 * $tmp0, $tmp1)", tmp0=spotY0, tmp1=spotY1, tmp2=spotY2, tmp3=spotY3, overwrite=True)
        grass.mapcalc("$tmp1 = $tmp3", tmp1=spotY1, tmp3=spotY3, overwrite=True)
        area2 = getNotNullCellsNumber(spotY1)
        i = i + 1

    grass.mapcalc("$eid = $tmp1", eid=actEId, tmp1=spotY1, overwrite=True)
    grass.run_command("r.null", map=actEId, setnull=0, quiet=True)
     
    minId = int(getMinValue(actEId))
    maxId = int(getMaxValue(actEId))
    grass.mapcalc("$edst = 0", overwrite=True, edst=actEDst)
    if (0 < maxId):
        for id in range(minId, maxId+1):
            grass.mapcalc("$tmp1 = if($eid == $id, 1, null())", overwrite=True, tmp1=spotY1, eid=actEId, id=id)
            area1 = getNotNullCellsNumber(spotY1)
            if (0 < area1):
                grass.message("enlargement distance to group {0}/{1}".format(id, maxId))
                grass.mapcalc("$tmp2 = if($prevSpotId == $id, 1, null())", overwrite=True, tmp2=spotY2, prevSpotId=prevSpotId, id=id)
                grass.run_command("r.grow.distance", input=spotY2, distance=spotY3, quiet=True, overwrite=True)
                grass.mapcalc("$tmp2 = $tmp1 * $tmp3", overwrite=True, tmp1=spotY1, tmp2=spotY2, tmp3=spotY3)
                grass.run_command("r.null", map=spotY2, null=0, quiet=True)
                grass.mapcalc("$tmp0 = $tmp2 + $edst", tmp0=spotY0, tmp2=spotY2, edst=actEDst, overwrite=True)
                grass.mapcalc("$edst = $tmp0", tmp0=spotY0, edst=actEDst, overwrite=True)

    grass.run_command("r.null", map=actEDst, setnull=0, quiet=True)

    grass.mapcalc("$tmp2 = if(2 == $actSpot, 1, null())", overwrite=True, tmp2=spotY2, actSpot=actSpot)
    grass.mapcalc("$tmp1 = $tmp2 * $eid", tmp1=spotY1, tmp2=spotY2, eid=actEId, overwrite=True)
    grass.mapcalc("$eid = $tmp1", tmp1=spotY1, eid=actEId, overwrite=True)

    deleteRaster(spotY0)
    deleteRaster(spotY1)
    deleteRaster(spotY2)
    deleteRaster(spotY3)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
#endregion



#region #################### DISTANCE TO FOREST EDGE ####################
def updateS50MaskSeries(targetMapset, yearFrom, yearTo):
    debugMessage("bboLib.updateS50MaskSeries")
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
        
    y = yearFrom
    while (y <= yearTo):
        actSpot = replaceYearParameter(spotTemplate, y)
        s50Mask = replaceYearParameter(s50MaskTemplate, y)
        updatedS50Mask = replaceYearParameter(updatedS50MaskTemplate, y)
        deleteRaster(updatedS50Mask)

        if (validateRaster(actSpot) and validateRaster(s50Mask)):
            prevSpot = findPreviousSpotLayer(y)
            if (prevSpot):
                updateS50Mask(y, s50Mask, prevSpot, updatedS50Mask)
        
        y = y + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

def updateS50Mask(year, s50Mask, prevSpot, updatedS50Mask):
    debugMessage("bboLib.updateS50Mask")

    tmp1 = "tmp_s50mask_tmp1"
    prevSpot0 = "tmp_s50mask_tmp2"
  
    if (validateRaster(prevSpot) and validateRaster(s50Mask)):
        grass.message("Update spruce forest mask {0}".format(year))

        # prepare actualSpot
        grass.mapcalc("$tmp1 = $prevSpot * $s50Mask", tmp1=tmp1, prevSpot=prevSpot, s50Mask=s50Mask, overwrite=True)
        grass.mapcalc("$prevSpot0 = if(0 < $tmp1, 1, null())", prevSpot0=prevSpot0, tmp1=tmp1, overwrite=True)
        grass.run_command("r.null", map=prevSpot0, null=0, quiet=True)
        
        # update spruce forest mask
        grass.mapcalc("$updatedS50Mask = $s50Mask - $prevSpot0", updatedS50Mask=updatedS50Mask, s50Mask=s50Mask, prevSpot0=prevSpot0, overwrite=True)
        grass.run_command("r.null", map=updatedS50Mask, setnull=0, quiet=True)

        deleteRaster(tmp1)
        deleteRaster(prevSpot0)


def updateS50DistanceSeries(targetMapset, yearFrom, yearTo):
    debugMessage("bboLib.updateS50DistanceSeries")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    y = yearFrom
    while (y <= yearTo):
        updatedS50Dst = replaceYearParameter(updatedS50DstTemplate, y)
        deleteRaster(updatedS50Dst)

        actSpot = replaceYearParameter(spotTemplate, y)
        updatedS50Mask = replaceYearParameter(updatedS50MaskTemplate, y)

        if (validateRaster(actSpot) and validateRaster(updatedS50Mask)):
            updateS50Distance(y, updatedS50Mask, updatedS50Dst)

        y = y + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

def updateS50Distance(year, updatedS50Mask, updatedS50Dst):
    debugMessage("bboLib.updateS50Distance")

    tmp1 = "tmp_s50dst_dst1"
    tmp2 = "tmp_s50dst_dst2"
    updatedS50MaskInv = "tmp_s50dst_s50mask_inv"

    if (validateRaster(updatedS50Mask)):
        grass.message("Update distance to spruce forest edge {0}".format(year))
       
        # distance to actual forest edge
        grass.mapcalc("$updatedS50MaskInv = $updatedS50Mask", updatedS50MaskInv=updatedS50MaskInv, updatedS50Mask=updatedS50Mask, overwrite=True)
        grass.run_command("r.null", map=updatedS50MaskInv, setnull=1, null=1, quiet=True)
        grass.run_command("r.grow.distance",input=updatedS50MaskInv, distance=tmp1, quiet=True, overwrite=True)
        grass.mapcalc("$tmp2 = $updatedS50Mask * $tmp1", tmp2=tmp2, updatedS50Mask=updatedS50Mask, tmp1=tmp1, overwrite=True)
        grass.run_command("r.grow.distance",input=updatedS50Mask, distance=tmp1, quiet=True, overwrite=True)
        grass.run_command("r.patch", input=tmp2 + ',' + tmp1, output=updatedS50Dst, quiet=True, overwrite=True)

        deleteRaster(tmp1)
        deleteRaster(tmp2)
        deleteRaster(updatedS50MaskInv)
#endregion



#region #################### GARRAY ####################
class garray(numpy.memmap):
    def __new__(cls, mapname, dtype=numpy.double):
        reg = grass.region()
        nrows = reg['rows']
        ncols = reg['cols']
        shape = (nrows, ncols)
        flags = 'f'
        size = 8
        filename = grass.tempfile()
        if (mapname): 
            grass.run_command("r.out.bin", flags=flags, input=mapname, output=filename, null=None, bytes=size, quiet=True, overwrite=True)
            self = numpy.memmap.__new__(cls, filename=filename, dtype=dtype, mode='r', shape=shape)
        else:
            self = numpy.memmap.__new__(cls, filename=filename, dtype=dtype, mode='w+', shape=shape)
        self.filename = filename
        return self

    def _close(self):
        numpy.memmap._close(self)
        if isinstance(self, garray):
            grass.try_remove(self.filename)

    def read(self, mapname, null=None):
        kind = self.dtype.kind
        size = self.dtype.itemsize

        if kind == 'f':
            flags = 'f'
        elif kind in 'biu':
            flags = 'i'
        else:
            raise ValueError("Invalid kind {0}".format(kind))

        if size not in [1, 2, 4, 8]:
            raise ValueError("Invalid size {0}".format(size))

        try:
            grass.run_command('r.out.bin', flags=flags, input=mapname, output=self.filename, null=null, bytes=size, quiet=True, overwrite=True)
        except Exception as e:
            grass.message(e)
            return 1
        else:
            return 0

    def write(self, mapname, title=None, null=None, overwrite=None):
        kind = self.dtype.kind
        size = self.dtype.itemsize

        if kind == 'f':
            if size == 4:
                flags = 'f'
            elif size == 8:
                flags = 'd'
            else:
                raise ValueError("Invalid FP size {0}".format(size))
            size = None
        elif kind in 'biu':
            if size not in [1, 2, 4]:
                raise ValueError("Invalid integer size {0})".format(size))
            flags = None
        else:
            raise ValueError("Invalid kind {0}".format(kind))

        reg = grass.region()

        try:
            grass.run_command("r.in.bin", flags=flags, input=self.filename, output=mapname, title=title, bytes=size, anull=null, overwrite=overwrite, north=reg['n'],
                               south=reg["s"], east=reg["e"], west=reg["w"], rows=reg["rows"], cols=reg["cols"]) 
        except Exception as e:
            grass.message(e)
            return 1
        else:
            return 0

def readMapSeries(mapPrefix, dayFrom, dayTo, iRow, iCol):
    #grass.message("loading series {0} row={1} col={2}".format(mapPrefix, iRow, iCol))
    valSeries = list()
    for iDay in range(dayFrom, dayTo + 1):
        mapFN = rasterDay(mapPrefix, iDay)
        if grass.find_file(mapFN)['file']:
            mapR = garray(mapFN)
            val = mapR[iRow, iCol]
            valSeries.append((iDay, val))
    return valSeries

def seriesToMap3d(mapPrefix, sourceMapset, outFN):
    maps = ""
    for iDay in range(1, 366):
        mapFN = rasterDay(mapPrefix, iDay) + "@" + sourceMapset
        if (0 == len(maps)):
            maps = mapFN
        else:
            maps = maps + "," + mapFN
    grass.run_command('r.to.rast3', input=maps, output=outFN, override=True)


class garray3d(numpy.memmap):
    def __new__(cls, nLays, dtype=numpy.double):
        reg = grass.region()
        nRows = reg['rows']
        nCols = reg['cols']
        #shape = (nLays, nRows, nCols)
        shape = (garray3DMaxRows, nRows, nCols)
        filename = grass.tempfile()
        self = numpy.memmap.__new__(cls, filename=filename, dtype=dtype, mode='w+', shape=shape)
        self.filename = filename
        return self

    def _close(self):
        numpy.memmap._close(self)
        if isinstance(self, garray):
            grass.try_remove(self.filename)

    def readMapSeries(self, mapPrefix, dayFrom, dayTo):
        reg = grass.region()
        nRows = reg['rows']
        nCols = reg['cols']
        for iDay in range(dayFrom, dayTo+1):
            mapFN = rasterDay(mapPrefix, iDay)
            grass.message("garray3D: reading map {0}".format(mapFN))
            i = iDay - dayFrom
            mapR = garray(mapFN)
            for r in range(nRows):
                for c in range(nCols):
                    self[i, r, c] = mapR[r, c]

    def getSeries(self, dayFrom, dayTo, iRow, iCol):
        valSeries = list()
        i = 0
        for iDay in range(dayFrom, dayTo+1):
            val = self[i, iRow, iCol]
            valSeries.append((iDay, val))
            i = i + 1
        return valSeries
#endregion



#region #################### VEGETATION INDEX ####################

def copyLandsat(sourceMapset, sourceTemplate, 
                targetMapset, targetTemplate,
                yearFrom, yearTo, 
                bandFrom, bandTo):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.message("copy LANDSAT images")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        b0 = bandFrom
        while (b0 <= bandTo):
            sourceImage = replaceYearBandParameter(sourceTemplate, y0, b0, sourceMapset)
            targetImage = replaceYearBandParameter(targetTemplate, y0, b0)
            if grass.find_file(sourceImage)['file']:
                grass.message("copy image {0} -> {1}".format(sourceImage, targetImage))
                grass.mapcalc("$target = $source", target=targetImage, source=sourceImage, overwrite=True)
            b0 = b0 + 1
        y0 = y0 + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def calcNDVI(targetMapset, bandTemplate, ndviTemplate, yearFrom, yearTo):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.message("calculate NDVI")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        b3Image = replaceYearBandParameter(bandTemplate, y0, 3)
        b4Image = replaceYearBandParameter(bandTemplate, y0, 4)
        ndviImage = replaceYearParameter(ndviTemplate, y0)
        if grass.find_file(b3Image)['file']:
            if grass.find_file(b4Image)['file']:
                grass.message("NDVI {0}".format(str(y0)))
                grass.run_command("i.vi", red=b3Image, nir=b4Image, output=ndviImage, viname="ndvi", overwrite=True)
        y0 = y0 + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def calcVCI(targetMapset, bandTemplate, vciTemplate, yearFrom, yearTo):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.message("calculate VCI")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        b4Image = replaceYearBandParameter(bandTemplate, y0, 4)
        b7Image = replaceYearBandParameter(bandTemplate, y0, 7)
        vciImage = replaceYearParameter(vciTemplate, y0)
        if grass.find_file(b4Image)['file']:
            if grass.find_file(b7Image)['file']:
                grass.message("VCI {0}".format(str(y0)))
                grass.mapcalc("$vci = $b7 / $b4", vci=vciImage, b4=b4Image, b7=b7Image, overwrite=True)
        y0 = y0 + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def calcNSC2(targetMapset, bandTemplate, nsc2Template, yearFrom, yearTo):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.message("calculate NSC2")
    
    y0 = yearFrom
    while (y0 <= yearTo):
        b1Image = replaceYearBandParameter(bandTemplate, y0, 1)
        b2Image = replaceYearBandParameter(bandTemplate, y0, 2)
        b3Image = replaceYearBandParameter(bandTemplate, y0, 3)
        b4Image = replaceYearBandParameter(bandTemplate, y0, 4)
        b5Image = replaceYearBandParameter(bandTemplate, y0, 5)
        b7Image = replaceYearBandParameter(bandTemplate, y0, 7)
        nsc2Image = replaceYearParameter(nsc2Template, y0)
        if grass.find_file(b1Image)['file'] and grass.find_file(b2Image)['file'] and grass.find_file(b3Image)['file']:
            if grass.find_file(b4Image)['file'] and grass.find_file(b5Image)['file'] and grass.find_file(b7Image)['file']:
                grass.message("nsc2 {0}".format(str(y0)))
                grass.mapcalc("$nsc2 = ( 0.1283 * $b1 ) + ( 0.1126 * $b2 ) + ( 0.3487 * $b3 ) - ( 0.5011 * $b4 ) + ( 0.5352 * $b5 ) + ( 0.5581 * $b7 )", 
	                          nsc2=nsc2Image, 
                              b1=b1Image, b2=b2Image, b3=b3Image, b4=b4Image, b5=b5Image, b7=b7Image, overwrite=True)
        y0 = y0 + 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

#endregion
