#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bboPrognosisLib
# AUTHOR(S):	Milan Koren, Rastislav Jakus, Miroslav Blazenec
# PURPOSE:      Prognosis routines library
# COPYRIGHT:	This program is free software under the GNU General Public
#		        License (>=v2). Read the file COPYING that comes with GRASS
#		        for details.
#
#############################################################################

# REMARKS
# Probability model is calculated from data related to a given year
#

#v.db.update map=bb_vcsamples_1984@shp layer=1 column=pspread value=0

import sys
import os
import json
import grass.script as grass
import math
import collections
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib


# #################### PARAMETERS ####################
#region PARAMETERS
# maximal number of steps
SPOT_PROGNOSIS_NSTEPS = 25

# attribute null value
ATTRIBUTENULLVALUE = -99999.9
PROGNOSISNULLVALUE = -9

# spot categories
OLD_SPOTCODE = 1
SPREAD_SPOTCODE = 2
INIT_SPOTCODE = 3
# extended spot codes, used for mask calculation
ALL_SPOTCODE = 4
NEW_SPOTCODE = 5


# probability prognosis methods
PROGMETHODCODE_NONE = 0
PROGMETHODCODE_LINEAR = 1
PROGMETHODCODE_RESISTANCE = 2
PROGMETHODCODE_WEIGHTEDPP = 3

# machine learning methods
PROGMETHODCODE_LR = 51
PROGMETHODCODE_LDA = 52
PROGMETHODCODE_QDA = 53
PROGMETHODCODE_KNC = 54
PROGMETHODCODE_GNB = 55
PROGMETHODCODE_DTC = 56
PROGMETHODCODE_DTR = 57
PROGMETHODCODE_RFC = 58
PROGMETHODCODE_RFR = 59
PROGMETHODCODE_ETC = 60
PROGMETHODCODE_ETR = 61
PROGMETHODCODE_GBC = 62
PROGMETHODCODE_GBR = 63
PROGMETHODCODE_SVC = 64
PROGMETHODCODE_EC = 65
PROGMETHODCODE_ER = 66

# experimental methods
PROGMETHODCODE_INVSCALE = 98
PROGMETHODCODE_SCALE = 99


# weighted paralell-piped parameters
WPP_STDMULTI = 1.0
WPP_METHOD = 201


# attack probability from init and spread
ATTACKPROGMETHODCODE_MAX = 201
ATTACKPROGMETHODCODE_MIN = 202
ATTACKPROGMETHODCODE_MULT = 203
ATTACKPROGMETHODCODE_AVG = 204


# spot prognosis methods
SPOTPROGMETHODCODE_MAXPROBABILITY = 301
SPOTPROGMETHODCODE_RANDOMTODISTANCE = 302
SPOTPROGMETHODCODE_RANDOMGROWING = 303
SPOTPROGMETHODCODE_ATTACKTODISTANCE = 304
SPOTPROGMETHODCODE_MAXINITSPREADPROB = 305


HSMMETHODCODE_DISTANCELIMIT = 401

# model parameters
PROJECT_LOG_TEMPLATE = "_log.txt"
INITMODELPARAMETERSPOSTFIX = "_iparameters.json"
SPREADMODELPARAMETERSPOSTFIX = "_sparameters.json"
ATTACKMODELPARAMETERSPOSTFIX = "_aparameters.json"
HSMMODELPARAMETERSPOSTFIX = "_hsmparameters.json"


# spot initialization parameters
INIT_MSG_TEMPLATE = "\nprobability of spot initialization {0}"
INIT_LOG_TEMPLATE = "_log_init.txt"
INIT_PROBABILITY_TEMPLATE = "_pinit_%Y"
INIT_AREA_TEMPLATE = "_initarea_%Y"
INIT_POTENTIAL_TEMPLATE = "_initpot_%Y"
INIT_RESISTANCE_TEMPLATE = "_initres_%Y"
INIT_COSTDST_TEMPLATE = "_initcostdst_%Y"
INIT_MODEL_YEARPARAMS_TEMPLATE = "_imodel_%Y.par"
INIT_HSM_TEMPLATE = "_ihsm_%Y"


# spot spread parameters
SPREAD_MSG_TEMPLATE = "\nprobability of spot spread {0}"
SPREAD_LOG_TEMPLATE = "_log_spread.txt"
SPREAD_PROBABILITY_TEMPLATE = "_pspread_%Y"
SPREAD_AREA_TEMPLATE = "_spreadarea_%Y"
SPREAD_POTENTIAL_TEMPLATE = "_spreadpot_%Y"
SPREAD_RESISTANCE_TEMPLATE = "_spreadres_%Y"
SPREAD_COSTDST_TEMPLATE = "_spreadcostdst_%Y"
SPREAD_MODEL_YEARPARAMS_TEMPLATE = "_smodel_%Y.par"
SPREAD_HSM_TEMPLATE = "_shsm_%Y"


# attack parameters
ATTACK_MSG_TEMPLATE = "\nprobability of bark beetle attack {0}"
ATTACK_LOG_TEMPLATE = "_log_attack.txt"
ATTACK_OUTPUT_TEMPLATE = "_pattack_%Y"
ATTACK_AREA_TEMPLATE = "_aarea_%Y"
ATTACK_POTENTIAL_TEMPLATE = "_apot_%Y"
ATTACK_RESISTANCE_TEMPLATE = "_ares_%Y"
ATTACK_COSTDST_TEMPLATE = "_acostdst_%Y"
ATTACK_MODEL_YEARPARAMS_TEMPLATE = "_amodel_%Y.par"
ATTACK_HSM_TEMPLATE = "_ahsm_%Y"


# prognosis parameters
progMethod = "progMethod"
progMaxDistance = "progMaxDistance"
# standard/neutral
progSpot = "progSpot"
progSpotId = "progSpotId"
progEDst = "progEDst"
progEId = "progEId"
progFDst = "progFDst"
progFId = "progFId"
progSpotTemplate = "_spot_%Y"
progSpotIdTemplate = "_spotid_%Y"
progEDstTemplate = "_edst_%Y"
progEIdTemplate = "_eid_%Y"
progFDstTemplate = "_fdst_%Y"
progFIdTemplate = "_fdstid_%Y"
# pesimistics
progPSpot = "progPSpot"
progPSpotId = "progPSpotId"
progPEDst = "progPEDst"
progPEId = "progPEId"
progPFDst = "progPFDst"
progPFId = "progPFId"
progPSpotTemplate = "_pspot_%Y"
progPSpotIdTemplate = "_pspotid_%Y"
progPEDstTemplate = "_pedst_%Y"
progPEIdTemplate = "_peid_%Y"
progPFDstTemplate = "_pfdst_%Y"
progPFIdTemplate = "_pfdstid_%Y"
# optimistics
progOSpot = "progOSpot"
progOSpotId = "progOSpotId"
progOEDst = "progOEDst"
progOEId = "progOEId"
progOFDst = "progOFDst"
progOFId = "progOFId"
progOSpotTemplate = "_ospot_%Y"
progOSpotIdTemplate = "_ospotid_%Y"
progOEDstTemplate = "_oedst_%Y"
progOEIdTemplate = "_oeid_%Y"
progOFDstTemplate = "_ofdst_%Y"
progOFIdTemplate = "_ofdstid_%Y"


# samples
SAMPLES_TEMPLATE = "bb_rsamples_%Y"
RASTER_TRAINING_SAMPLES_TEMPLATE = "bb_tsamples_%Y"
RASTER_CONTROL_SAMPLES_TEMPLATE = "bb_csamples_%Y"

VECTOR_SAMPLES_TEMPLATE = "bb_vsamples_%Y"
VECTOR_TRAINING_SAMPLES_TEMPLATE = "bb_vtsamples_%Y"
VECTOR_CONTROL_SAMPLES_TEMPLATE = "bb_vcsamples_%Y"

ASCII_SAMPLES_FILENAME = "bb_samples.asc"
ASCII_SAMPLES_TEMPLATE = "bb_samples_%Y.asc"
ASCII_CONTROL_SAMPLES_TEMPLATE = "bb_csamples_%Y.asc"
ASCII_TRAINING_SAMPLES_TEMPLATE = "bb_tsamples_%Y.asc"

CSV_SAMPLES_FILENAME = "bb_samples.csv"
CSV_TRAINING_SAMPLES_FILENAME = "bb_samples_training.csv"
CSV_CONTROL_SAMPLES_FILENAME = "bb_samples_control.csv"
CSV_SAMPLES_TEMPLATE = "bb_samples_%Y.csv"
CSV_CONTROL_SAMPLES_TEMPLATE = "bb_csamples_%Y.csv"
CSV_TRAINING_SAMPLES_TEMPLATE = "bb_tsamples_%Y.csv"

SAMPLES_ABUNDANCE_COLUMN_NAME = "abundance"
SAMPLES_PINIT_COLUMN_NAME = "pinit"
SAMPLES_PSPREAD_COLUMN_NAME = "pspread"
SAMPLES_PATTACK_COLUMN_NAME = "pattack"
SAMPLES_HSM_COLUMN_NAME = "hsm"
SAMPLES_PROG_COLUMN_NAME = "prog"
SAMPLES_YEAR_COLUMN_NAME = "year"
SAMPLES_TRAINING_COLUMN_NAME = "train"
SAMPLES_PRESENCE_COLUMN_NAME = "presence"

# training
TRAINING_ISM_LOG_TEMPLATE = "_train.txt"
TRAINING_ISM_AUC_TEMPLATE = "_train_auc.csv"
TRAINING_ISM_CROSSTAB_TEMPLATE = "_train_ctab.csv"

TRAINING_ATTACK_LOG_TEMPLATE = "_atrain.txt"
TRAINING_ATTACK_AUC_TEMPLATE = "_atrain_auc.csv"
TRAINING_ATTACK_SUMCTAB_TEMPLATE = "_atrain_sumctab.csv"
TRAINING_ATTACK_CTAB_TEMPLATE = "_atrain_ctab.csv"

TRAINING_SPREAD_LOG_TEMPLATE = "_strain.txt"
TRAINING_SPREAD_AUC_TEMPLATE = "_strain_auc.csv"
TRAINING_SPREAD_CROSSTAB_TEMPLATE = "_strain_ctab.csv"

TRAINING_INIT_LOG_TEMPLATE = "_itrain.txt"
TRAINING_INIT_AUC_TEMPLATE = "_itrain_auc.csv"
TRAINING_INIT_CROSSTAB_TEMPLATE = "_itrain_ctab.csv"

TRAINING_INITLAYERS_LOG_TEMPLATE = "_ilay_train.txt"
TRAINING_INITLAYERS_AUC_TEMPLATE = "_ilay_train_auc.csv"
TRAINING_INITLAYERS_CROSSTAB_TEMPLATE = "_ilay_train_ctab.csv"

TRAINING_SPREADLAYERS_LOG_TEMPLATE = "_slay_train.txt"
TRAINING_SPREADLAYERS_AUC_TEMPLATE = "_slay_train_auc.csv"
TRAINING_SPREADLAYERS_CROSSTAB_TEMPLATE = "_slay_train_ctab.csv"

TRAINING_ATTACKLAYERS_LOG_TEMPLATE = "_alay_train.txt"
TRAINING_ATTACKLAYERS_AUC_TEMPLATE = "_alay_train_auc.csv"
TRAINING_ATTACKLAYERS_SUMCTAB_TEMPLATE = "_alay_train_sumctab.csv"
TRAINING_ATTACKLAYERS_CTAB_TEMPLATE = "_alay_train_ctab.csv"

TRAINING_ISMLAYERS_LOG_TEMPLATE = "_islay_train.txt"
TRAINING_ISMLAYERS_AUC_TEMPLATE = "_islay_train_auc.csv"
TRAINING_ISMLAYERS_CROSSTAB_TEMPLATE = "_islay_train_ctab.csv"



def _readProject(projectFN):
    bboLib.debugMessage("bboPrognosisLib._readProject")

    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    projectFN = os.path.join(dbName, locName, "_data\\prognoses", projectFN)
    jsonFile = open(projectFN, "r")
    project = json.load(jsonFile)
    jsonFile.close()
   
    project["logFN"] = project["outputPrefix"] + PROJECT_LOG_TEMPLATE

    project["initModel"]["logFN"] = project["outputPrefix"] + INIT_LOG_TEMPLATE
    project["initModel"]["outputFN"] = project["outputPrefix"] + INIT_PROBABILITY_TEMPLATE
    project["initModel"]["outputArea"] = project["outputPrefix"] + INIT_AREA_TEMPLATE
    project["initModel"]["outputPotential"] = project["outputPrefix"] + INIT_POTENTIAL_TEMPLATE
    project["initModel"]["outputResistance"] = project["outputPrefix"] + INIT_RESISTANCE_TEMPLATE
    project["initModel"]["outputCostDst"] = project["outputPrefix"] + INIT_COSTDST_TEMPLATE
    project["initModel"]["targetMapset"] = project["targetMapset"]
    project["initModel"]["modelYearParams"] = project["outputPrefix"] + INIT_MODEL_YEARPARAMS_TEMPLATE
    project["initModel"]["hsmFN"] = project["outputPrefix"] + INIT_HSM_TEMPLATE

    project["spreadModel"]["logFN"] = project["outputPrefix"] + SPREAD_LOG_TEMPLATE
    project["spreadModel"]["outputFN"] = project["outputPrefix"] + SPREAD_PROBABILITY_TEMPLATE
    project["spreadModel"]["outputArea"] = project["outputPrefix"] + SPREAD_AREA_TEMPLATE
    project["spreadModel"]["outputPotential"] = project["outputPrefix"] + SPREAD_POTENTIAL_TEMPLATE
    project["spreadModel"]["outputResistance"] = project["outputPrefix"] + SPREAD_RESISTANCE_TEMPLATE
    project["spreadModel"]["outputCostDst"] = project["outputPrefix"] + SPREAD_COSTDST_TEMPLATE
    project["spreadModel"]["targetMapset"] = project["targetMapset"]
    project["spreadModel"]["modelYearParams"] = project["outputPrefix"] + SPREAD_MODEL_YEARPARAMS_TEMPLATE
    project["spreadModel"]["hsmFN"] = project["outputPrefix"] + SPREAD_HSM_TEMPLATE

    project["attackModel"]["logFN"] = project["outputPrefix"] + ATTACK_LOG_TEMPLATE
    project["attackModel"]["outputFN"] = project["outputPrefix"] + ATTACK_OUTPUT_TEMPLATE
    project["attackModel"]["outputArea"] = project["outputPrefix"] + ATTACK_AREA_TEMPLATE
    project["attackModel"]["outputPotential"] = project["outputPrefix"] + ATTACK_POTENTIAL_TEMPLATE
    project["attackModel"]["outputResistance"] = project["outputPrefix"] + ATTACK_RESISTANCE_TEMPLATE
    project["attackModel"]["outputCostDst"] = project["outputPrefix"] + ATTACK_COSTDST_TEMPLATE
    project["attackModel"]["targetMapset"] = project["targetMapset"]
    project["attackModel"]["modelYearParams"] = project["outputPrefix"] + ATTACK_MODEL_YEARPARAMS_TEMPLATE
    project["attackModel"]["hsmFN"] = project["outputPrefix"] + ATTACK_HSM_TEMPLATE

    project["spotPrognosis"]["spotFN"] = project["outputPrefix"] + progSpotTemplate
    project["spotPrognosis"]["spotIdFN"] = project["outputPrefix"] + progSpotIdTemplate
    project["spotPrognosis"]["eDstFN"] = project["outputPrefix"] + progEDstTemplate
    project["spotPrognosis"]["eIdFN"] = project["outputPrefix"] + progEIdTemplate
    project["spotPrognosis"]["fDstFN"] = project["outputPrefix"] + progFDstTemplate
    project["spotPrognosis"]["fIdFN"] = project["outputPrefix"] + progFIdTemplate

    project["spotPrognosis"]["pSpotFN"] = project["outputPrefix"] + progPSpotTemplate
    project["spotPrognosis"]["pSpotIdFN"] = project["outputPrefix"] + progPSpotIdTemplate
    project["spotPrognosis"]["pEDstFN"] = project["outputPrefix"] + progPEDstTemplate
    project["spotPrognosis"]["pEIdFN"] = project["outputPrefix"] + progPEIdTemplate
    project["spotPrognosis"]["pFDstFN"] = project["outputPrefix"] + progPFDstTemplate
    project["spotPrognosis"]["pFIdFN"] = project["outputPrefix"] + progPFIdTemplate

    project["spotPrognosis"]["oSpotFN"] = project["outputPrefix"] + progOSpotTemplate
    project["spotPrognosis"]["oSpotIdFN"] = project["outputPrefix"] + progOSpotIdTemplate
    project["spotPrognosis"]["oEDstFN"] = project["outputPrefix"] + progOEDstTemplate
    project["spotPrognosis"]["oEIdFN"] = project["outputPrefix"] + progOEIdTemplate
    project["spotPrognosis"]["oFDstFN"] = project["outputPrefix"] + progOFDstTemplate
    project["spotPrognosis"]["oFIdFN"] = project["outputPrefix"] + progOFIdTemplate

    return project



def _getTemplatesList(maskName, modelParams):
    if maskName is not None:
        templatesLst = [maskName]
    else:
        templatesLst = []
    templatesLst = modelParams["layers"]
    return templatesLst


def _getTemplatesAsString(maskName, modelParams):
    stringLst = ""
    templatesLst = _getTemplatesList(maskName, modelParams)
    for t in templatesLst:
        if len(stringLst) == 0:
            stringLst = t
        else:
            stringLst = stringLst + "," + t
    return stringLst


def _getInitTemplatesList(maskName, project):
    return _getTemplatesList(maskName, project["initModel"])


def _getSpreadTemplatesList(maskName, project):
    return _getTemplatesList(maskName, project["spreadModel"])


def _getInitTemplatesAsString(maskName, project):
    return _getTemplatesAsString(maskName, project["initModel"])


def _getSpreadTemplatesAsString(maskName, project):
    return _getTemplatesAsString(maskName, project["spreadModel"])



def _getInitModelParametersFN(project):
    return project["outputPrefix"] + INITMODELPARAMETERSPOSTFIX


def _getSpreadModelParametersFN(project):
    return project["outputPrefix"] + SPREADMODELPARAMETERSPOSTFIX


def _getAttackModelParametersFN(project):
    return project["outputPrefix"] + ATTACKMODELPARAMETERSPOSTFIX


def _getHSMModelParametersFN(project):
    return project["outputPrefix"] + HSMMODELPARAMETERSPOSTFIX


def _saveModelParameters(fileName, modelName, yearFrom, yearTo, modelParams):
    if (modelParams):
        dbName = grass.gisenv()["GISDBASE"]
        locName = grass.gisenv()["LOCATION_NAME"]
        outputFN = os.path.join(dbName, locName, "_data\\prognoses", fileName)
        params = {}
        params["modelName"] = modelName
        params["yearFrom"] = yearFrom
        params["yearTo"] = yearTo
        params["parameters"] = modelParams
        jsonFile = open(outputFN, "w")
        params = json.dump(params, jsonFile)
        jsonFile.close()

#endregion PARAMETERS



# #################### MODEL ####################
#region MODEL
def buildModel(projectFN):
    bboLib.debugMessage("bboPrognosisLib.buildModel")

    project = _readProject(projectFN)
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    fullLogFileName = bboLib.getFullLogFileName(project["logFN"])
    logFile = open(fullLogFileName, "w")

    useAllSamples = True

    _buildInitModel(project, yearFrom, yearTo, useAllSamples)
    _buildSpreadModel(project, yearFrom, yearTo, useAllSamples)
    _buildAttackModel(project, yearFrom, yearTo, useAllSamples)
    #_assignProbabilitiesToSamples(project)
               
    bboLib.logMessage("", logFile)
    _spotPrognosis(project, project["yearFrom"], project["yearTo"])
    _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)
    bboLib.logMessage("\n", logFile)

    logFile.close()


def runModelPrognosis(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runModelPrognosis")

    project = _readProject(projectFN)
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    #TODO
    bboLib.errorMessage("NOT IMPLEMENTED bboPrognosisLib.runModelPrognosis {} {}".format(yearFrom, yearTo))


def cleanModel(projectFN):
    bboLib.debugMessage("bboPrognosisLib.cleanModel")
    
    project = _readProject(projectFN)
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    _cleanSubmodel(project["initModel"], yearFrom, yearTo)
    _cleanSubmodel(project["spreadModel"], yearFrom, yearTo)
    _cleanSubmodel(project["attackModel"], yearFrom, yearTo)


def _cleanSubmodel(model, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._cleanSubmodel")
    
    targetMapset = model["targetMapset"]
    bboLib.deleteYearSeries(targetMapset, model["outputFN"], yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, model["outputArea"], yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, model["outputPotential"], yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, model["outputResistance"], yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, model["outputCostDst"], yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, model["modelYearParams"], yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, model["hsmFN"], yearFrom, yearTo)
    #TODO delete log files in _data\\prognoses


def _buildSpreadModel(project, yearFrom, yearTo, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._buildSpreadModel")
    if (project["spreadModel"]["method"] < 100):
        modelParams = _calculateModel(project, project["spreadModel"], yearFrom, yearTo, SPREAD_SPOTCODE, SPREAD_MSG_TEMPLATE, useAllSamples)
        _saveModelParameters(_getSpreadModelParametersFN(project), "spreadModel", yearFrom, yearTo, modelParams)


def _buildInitModel(project, yearFrom, yearTo, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._buildInitModel")
    if (project["initModel"]["method"] < 100):
        modelParams = _calculateModel(project, project["initModel"], yearFrom, yearTo, INIT_SPOTCODE, INIT_MSG_TEMPLATE, useAllSamples)
        _saveModelParameters(_getInitModelParametersFN(project), "initModel", yearFrom, yearTo, modelParams)


def _buildAttackModel(project, yearFrom, yearTo, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._buildAttackModel")
    if ((project["attackModel"]["method"] < 100) or ((200 < project["attackModel"]["method"]) and (project["attackModel"]["method"] < 300))):
        modelParams = _calculateModel(project, project["attackModel"], yearFrom, yearTo, NEW_SPOTCODE, ATTACK_MSG_TEMPLATE, useAllSamples)
        _saveModelParameters(_getAttackModelParametersFN(project), "attackModel", yearFrom, yearTo, modelParams)



def _calculateModel(project, model, yearFrom, yearTo, spotCode, msgTemplate, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._calculateModel")

    logFN = model["logFN"]
    prognosisMethod = model["method"]

    fullLogFileName = bboLib.getFullLogFileName(logFN)

    if (prognosisMethod == PROGMETHODCODE_NONE):
        _cleanSubmodel(model, yearFrom, yearTo)
        bboLib.deleteFile(fullLogFileName)
        return None

    logFile = open(fullLogFileName, "w")

    bboLib.logMessage("")

    modelParams = {}
    for year in range(yearFrom, yearTo + 1):
        bboLib.debugMessage("bboPrognosisLib.calcProbability {0}".format(year))
        outRaster = bboLib.replaceYearParameter(model["outputFN"], year)
        bboLib.deleteRaster(outRaster)
        hsmRaster = bboLib.replaceYearParameter(model["hsmFN"], year)
        bboLib.deleteRaster(hsmRaster)
        bbSpot = bboLib.replaceYearParameter(bboLib.spotTemplate, year, bboLib.forestMapset)
        if (bboLib.validateRaster(bbSpot)):
            yearParams = None
            bboLib.logMessage(msgTemplate.format(year), logFile)
            if (prognosisMethod == PROGMETHODCODE_LINEAR):
				# linear regression
                yearParams = _calcProbabilityLinearRegression(model, year, spotCode, logFile, useAllSamples)
            elif (prognosisMethod == PROGMETHODCODE_RESISTANCE):
				# linear regression with resistance
                yearParams = _calcProbabilityResistance(model, year, spotCode, logFile)
            elif (prognosisMethod == PROGMETHODCODE_WEIGHTEDPP):
				# weighted parallelpiped
                yearParams = _calcProbabilityWeightedPP(model, year, spotCode, logFile)
            elif ((50 < prognosisMethod) and (prognosisMethod < 70)):
				# run machine learning method
                yearParams = _calcMLMethod(model, year, spotCode, logFile, useAllSamples)
            elif (prognosisMethod == PROGMETHODCODE_INVSCALE):
				# inverse scale
                _calcProbabilityInverseScale(model, year, logFile)
            elif (prognosisMethod == PROGMETHODCODE_SCALE):
				# scale
                _calcProbabilityScale(model, year, logFile)
            elif (prognosisMethod == ATTACKPROGMETHODCODE_MAX):
				# attack probability max
                yearParams = _attackProbability201(project, year, logFile)
            elif (prognosisMethod == ATTACKPROGMETHODCODE_MIN):
				# attack probability min
                yearParams = _attackProbability202(project, year, logFile)
            elif (prognosisMethod == ATTACKPROGMETHODCODE_MULT):
				# attack probability mult
                yearParams = _attackProbability203(project, year, logFile)
            elif (prognosisMethod == ATTACKPROGMETHODCODE_AVG):
				# attack probability avg
                yearParams = _attackProbability204(project, year, logFile)
            else:
                bboLib.logMessage("Unknown probability calculation method {0}".format(prognosisMethod), logFile)                
                bboLib.logMessage("\n", logFile)
            if (yearParams):
                yearSection = "y{0}".format(year)
                modelParams[yearSection] = yearParams

    if (logFile):
        logFile.close()

    return modelParams



def _printLinearRegressionParams(year, params, layerList, logFile):
    bboLib.logMessage("parameters for year {0}".format(year), logFile)
    b0 = params["b0"].strip()
    bboLib.logMessage("{0}".format(b0), logFile)
    i = 1
    for l in layerList:
        b0 = params["b{0}".format(i)].strip()
        msg = "{0:<20} {1}".format(b0, l)
        bboLib.logMessage(msg, logFile)
        i = i + 1

def _getLinearRegressionCmd(params, layerList):
    b0 = params["b0"].strip()
    i = 1
    cmd = "$spotProb = {0}".format(b0)
    for l in layerList:
        b0 = params["b{0}".format(i)].strip()
        cmd = cmd +" + ({0} * {1})".format(b0, l)
        i = i + 1
    return cmd

def _getLinearRegressionParams(params, layerList):
    modelParams = {}
    modelParams["b0"] = params["b0"].strip()
    i = 1
    for l in layerList:
        k = "b{0}".format(i)
        modelParams[k] = params[k].strip()
        i = i + 1
    return modelParams



def _applyHSM(modelParams, valueLayer, hsmLayer):
    bboLib.debugMessage("bboPrognosisLib._applyHSM")

    tmp = "tmp_bboplib_apphsm1"

    if (bboLib.validateRaster(valueLayer)):
        if (bboLib.validateRaster(hsmLayer)):
            if (modelParams["applyHSM"]):
                grass.mapcalc("$tmp = $val * $hsm", tmp=tmp, val=valueLayer, hsm=hsmLayer, overwrite=True)
                grass.mapcalc("$val = $tmp", tmp=tmp, val=valueLayer, overwrite=True)
                bboLib.deleteRaster(tmp)



def _applyDistanceLimit(modelParams, year, spotCode, logFile=None, trainingYears=1):
    bboLib.debugMessage("bboPrognosisLib._applyDistanceLimit")
    
    buf1 = "tmp_bboplib_cp101_buf"
    tmpMask = "tmp_bboplib_cp101_mask"

    targetMapset = modelParams["targetMapset"]
    outfileTemplate = modelParams["outputFN"]
    distanceLimit = modelParams["distanceLimit"]

    if (targetMapset):
        userMapset = grass.gisenv()["MAPSET"]  
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)
    
    modelParams = None
    if (0.0 < distanceLimit):
        prevSpot = bboLib.findPreviousSpotLayer(year)
        if (prevSpot):
            bboLib.logMessage("distance limit {0}".format(year), logFile)
            outputFN = bboLib.replaceYearParameter(outfileTemplate, year)
            _getSpotMask(year, spotCode, tmpMask, trainingYears)
            grass.run_command("r.buffer", input=tmpMask, output=buf1, distances=distanceLimit, overwrite=True, quiet=True)
            grass.mapcalc("$outLayer = if(0 < $buf, 1, 0)", outLayer=outputFN, buf=buf1, overwrite=True)
            grass.run_command("r.null", map=outputFN, null=0, quiet=True)
            bboLib.deleteRaster(buf1)
            bboLib.deleteRaster(tmpMask)
            modelParams = {"method": HSMMETHODCODE_DISTANCELIMIT}
            modelParams["distanceLimit"] = distanceLimit

    # finish calculation, restore settings
    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)

    return modelParams



# method 1: linear regression
def _calcProbabilityLinearRegression(model, year, spotCode, logFile = None, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._calcProbabilityLinearRegression")

    targetMapset = model["targetMapset"]
    outputFN = bboLib.replaceYearParameter(model["outputFN"], year)
    bboLib.deleteRaster(outputFN)
    layerTemplates = model["layers"]
    trainingYears = model["trainingYears"]

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    tmp1 = "tmp_bboplib_cp1_tmp1"
    cummPrefix = "tmp_bboplib_cp1_c"
    normPrefix = "tmp_bboplib_cp1_n"
    outSamples = "tmp_bboplib_cp1_samples"
    sampleLReg = "tmp_bboplib_cp1_sampleslr"

    # generate samples
    if (not _getTrainingSamplesMask(year, spotCode, sampleLReg, trainingYears, useAllSamples)):
        return

    nSamples = bboLib.getCellsNumber(sampleLReg, 1)
    bboLib.logMessage("number of samples: {0}".format(nSamples), logFile)
    
    if ((2 * len(layerTemplates)) < nSamples):
        layerList = []
        if (trainingYears < 2):
            for l in layerTemplates:
                layerName = bboLib.replaceYearParameter(l, year)
                layerList.append(layerName)
        else:
            i = 0
            for l in layerTemplates:
                cummFN = cummPrefix + str(i)
                _aggregateRasters(l, SAMPLES_TEMPLATE, cummFN, year, None, trainingYears)
                layerList.append(cummFN)
                i = i + 1

        # rescale input rasters
        i = 0
        normLayer = []
        for l in layerList:
            normFN = normPrefix + str(i)
            bboLib.rescaleRaster(l, normFN)
            normLayer.append(normFN)
            i = i + 1

        # calculate multiple linear regression for spot initialization probability   
        params = grass.parse_command("r.regression.multi", mapx=normLayer, mapy=sampleLReg, overwrite=True, quiet=True)

        _printLinearRegressionParams(year, params, layerList, logFile)

        if (1 < trainingYears):
            i = 0
            normLayer = []
            for l in layerTemplates:
                layerFN = bboLib.replaceYearParameter(l, year)
                normFN = normPrefix + str(i)
                bboLib.rescaleRaster(layerFN, normFN)
                normLayer.append(normFN)
                i = i + 1

        cmd = _getLinearRegressionCmd(params, normLayer)
        grass.mapcalc(cmd, overwrite=True, spotProb=tmp1)
        bboLib.rescaleRaster(tmp1, outputFN)

        i = 0
        for l in layerList:
            normFN = normPrefix + str(i)
            bboLib.deleteRaster(normFN)
            cummFN = cummPrefix + str(i)
            bboLib.deleteRaster(cummFN)
            i = i + 1
        
        modelParams = {"method": PROGMETHODCODE_LINEAR}
        modelParams["layers"] = layerTemplates
        modelParams["parameters"] = _getLinearRegressionParams(params, layerList)
    else:
        modelParams = None

    bboLib.deleteRaster(tmp1)
    bboLib.deleteRaster(outSamples)
    bboLib.deleteRaster(sampleLReg)

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return modelParams



# method 2: resistance
def _calcProbabilityResistance(model, year, spotCode, logFile = None):
    bboLib.debugMessage("bboPrognosisLib._calcProbabilityResistance")

    targetMapset = model["targetMapset"]

    outputFN = bboLib.replaceYearParameter(model["outputFN"], year)
    bboLib.deleteRaster(outputFN)
    layerTemplates = model["layers"]
    outputSpreadArea = bboLib.replaceYearParameter(model["outputArea"], year)
    bboLib.deleteRaster(outputSpreadArea)
    outputSpreadPot = bboLib.replaceYearParameter(model["outputPotential"], year)
    bboLib.deleteRaster(outputSpreadPot)
    outputSpreadRes = bboLib.replaceYearParameter(model["outputResistance"], year)
    bboLib.deleteRaster(outputSpreadRes)
    outputSpreadDist = bboLib.replaceYearParameter(model["outputCostDst"], year)
    bboLib.deleteRaster(outputSpreadDist)

    tmp1 = "tmp_bboplib_cprob2_prg1"
    tmp2 = "tmp_bboplib_cprob2_prg2"
    normPrefix = "tmp_bboplib_cprob2_param"

    spotSpreadPot2 = "tmp_bboplib_cprob2_spread_spot2"

    actualSpot = "tmp_bboplib_cprob2_aspt"
    actualSpot0 = "tmp_bboplib_cprob2_aspt0"
    actualNSpot = "tmp_bboplib_cprob2_anspt"
    actualNSpot0 = "tmp_bboplib_cprob2_anspt0"

    actualNSpotGroup = "tmp_bboplib_cprob2_nspot_group"
    actualNSpotArea = "tmp_bboplib_cprob2_nspot_area"

    prevNSpot = "tmp_bboplib_cprob2_pnspt"

    s50Mask = bboLib.replaceYearParameter(bboLib.s50MaskTemplate, year, bboLib.forestMapset)

    prevSpot = bboLib.findPreviousSpotLayer(year)
    if (not prevSpot):
        bboLib.logMessage("cannot calculate actual bark beetle spots {0}".format(year))
        return

    userMapset = grass.gisenv()["MAPSET"] 
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    # prepare actualSpot
    _getSpotMask(year, ALL_SPOTCODE, actualSpot)
    grass.mapcalc("$actualSpot0 = $actualSpot", actualSpot0=actualSpot0, actualSpot=actualSpot, overwrite=True)
    grass.run_command("r.null", map=actualSpot0, null=0, quiet=True)

    # prepare actualNSpot
    _getSpotMask(year, spotCode, actualNSpot)
    grass.mapcalc("$actualNSpot0 = $actualNSpot", actualNSpot0=actualNSpot0, actualNSpot=actualNSpot, overwrite=True)
    grass.run_command("r.null", map=actualNSpot0, null=0, quiet=True)

    # prepare prevNSpot
    grass.mapcalc("$prevNSpot = if(1 < $prevSpot, 1, null())", prevNSpot=prevNSpot, prevSpot=prevSpot, overwrite=True)

    # size of bark beetle spots
    grass.mapcalc("$tmp1 = 1", tmp1=tmp1, overwrite=True)
    grass.run_command("r.clump", overwrite=True, input=actualNSpot, output=tmp2, quiet=True)
    grass.mapcalc("$actualNSpotGroup = $tmp2 * $actualNSpot", actualNSpotGroup=actualNSpotGroup, tmp2=tmp2, actualNSpot=actualNSpot, overwrite=True)
    grass.run_command("r.statistics", overwrite=True, base=actualNSpotGroup, cover=tmp1, output=actualNSpotArea, method="sum", quiet=True)
 
    nSamples = bboLib.getNotNullCellsNumber(actualNSpotArea)
    bboLib.logMessage("number of samples: {0}".format(nSamples), logFile)

    if (3*len(layerTemplates) < nSamples):
        layerList = []
        for l in layerTemplates:
            lr = bboLib.replaceYearParameter(l, year)
            layerList.append(lr)

        # rescale input rasters
        i = 0
        normLayer = []
        for l in layerList:
            nl = normPrefix + str(i)
            normLayer.append(nl)
            bboLib.rescaleRaster(l, nl)
            i = i + 1

        # calculate multiple linear regression for spot potential
        bboLib.debugMessage("multi linear regression")
        params = grass.parse_command("r.regression.multi", mapx=normLayer, mapy=actualNSpotArea, overwrite=True, quiet=True)
        
        cmd = _getLinearRegressionCmd(params, normLayer)
        _printLinearRegressionParams(year, params, layerList, logFile)
        
        grass.mapcalc(cmd, overwrite=True, spotProb=outputSpreadArea)
        bboLib.rescaleRaster(outputSpreadArea, outputSpreadPot)

        # spot spreading resistance
        bboLib.debugMessage("spreading resistance")
        grass.mapcalc("$spotSpreadPot2 = if(0.000001 < $spotSpreadPot, $spotSpreadPot, 0)", overwrite=True,
                      spotSpreadPot2=spotSpreadPot2, spotSpreadPot=outputSpreadPot)
        grass.run_command("r.null", map=spotSpreadPot2, setnull=0, quiet=True)
        grass.mapcalc("$spotSpreadRes = 1.0 / $spotSpreadPot2", overwrite=True,
                      spotSpreadRes=outputSpreadRes, spotSpreadPot2=spotSpreadPot2)
        
        # relative distances
        bboLib.debugMessage("spreading relative resistance")
        grass.run_command("r.cost", input=outputSpreadRes, output=outputSpreadDist, start_rast=prevNSpot, overwrite=True, quiet=True)

        # probability
        bboLib.debugMessage("spreading probability")
        bboLib.rescaleRaster(outputSpreadDist, tmp1)
        grass.mapcalc("$tmp2 = if(0.001 < $tmp1, $tmp1, 0)", overwrite=True, tmp2=tmp2, tmp1=tmp1)
        grass.run_command("r.null", map=tmp2, setnull=0, quiet=True)
        grass.mapcalc("$tmp1 = 1.0 / $tmp2", overwrite=True, tmp1=tmp1, tmp2=tmp2)
        bboLib.rescaleRaster(tmp1, tmp2)
        grass.mapcalc("$spotSpreadProb = $tmp2 * $s50Mask", spotSpreadProb=outputFN, tmp2=tmp2, s50Mask=s50Mask, overwrite=True)
        #grass.mapcalc("$spotSpreadProb = if($actualSpot0, 0, $tmp2)", overwrite=True, spotSpreadProb=spotSpreadProb, actualSpot0=actualSpot0, tmp2=tmp2)

        for l in normLayer:
            bboLib.deleteRaster(l)
        
        modelParams = {"method": PROGMETHODCODE_RESISTANCE}
        modelParams["layers"] = layerTemplates
        modelParams["parameters"] = _getLinearRegressionParams(params, layerList)
    else:
        grass.mapcalc("$spotSpreadProb = 0 * $s50Mask", spotSpreadProb=outputFN, s50Mask=s50Mask, overwrite=True)
        bboLib.logMessage("probability 0", logFile)
        modelParams = None

    bboLib.deleteRaster(prevSpot)
    bboLib.deleteRaster(actualSpot)
    bboLib.deleteRaster(actualSpot0)
    bboLib.deleteRaster(actualNSpot)
    bboLib.deleteRaster(actualNSpot0)

    bboLib.deleteRaster(actualNSpotArea)
    bboLib.deleteRaster(actualNSpotGroup)
    bboLib.deleteRaster(spotSpreadPot2)
    bboLib.deleteRaster(tmp2)
    bboLib.deleteRaster(tmp1)
    bboLib.deleteRaster(prevNSpot)

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
    
    return modelParams



# method 3: weighted parallelpiped
def _calcProbabilityWeightedPP(model, yearTo, spotCode, logFile=None):
    bboLib.debugMessage("bboPrognosisLib._calcProbabilityWeightedPP")

    targetMapset = model["targetMapset"]
    outputFN = bboLib.replaceYearParameter(model["outputFN"], yearTo)
    hsmFN = bboLib.replaceYearParameter(model["hsmFN"], yearTo)
    layerTemplates = model["layers"]
    nYears = model["trainingYears"]
    stdMulti = WPP_STDMULTI
    wppMethod = WPP_METHOD

    if (nYears < 1):
        bboLib.logMessage("weighted parallelpiped: incorrect parameter nYears", logFile)
        return

    bError = False
    maskTemplate = "tmp_bboplib_cp3_m_%Y"

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    yearFrom = yearTo - nYears + 1

    _getSpotMaskSeries(yearFrom, yearTo, spotCode, maskTemplate)

    modelParams = {"method": PROGMETHODCODE_WEIGHTEDPP}
    modelParams["layers"] = layerTemplates
    modelParams["applyHSM"] = model["applyHSM"]
    modelLowerBounds = []
    modelUpperBounds = []

    if (not bError):
        for layerT in layerTemplates:
            valStat = bboLib.getSeriesStatistics(targetMapset, maskTemplate, layerT, yearFrom, yearTo)
            if (valStat is None):
                bboLib.logMessage("parallelpiped: cannot calculate series statistics ({0} {1}-{2})".format(layerT, yearFrom, yearTo), logFile)
                bError = True
            else:
                bboLib.showSeriesStatistics(layerT, yearFrom, yearTo, valStat, logFile)
                if (stdMulti <= 0.0):
                    minVal = valStat.min
                    maxVal = valStat.max
                else:
                    minVal = valStat.avg - stdMulti*valStat.std
                    maxVal = valStat.avg + stdMulti*valStat.std
                modelLowerBounds.append(minVal)
                modelUpperBounds.append(maxVal)

    bboLib.deleteYearSeries(targetMapset, maskTemplate, yearFrom, yearTo)

    if (bError):
        bboLib.deleteRaster(outputFN)
        bboLib.deleteRaster(hsmFN)
        modelParams = None
    else:
        modelParams["parameters"] = { "lowerBounds": modelLowerBounds, "upperBounds": modelUpperBounds }
        _calcWeightedPP(modelParams, yearTo, outputFN, hsmFN, wppMethod)

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return modelParams


def _calcWeightedPP(modelParams, year, outputFN, hsmFN, wppMethod=ATTACKPROGMETHODCODE_MAX):
    bboLib.debugMessage("bboPrognosisLib._calcWeightedPP")

    tmp1FN = "tmp_bboplib_cp3_val1"
    tmp2FN = "tmp_bboplib_cp3_val2"

    layersList = modelParams["layers"]
    lowerBounds = modelParams["parameters"]["lowerBounds"]
    upperBounds = modelParams["parameters"]["upperBounds"]

    if ((wppMethod == ATTACKPROGMETHODCODE_MIN) or (wppMethod == ATTACKPROGMETHODCODE_MULT)):
        grass.mapcalc("$out = 1", out=outputFN, overwrite=True)
    else:
        grass.mapcalc("$out = 0", out=outputFN, overwrite=True)

    nLayers = len(layersList)
    iLayer = 0
    while (iLayer < nLayers):
        valFN = bboLib.replaceYearParameter(layersList[iLayer], year)
        a = (upperBounds[iLayer] + lowerBounds[iLayer]) / 2.0
        r = a - lowerBounds[iLayer]
        if (0.0 < r):
            grass.mapcalc("$tmp1 = if(isnull($val), 0, if($val<$min, 0, if($max<$val, 0, if($val<$avg, ($val-$min)/$r, ($max-$val)/$r))))", 
                          tmp1=tmp1FN, val=valFN, min=lowerBounds[iLayer], max=upperBounds[iLayer], avg=a, r=r, overwrite=True)
            if (wppMethod == ATTACKPROGMETHODCODE_MIN):
                grass.mapcalc("$tmp2 = min($out, $tmp1)", tmp2=tmp2FN, tmp1=tmp1FN, out=outputFN, overwrite=True)
            elif (wppMethod == ATTACKPROGMETHODCODE_MAX):
                grass.mapcalc("$tmp2 = max($out, $tmp1)", tmp2=tmp2FN, tmp1=tmp1FN, out=outputFN, overwrite=True)
            elif (wppMethod == ATTACKPROGMETHODCODE_MULT):
                grass.mapcalc("$tmp2 = $out * $tmp1", tmp2=tmp2FN, tmp1=tmp1FN, out=outputFN, overwrite=True)
            elif (wppMethod == ATTACKPROGMETHODCODE_AVG):
                grass.mapcalc("$tmp2 = $out + $tmp1", tmp2=tmp2FN, tmp1=tmp1FN, out=outputFN, overwrite=True)
            grass.mapcalc("$out = $tmp2", tmp2=tmp2FN, out=outputFN, overwrite=True)
        iLayer = iLayer + 1
    
    if ((wppMethod == ATTACKPROGMETHODCODE_AVG) and (0 < nLayers)):
        grass.mapcalc("$tmp2 = $out / $cnt", tmp2=tmp2FN, out=outputFN, cnt=nLayers, overwrite=True)
        grass.mapcalc("$out = $tmp2", tmp2=tmp2FN, out=outputFN, overwrite=True)
    
    grass.mapcalc("$out = 1", out=hsmFN, overwrite=True)
    nLayers = len(layersList)
    iLayer = 0
    while (iLayer < nLayers):
        valFN = bboLib.replaceYearParameter(layersList[iLayer], year)
        grass.mapcalc("$tmp1 = if(1 == $hsm, if($min <= $val && $val <= $max, 1, 0), $hsm)", hsm=hsmFN, tmp1=tmp1FN, val=valFN,
                      min=lowerBounds[iLayer], max=upperBounds[iLayer], overwrite=True)
        grass.mapcalc("$hsm = $tmp1", tmp1=tmp1FN, hsm=hsmFN, overwrite=True)
        iLayer = iLayer + 1
    
    _applyHSM(modelParams, outputFN, hsmFN)
    
    bboLib.deleteRaster(tmp1FN)
    bboLib.deleteRaster(tmp2FN)
    


# method 98: inverse scale
def _calcProbabilityInverseScale(model, year, logFile = None):
    bboLib.debugMessage("bboPrognosisLib._calcProbabilityInverseScale")

    targetMapset = model["targetMapset"]
    outputFN = bboLib.replaceYearParameter(model["outputFN"], year)
    layerTemplates = model["layers"]
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
          
    # rescale input raster
    inputFN = bboLib.replaceYearParameter(layerTemplates[0], year)
    grass.message("inverse scale {0}".format(inputFN))
    bboLib.rescaleRaster(inputFN, outputFN, 1.0, 0.0)

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


# method 99: scale
def _calcProbabilityScale(model, year, logFile = None):
    bboLib.debugMessage("bboPrognosisLib._calcProbabilityScale")

    targetMapset = model["targetMapset"]
    outputFN = bboLib.replaceYearParameter(model["outputFN"], year)
    layerTemplates = model["layers"]

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)
    
    # rescale input raster
    inputFN = bboLib.replaceYearParameter(layerTemplates[0], year)
    grass.message("scale {0}".format(inputFN))
    bboLib.rescaleRaster(inputFN, outputFN)

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

#endregion MODEL



# #################### ATTACK PROBABILITY ####################
#region ATTACK_PROBABILITY
# attack probability method 201: max
def _attackProbability201(project, year, logFile=None):
    bboLib.debugMessage("bboPrognosisLib.attackProbability201")

    tmp1 = "tmp_bboplib_ap201_1"
    tmp2 = "tmp_bboplib_ap201_2"
    
    targetMapset = project["targetMapset"]
    initFN = bboLib.replaceYearParameter(project["initModel"]["outputFN"], year)
    spreadFN = bboLib.replaceYearParameter(project["spreadModel"]["outputFN"], year)
    attackFN = bboLib.replaceYearParameter(project["attackModel"]["outputFN"], year)

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    modelParams = None
    if (bboLib.validateRaster(initFN)):
        if (bboLib.validateRaster(spreadFN)):
            bboLib.logMessage("attack probability max {0}".format(year), logFile)
            grass.mapcalc("$tmp1 = $spotInitProb", overwrite=True, tmp1=tmp1, spotInitProb=initFN)
            grass.run_command("r.null", map=tmp1, null=0, quiet=True)
            grass.mapcalc("$tmp2 = $spotSpreadProb", overwrite=True, tmp2=tmp2, spotSpreadProb=spreadFN)
            grass.run_command("r.null", map=tmp2, null=0, quiet=True)
            grass.mapcalc("$attackProb = max($tmp1,$tmp2)", overwrite=True, attackProb=attackFN, tmp1=tmp1, tmp2=tmp2)
            bboLib.deleteRaster(tmp1)
            bboLib.deleteRaster(tmp2)
            modelParams = {"method": ATTACKPROGMETHODCODE_MAX}

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
    
    return modelParams


# attack probability method 202: min
def _attackProbability202(project, year, logFile=None):
    bboLib.debugMessage("bboPrognosisLib.attackProbability202")

    tmp1 = "tmp_bboplib_ap202_1"
    tmp2 = "tmp_bboplib_ap202_2"
    
    targetMapset = project["targetMapset"]
    initFN = bboLib.replaceYearParameter(project["initModel"]["outputFN"], year)
    spreadFN = bboLib.replaceYearParameter(project["spreadModel"]["outputFN"], year)
    attackFN = bboLib.replaceYearParameter(project["attackModel"]["outputFN"], year)

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    modelParams = None
    if (bboLib.validateRaster(initFN)):
        if (bboLib.validateRaster(spreadFN)):
            bboLib.logMessage("attack probability min {0}".format(year), logFile)
            grass.mapcalc("$tmp1 = $spotInitProb", overwrite=True, tmp1=tmp1, spotInitProb=initFN)
            grass.run_command("r.null", map=tmp1, null=0, quiet=True)
            grass.mapcalc("$tmp2 = $spotSpreadProb", overwrite=True, tmp2=tmp2, spotSpreadProb=spreadFN)
            grass.run_command("r.null", map=tmp2, null=0, quiet=True)
            grass.mapcalc("$attackProb = min($tmp1,$tmp2)", overwrite=True, attackProb=attackFN, tmp1=tmp1, tmp2=tmp2)
            bboLib.deleteRaster(tmp1)
            bboLib.deleteRaster(tmp2)
            modelParams = {"method": ATTACKPROGMETHODCODE_MIN}

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
    
    return modelParams


# attack probability method 203: mult
def _attackProbability203(project, year, logFile=None):
    bboLib.debugMessage("bboPrognosisLib.attackProbability203")

    tmp1 = "tmp_bboplib_ap203_1"
    tmp2 = "tmp_bboplib_ap203_2"
    
    targetMapset = project["targetMapset"]
    initFN = bboLib.replaceYearParameter(project["initModel"]["outputFN"], year)
    spreadFN = bboLib.replaceYearParameter(project["spreadModel"]["outputFN"], year)
    attackFN = bboLib.replaceYearParameter(project["attackModel"]["outputFN"], year)

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    modelParams = None
    if (bboLib.validateRaster(initFN)):
        if (bboLib.validateRaster(spreadFN)):
            bboLib.logMessage("attack probability mult {0}".format(year), logFile)
            grass.mapcalc("$tmp1 = $spotInitProb", overwrite=True, tmp1=tmp1, spotInitProb=initFN)
            grass.run_command("r.null", map=tmp1, null=0, quiet=True)
            grass.mapcalc("$tmp2 = $spotSpreadProb", overwrite=True, tmp2=tmp2, spotSpreadProb=spreadFN)
            grass.run_command("r.null", map=tmp2, null=0, quiet=True)
            grass.mapcalc("$attackProb = $tmp1 * $tmp2", overwrite=True, attackProb=attackFN, tmp1=tmp1, tmp2=tmp2)
            bboLib.deleteRaster(tmp1)
            bboLib.deleteRaster(tmp2)
            modelParams = {"method": ATTACKPROGMETHODCODE_MULT}

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return modelParams


# attack probability method 204: avg
def _attackProbability204(project, year, logFile=None):
    bboLib.debugMessage("bboPrognosisLib.attackProbability204")

    tmp1 = "tmp_bboplib_ap204_1"
    tmp2 = "tmp_bboplib_ap204_2"
    
    targetMapset = project["targetMapset"]
    initFN = bboLib.replaceYearParameter(project["initModel"]["outputFN"], year)
    spreadFN = bboLib.replaceYearParameter(project["spreadModel"]["outputFN"], year)
    attackFN = bboLib.replaceYearParameter(project["attackModel"]["outputFN"], year)

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    modelParams = None
    if (bboLib.validateRaster(initFN)):
        if (bboLib.validateRaster(spreadFN)):
            bboLib.logMessage("attack probability avg {0}".format(year), logFile)
            grass.mapcalc("$tmp1 = $spotInitProb", overwrite=True, tmp1=tmp1, spotInitProb=initFN)
            grass.run_command("r.null", map=tmp1, null=0, quiet=True)
            grass.mapcalc("$tmp2 = $spotSpreadProb", overwrite=True, tmp2=tmp2, spotSpreadProb=spreadFN)
            grass.run_command("r.null", map=tmp2, null=0, quiet=True)
            grass.mapcalc("$attackProb = ($tmp1 + $tmp2) / 2.0", overwrite=True, attackProb=attackFN, tmp1=tmp1, tmp2=tmp2)
            bboLib.deleteRaster(tmp1)
            bboLib.deleteRaster(tmp2)
            modelParams = {"method": ATTACKPROGMETHODCODE_AVG}

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return modelParams

#endregion ATTACK_PROBABILITY



# #################### MACHINE LEARNING ####################
#region MACHINE_LEARNING

LMMETHODS = [
                (PROGMETHODCODE_LR, "LogisticRegression", "logistic regression {0}"),
                (PROGMETHODCODE_LDA, "LinearDiscriminantAnalysis", "linear discriminant analysis {0}"),
                (PROGMETHODCODE_QDA, "QuadraticDiscriminantAnalysis", "quadratic discriminant analysis {0}"),
                (PROGMETHODCODE_KNC, "KNeighborsClassifier", "k-neighbors classifier {0}"),
                (PROGMETHODCODE_GNB, "GaussianNB", "Gaussian NB {0}"),
                (PROGMETHODCODE_DTC, "DecisionTreeClassifier", "decision tree classifier {0}"),
                (PROGMETHODCODE_DTR, "DecisionTreeRegressor", "decision tree regressor {0}"),
                (PROGMETHODCODE_RFC, "RandomForestClassifier", "random forest classifier {0}"),
                (PROGMETHODCODE_RFR, "RandomForestRegressor", "random forest regressor {0}"),
                (PROGMETHODCODE_ETC, "ExtraTreesClassifier","extra trees classifier {0}"),
                (PROGMETHODCODE_ETR, "ExtraTreesRegressor","extra trees regressor {0}"),
                (PROGMETHODCODE_GBC, "GradientBoostingClassifier","gradient boosting classifier {0}"),
                (PROGMETHODCODE_GBR, "GradientBoostingRegressor","gradient boosting regressor {0}"),
                (PROGMETHODCODE_SVC, "SVC","SVC {0}"),
                (PROGMETHODCODE_EC, "EarthClassifier","Earth classifier {0}"),
                (PROGMETHODCODE_ER, "EarthRegressor","Earth regressor {0}")
            ]


# calculate machine learning method
def _calcMLMethod(keyParams, year, spotCode, logFile=None, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._calcMLMethod")
    for m in LMMETHODS:
        if (m[0] == keyParams["method"]):
            return _calcMachineLearning(m[1], m[2], keyParams, year, spotCode, logFile, useAllSamples)
    return None


def _calcMachineLearning(mlClassifier, mlMessage, model, year, spotCode, logFile=None, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._calcMachineLearning")

    sampleSpot = "tmp_bboplib_cml_samplespot"
    sampleLReg = "tmp_bboplib_cml_samplelreg"
    layerGrp = "tmp_bboplib_cml_lgrp"
    cummPrefix = "tmp_bboplib_cml_c"
    #normPrefix = "tmp_bboplib_cml_n"
    tmpOutPrediction = "tmp_bboplib_cml"
    tmpOutPrediction0 = "tmp_bboplib_cml_0"
    tmpOutPrediction1 = "tmp_bboplib_cml_1"
    
    targetMapset = model["targetMapset"]

    outputTemplate = model["outputFN"]
    outputFN = bboLib.replaceYearParameter(outputTemplate, year)

    hsmTemplate = model["hsmFN"]
    hsmFN = bboLib.replaceYearParameter(hsmTemplate, year)

    layerTemplates = model["layers"]
    trainingYears = model["trainingYears"]

    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    saveModelParamsFN = bboLib.replaceYearParameter(model["modelYearParams"], year)
    saveModelParamsFullPath = os.path.join(dbName, locName, "_data\\prognoses", saveModelParamsFN)

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    bboLib.deleteRaster(hsmFN)
    bboLib.deleteRaster(outputFN)

    # generate samples
    if (not _getTrainingSamplesMask(year, spotCode, sampleLReg, trainingYears, useAllSamples)):
        return
   
    nSamples1 = bboLib.getCellsNumber(sampleLReg, 1)
    nSamples0 = bboLib.getCellsNumber(sampleLReg, 0)
    bboLib.logMessage("number of samples: {0}/{1}".format(nSamples1, nSamples0), logFile)

    if ((2 * len(layerTemplates)) < nSamples1):
        layerList = []
        if (trainingYears < 2):
            for l in layerTemplates:
                layerName = bboLib.replaceYearParameter(l, year)
                layerList.append(layerName)
        else:
            i = 0
            for l in layerTemplates:
                cummFN = cummPrefix + str(i)
                _aggregateRasters(l, SAMPLES_TEMPLATE, cummFN, year, None, trainingYears)
                layerList.append(cummFN)
                i = i + 1
        
        # rescale input rasters
        #i = 0
        #normLayer = []
        #for l in layerList:
        #    normFN = normPrefix + str(i)
        #    bboLib.rescaleRaster(l, normFN)
        #    normLayer.append(normFN)
        #    i = i + 1

		# machine learning
        grass.run_command("i.group", group=layerGrp, input=layerList, quiet=True, overwrite=True)

        bboLib.logMessage(mlMessage.format(year), logFile)
        bboLib.deleteRaster(outputFN)
        grass.run_command("r.learn.ml", group=layerGrp, trainingmap=sampleLReg, output=tmpOutPrediction, 
                          classifier=mlClassifier, save_model=saveModelParamsFullPath,
                          flags="bp", quiet=True, overwrite=True)

        if (1 < trainingYears):
            bboLib.deleteGroup(layerGrp)
            bboLib.deleteRaster(tmpOutPrediction)
            bboLib.deleteRaster(tmpOutPrediction0)
            bboLib.deleteRaster(tmpOutPrediction1)
      
            layerList = []
            for l in layerTemplates:
                layerName = bboLib.replaceYearParameter(l, year)
                layerList.append(layerName)            

            #i = 0
            #normLayer = []
            #for l in layerList:
            #    normFN = normPrefix + str(i)
            #    bboLib.rescaleRaster(l, normFN)
            #    normLayer.append(normFN)
            #    i = i + 1

            grass.run_command("i.group", group=layerGrp, input=layerList, quiet=True, overwrite=True)

			# n_estimators=100
			# max_features = 0
            grass.run_command("r.learn.ml", group=layerGrp, output=tmpOutPrediction, 
                              classifier=mlClassifier, load_model=saveModelParamsFullPath, 
                              flags="p", quiet=True, overwrite=True)

        if (bboLib.validateRaster(tmpOutPrediction)):
            grass.mapcalc("$outHSM = $tmp", outHSM=hsmFN, tmp=tmpOutPrediction, quiet=True, overwrite=True)
            grass.run_command("r.null", map=hsmFN, null=0, quiet=True)
        if (bboLib.validateRaster(tmpOutPrediction1)):
            grass.mapcalc("$outProb = $tmp", outProb=outputFN, tmp=tmpOutPrediction1, quiet=True, overwrite=True)
            grass.run_command("r.null", map=outputFN, null=0, quiet=True)
        else:
            bboLib.warningMessage("Probability has not been calculated {0}".format(year))
            
        _applyHSM(model, outputFN, hsmFN)

        bboLib.deleteGroup(layerGrp)

        i = 0
        for l in layerList:
            #normFN = normPrefix + str(i)
            #bboLib.deleteRaster(normFN)
            cummFN = cummPrefix + str(i)
            bboLib.deleteRaster(cummFN)
            i = i + 1
        
        modelParams = {"method": model["method"]}
        modelParams["layers"] = layerTemplates
        modelParams["paramsFN"] = saveModelParamsFN
        modelParams["applyHSM"] = model["applyHSM"]
    else:
        modelParams = None

    bboLib.deleteRaster(tmpOutPrediction)
    bboLib.deleteRaster(tmpOutPrediction0)
    bboLib.deleteRaster(tmpOutPrediction1)
    bboLib.deleteRaster(sampleSpot)
    bboLib.deleteRaster(sampleLReg)

    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return modelParams

#endregion MACHINE_LEARNING



# #################### MODEL TRAINING ####################
#region MODEL_TRAINING
def runAttackModelTraining(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runAttackModelTraining")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
 
    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACK_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACK_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACK_CTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACK_SUMCTAB_TEMPLATE)
    sumctabFile = open(fileName, "w")

    bboLib.logMessage("layers: {0}".format(project["attackModel"]["layers"]), logFile)
    bboLib.logMessage("apply HSM: {0}\n".format(project["attackModel"]["applyHSM"]), logFile)

    s = "attack;year;auc;hsmTP;hsmFP;hsmFN;hsmTN;progTP;progFP;progFN;progTN\n"
    aucFile.writelines(s)

    _writeCrossTableHeader(ctabFile, True, False, False, True, None)
    _writeCrossTableHeader(sumctabFile, False, False, False, True, None)

    for aMethod in project["attackModel"]["trainingMethods"]:
        _calculateAttackModel(aMethod, project, yearFrom, yearTo)
        _spotPrognosis(project, yearFrom, yearTo, False)
        _assignAttackProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "probabilities to control samples")
        _assignPrognosisToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "prognosis to control samples")
        controlStatistics = _controlSamplesStatistics(yearFrom, yearTo, NEW_SPOTCODE, SAMPLES_PATTACK_COLUMN_NAME, logFile)

        s = "attack;year;auc;hsmTP;hsmFP;hsmFN;hsmFP;progTP;progFP;progFN;progTN"
        bboLib.logMessage(s, logFile)
        i = 0
        for year in range(yearFrom, yearTo + 1):
            s = "{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10}".format(aMethod, year, controlStatistics[i]["auc"], 
                                            controlStatistics[i]["hsmTP"], controlStatistics[i]["hsmFP"], controlStatistics[i]["hsmFN"], controlStatistics[i]["hsmTN"],
                                            controlStatistics[i]["progTP"], controlStatistics[i]["progFP"], controlStatistics[i]["progFN"], controlStatistics[i]["progTN"])
            bboLib.logMessage(s, logFile)
            if (aucFile):
                aucFile.writelines("{0}\n".format(s))
            i = i + 1   

        #crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], 
        #                                   logFile=logFile, ctabFile=ctabFile, sumctabFile=sumctabFile, aMethod=aMethod)
        bboLib.logMessage("\n", logFile)

    ctabFile.close()
    sumctabFile.close()
    aucFile.close()
    logFile.close()


# unused procedure runInitModelTraining
def runInitModelTraining(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runInitModelTraining")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
 
    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_INIT_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_INIT_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_INIT_CROSSTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    bboLib.logMessage("layers: {0}".format(project["initModel"]["layers"]), logFile)
    bboLib.logMessage("apply HSM: {0}\n".format(project["initModel"]["applyHSM"]), logFile)

    aucFile.writelines("init;year;init_pinit\n")

    crosstabFields = ["forest", "oldspot", "spread", "init"]
    h = "init"
    for v1 in range(0, 4):
        for v2 in range(0, 4):
            h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

    ctabFile.writelines("{0}\n".format(h))
  
    for iMethod in project["initModel"]["trainingMethods"]:
        _calculateInitModel(iMethod, project, yearFrom, yearTo)
        _assignInitProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
        controlSamplesAUC = _controlSamplesAUC(yearFrom, yearTo, INIT_SPOTCODE, SAMPLES_PINIT_COLUMN_NAME)

        bboLib.logMessage("init;year;init_pinit", logFile)
        i = 0
        for year in range(yearFrom, yearTo + 1):
            s = "{0};{1};{2}".format(iMethod, year, controlSamplesAUC[i])
            bboLib.logMessage(s, logFile)
            aucFile.writelines("{0}\n".format(s))
            i = i + 1   
            
        initMI = _calcMortalityIndexInit(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
        _calcPartialSpotPrognosis(project["spotPrognosis"]["method"], targetMapset, initMI, 
                                  project["initModel"]["outputFN"], project["spotPrognosis"]["spotFN"], 
                                  project["spotPrognosis"]["maxDistance"], "init", 0)

        _spotClassification(project)

        crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)
        bboLib.logMessage("\n", logFile)

        if (crossTab):
            l = "{0}".format(iMethod)
            for v1 in range(0, 4):
                for v2 in range(0, 4):
                    l = "{0};{1}".format(l, crossTab[v1][v2])
            ctabFile.writelines("{0}\n".format(l))

    ctabFile.close()
    aucFile.close()
    logFile.close()   


def runSpreadModelTraining(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runSpreadModelTraining")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
 
    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_SPREAD_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_SPREAD_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_SPREAD_CROSSTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    bboLib.logMessage("layers: {0}".format(project["spreadModel"]["layers"]), logFile)
    bboLib.logMessage("apply HSM: {0}\n".format(project["spreadModel"]["applyHSM"]), logFile)

    aucFile.writelines("spread;year;spread_pspread\n")

    crosstabFields = ["forest", "oldspot", "spread", "init"]
    h = "spread"
    for v1 in range(0, 4):
        for v2 in range(0, 4):
            h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

    ctabFile.writelines("{0}\n".format(h))

    for iMethod in project["spreadModel"]["trainingMethods"]:
        _calculateSpreadModel(iMethod, project, yearFrom, yearTo)
        _assignSpreadProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
        controlSamplesAUC = _controlSamplesAUC(yearFrom, yearTo, SPREAD_SPOTCODE, SAMPLES_PSPREAD_COLUMN_NAME)

        bboLib.logMessage("spread;year;spread_pspread", logFile)
        i = 0
        for year in range(yearFrom, yearTo + 1):
            s = "{0};{1};{2}".format(iMethod, year, controlSamplesAUC[i])
            bboLib.logMessage(s, logFile)
            aucFile.writelines("{0}\n".format(s))
            i = i + 1   

        spreadMI = _calcMortalityIndexSpread(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
        _calcPartialSpotPrognosis(project["spotPrognosis"]["method"], targetMapset, spreadMI, 
                                  project["spreadModel"]["outputFN"], project["spotPrognosis"]["spotFN"], 
                                  project["spotPrognosis"]["maxDistance"], "spread", 0)
        
        _spotClassification(project)

        crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)
        bboLib.logMessage("\n", logFile)

        if (crossTab):
            l = "{0}".format(iMethod)
            for v1 in range(0, 4):
                for v2 in range(0, 4):
                    l = "{0};{1}".format(l, crossTab[v1][v2])
            ctabFile.writelines("{0}\n".format(l))
   
    ctabFile.close()
    aucFile.close()
    logFile.close()


def runInitSpreadModelTraining(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runInitSpreadModelTraining")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    fileName = project["outputPrefix"] + TRAINING_ISM_LOG_TEMPLATE
    fileName = os.path.join(dbName, locName, "_data\\prognoses", fileName)
    logFile = open(fileName, "w")

    fileName = project["outputPrefix"] + TRAINING_ISM_AUC_TEMPLATE
    fileName = os.path.join(dbName, locName, "_data\\prognoses", fileName)
    aucFile = open(fileName, "w")

    fileName = project["outputPrefix"] + TRAINING_ISM_CROSSTAB_TEMPLATE
    fileName = os.path.join(dbName, locName, "_data\\prognoses", fileName)
    ctabFile = open(fileName, "w")

    bboLib.logMessage("init layers: {0}".format(str(project["initModel"]["layers"])), logFile)
    bboLib.logMessage("init apply HSM: {0}".format(project["initModel"]["applyHSM"]), logFile)
    bboLib.logMessage("spread layers: {0}".format(str(project["spreadModel"]["layers"])), logFile)
    bboLib.logMessage("spread apply HSM: {0}\n".format(project["spreadModel"]["applyHSM"]), logFile)
    
    aucFile.writelines("init;spread;attack;year;new_pattack;spread_pattack;init_pattack;spread_pspread;init_pinit\n")

    crosstabFields = ["forest", "oldspot", "spread", "init"]
    h = "init;spread;attack"
    for v1 in range(0, 4):
        for v2 in range(0, 4):
            h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

    ctabFile.writelines("{0}\n".format(h))

    lastSpreadMethod = -1
    for initMethod in project["initModel"]["trainingMethods"]:
        _calculateInitModel(initMethod, project, yearFrom, yearTo)
        _assignInitProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
        for spreadMethod in project["spreadModel"]["trainingMethods"]:
            if (spreadMethod != lastSpreadMethod):
                _calculateSpreadModel(spreadMethod, project, yearFrom, yearTo)
                _assignSpreadProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
                lastSpreadMethod = spreadMethod
            for attackMethod in project["attackModel"]["trainingMethods"]:
                _calculateAttackModel(attackMethod, project, yearFrom, yearTo)
                _assignAttackProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
                samplesStat = _calcControlSamplesStatistics(project["yearFrom"], project["yearTo"])

                bboLib.logMessage("init;spread;attack;year;new_pattack;spread_pattack;init_pattack;spread_pspread;init_pinit", logFile)
                i = 0
                for year in range(yearFrom, yearTo + 1):
                    s = "{0};{1};{2};{3};{4};{5};{6};{7};{8}".format(initMethod, spreadMethod, attackMethod, year, 
                         samplesStat["new_pattack"][i], samplesStat["spread_pattack"][i],samplesStat["init_pattack"][i],
                         samplesStat["spread_pspread"][i],samplesStat["init_pinit"][i])
                    bboLib.logMessage(s, logFile)
                    aucFile.writelines("{0}\n".format(s))
                    i = i + 1
                
                bboLib.logMessage("", logFile)
                _spotPrognosis(project, project["yearFrom"], project["yearTo"])
                crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)
                bboLib.logMessage("\n", logFile)

                if (crossTab):
                    l = "{0};{1};{2}".format(initMethod, spreadMethod, attackMethod)
                    for v1 in range(0, 4):
                        for v2 in range(0, 4):
                            l = "{0};{1}".format(l, crossTab[v1][v2])
                    ctabFile.writelines("{0}\n".format(l))
            
    ctabFile.close()
    aucFile.close()
    logFile.close()

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def runInitModelLayers(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runInitModelLayers")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_INITLAYERS_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_INITLAYERS_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_INITLAYERS_CROSSTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    bboLib.logMessage("init layers training: {0}".format(project["initModel"]["trainingLayers"]), logFile)
    bboLib.logMessage("apply HSM: {0}\n".format(project["initModel"]["applyHSM"]), logFile)

    layersFields = None
    i = 1
    for iLayer in project["initModel"]["trainingLayers"]:
        if (layersFields):
            layersFields = "{0};L{1}".format(layersFields, i)
        else:
            layersFields = "L{0}".format(i)
        i = i + 1

    aucFile.writelines("init;year;{0};new_pinit\n".format(layersFields))

    crosstabFields = ["forest", "oldspot", "spread", "init"]
    h = "init;{0}".format(layersFields)
    for v1 in range(0, 4):
        for v2 in range(0, 4):
            h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

    ctabFile.writelines("{0}\n".format(h))

    layerList = project["initModel"]["trainingLayers"]
    grass.message(str(layerList))
    nLayers = len(layerList)
    for i in range(1, nLayers + 1):
        _calcInitModelLayersSubset(project, i, logFile, aucFile, ctabFile)

    ctabFile.close()
    aucFile.close()
    logFile.close()

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def runSpreadModelLayers(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runSpreadModelLayers")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_SPREADLAYERS_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_SPREADLAYERS_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_SPREADLAYERS_CROSSTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    bboLib.logMessage("spread layers training: {0}".format(project["spreadModel"]["trainingLayers"]), logFile)
    bboLib.logMessage("apply HSM: {0}\n".format(project["spreadModel"]["applyHSM"]), logFile)

    layersFields = None
    i = 1
    for iLayer in project["spreadModel"]["trainingLayers"]:
        if (layersFields):
            layersFields = "{0};L{1}".format(layersFields, i)
        else:
            layersFields = "L{0}".format(i)
        i = i + 1

    aucFile.writelines("spread;year;{0};new_pspread\n".format(layersFields))

    crosstabFields = ["forest", "oldspot", "spread", "init"]
    h = "spread;{0}".format(layersFields)
    for v1 in range(0, 4):
        for v2 in range(0, 4):
            h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

    ctabFile.writelines("{0}\n".format(h))

    layerList = project["spreadModel"]["trainingLayers"]
    grass.message(str(layerList))
    nLayers = len(layerList)
    for i in range(1, nLayers + 1):
        _calcSpreadModelLayersSubset(project, i, logFile, aucFile, ctabFile)

    ctabFile.close()
    aucFile.close()
    logFile.close()

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

        
def runAttackModelLayers(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runAttackModelLayers")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACKLAYERS_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACKLAYERS_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACKLAYERS_CTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ATTACKLAYERS_SUMCTAB_TEMPLATE)
    sumctabFile = open(fileName, "w")

    bboLib.logMessage("attack layers training: {0}".format(project["attackModel"]["trainingLayers"]), logFile)
    bboLib.logMessage("apply HSM: {0}\n".format(project["attackModel"]["applyHSM"]), logFile)

    layersFields = None
    i = 1
    for iLayer in project["attackModel"]["trainingLayers"]:
        if (layersFields):
            layersFields = "{0};L{1}".format(layersFields, i)
        else:
            layersFields = "L{0}".format(i)
        i = i + 1

    s = "attack;year;{0};auc;hsmTP;hsmFP;hsmFN;hsmTN;progTP;progFP;progFN;progTN\n".format(layersFields)
    aucFile.writelines(s)

    _writeCrossTableHeader(ctabFile, True, False, False, True, project["attackModel"]["trainingLayers"])
    _writeCrossTableHeader(sumctabFile, False, False, False, True, project["attackModel"]["trainingLayers"])

    layerList = project["attackModel"]["trainingLayers"]
    grass.message(str(layerList))
    nLayers = len(layerList)
    for i in range(1, nLayers + 1):
        _calcAttackModelLayersSubset(project, i, logFile, aucFile, ctabFile, sumctabFile)

    ctabFile.close()
    sumctabFile.close()
    aucFile.close()
    logFile.close()

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def runInitSpreadModelLayers(projectFN):
    bboLib.debugMessage("bboPrognosisLib.runInitSpreadModelLayers")

    project = _readProject(projectFN)
    bboLib.setDebug(project)

    targetMapset = project["targetMapset"]

    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ISMLAYERS_LOG_TEMPLATE)
    logFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ISMLAYERS_AUC_TEMPLATE)
    aucFile = open(fileName, "w")

    fileName = bboLib.getFullLogFileName(project["outputPrefix"] + TRAINING_ISMLAYERS_CROSSTAB_TEMPLATE)
    ctabFile = open(fileName, "w")

    bboLib.logMessage("init methods: {0}".format(project["initModel"]["trainingMethods"]), logFile)
    bboLib.logMessage("apply init HSM: {0}\n".format(project["initModel"]["applyHSM"]), logFile)
    bboLib.logMessage("spread methods: {0}".format(project["spreadModel"]["trainingMethods"]), logFile)
    bboLib.logMessage("apply spread HSM: {0}\n".format(project["spreadModel"]["applyHSM"]), logFile)
    bboLib.logMessage("attack methods: {0}".format(project["attackModel"]["trainingMethods"]), logFile)
    bboLib.logMessage("apply attack HSM: {0}\n".format(project["attackModel"]["applyHSM"]), logFile)
    bboLib.logMessage("init/spread model layers: {0}\n".format(project["attackModel"]["trainingLayers"]), logFile)

    layersFields = None
    i = 1
    for iLayer in project["attackModel"]["trainingLayers"]:
        if (layersFields):
            layersFields = "{0};L{1}".format(layersFields, i)
        else:
            layersFields = "L{0}".format(i)
        i = i + 1

    aucFile.writelines("init;spread;attack;year;{0};new_pattack\n".format(layersFields))

    crosstabFields = ["forest", "oldspot", "spread", "init"]
    h = "init;spread;attack;{0}".format(layersFields)
    for v1 in range(0, 4):
        for v2 in range(0, 4):
            h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

    ctabFile.writelines("{0}\n".format(h))

    layerList = project["attackModel"]["trainingLayers"]
    grass.message(str(layerList))
    nLayers = len(layerList)
    for i in range(1, nLayers + 1):
        _calcISModelLayersSubset(project, i, logFile, aucFile, ctabFile)

    ctabFile.close()
    aucFile.close()
    logFile.close()

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)



def _calculateInitModel(iMethod, project, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._calculateInitModel")

    if (iMethod < 100):
        model = project["initModel"]
        model["method"] = iMethod
        _calculateModel(project, model, yearFrom, yearTo, INIT_SPOTCODE, INIT_MSG_TEMPLATE)

def _calculateSpreadModel(iMethod, project, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._calculateSpreadModel")

    if (iMethod < 100):
        model = project["spreadModel"]
        model["method"] = iMethod
        _calculateModel(project, model, yearFrom, yearTo, SPREAD_SPOTCODE, SPREAD_MSG_TEMPLATE)

def _calculateAttackModel(iMethod, project, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._calculateAttackModel")

    if ((iMethod < 100) or ((200 < iMethod) and (iMethod < 300))):
        model = project["attackModel"]
        model["method"] = iMethod
        _calculateModel(project, model, yearFrom, yearTo, NEW_SPOTCODE, ATTACK_MSG_TEMPLATE)



def _spotClassification(project):
    bboLib.debugMessage("bboPrognosisLib._spotClassification")

    targetMapset = project["targetMapset"]

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    for year in range(yearFrom, yearTo + 1):
        spotPrognosisFN = bboLib.replaceYearParameter(project["spotPrognosis"]["spotFN"], year)
        spotIdPrognosisFN = bboLib.replaceYearParameter(project["spotPrognosis"]["spotIdFN"], year)
        if (bboLib.validateRaster(spotPrognosisFN)):
            prevYear = bboLib.findPreviousSpotYear(year)
            if (prevYear):
                prevSpotFN = bboLib.replaceYearParameter(bboLib.spotTemplate, prevYear, bboLib.forestMapset)
                prevSpotIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, prevYear, bboLib.forestMapset)
                bboLib.spotClassificationFN(targetMapset, prevSpotFN, prevSpotIdFN, spotPrognosisFN, spotIdPrognosisFN)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)



def _calcInitModelLayersSubset(project, subsetSize, logFile=None, aucFile=None, ctabFile=None, firstLayer=0, layerSubset=[]):
    bboLib.debugMessage("bboPrognosisLib._calcInitModelLayersSubset")

    layerList = project["initModel"]["trainingLayers"]
    nLayers = len(layerList)

    for iLayer in range(firstLayer, nLayers):
        newLayerSubset = list(layerSubset)
        newLayerSubset.append(layerList[iLayer])
        if (len(newLayerSubset) < subsetSize):
            _calcInitModelLayersSubset(project, subsetSize, logFile, aucFile, ctabFile, iLayer + 1, newLayerSubset)
        else:
            _calcInitModelOnLayers(project, newLayerSubset, logFile, aucFile, ctabFile)


def _calcInitModelOnLayers(project, newLayersList, logFile=None, aucFile=None, ctabFile=None):
    bboLib.debugMessage("bboPrognosisLib._calcInitModelOnLayers")
    
    iMethod = project["initModel"]["method"]

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    
    project["initModel"]["layers"] = newLayersList

    newLayersFields = None
    newLayersBits = None
    i = 1
    for iLayer in project["initModel"]["trainingLayers"]:
        l = int(iLayer in newLayersList)
        if (newLayersFields):
            newLayersFields = "{0};L{1}".format(newLayersFields, i)
            newLayersBits = "{0};{1}".format(newLayersBits, l)
        else:
            newLayersFields = "L{0}".format(i)
            newLayersBits = "{0}".format(l)
        i = i + 1


    _calculateInitModel(iMethod, project, yearFrom, yearTo)
    _assignInitProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
    controlSamplesAUC = _controlSamplesAUC(yearFrom, yearTo, INIT_SPOTCODE, SAMPLES_PINIT_COLUMN_NAME)

    s = "init;year;{0};auc".format(newLayersFields)
    bboLib.logMessage(s, logFile)

    i = 0
    for year in range(yearFrom, yearTo + 1):
        s = "{0};{1};{2};{3}".format(iMethod, year, newLayersBits, controlSamplesAUC[i])
        bboLib.logMessage(s, logFile)
        if (aucFile):
            aucFile.writelines("{0}\n".format(s))
        i = i + 1   
          
    initMI = _calcMortalityIndexInit(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    _calcPartialSpotPrognosis(project["spotPrognosis"]["method"], project["targetMapset"], initMI, 
                              project["initModel"]["outputFN"], project["spotPrognosis"]["spotFN"], 
                              project["spotPrognosis"]["maxDistance"], "init", 0)

    _spotClassification(project)
    crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)

    if (crossTab):
        l = "{0};{1}".format(iMethod, newLayersBits)
        for v1 in range(0, 4):
            for v2 in range(0, 4):
                l = "{0};{1}".format(l, crossTab[v1][v2])
        bboLib.logMessage(l)
        if (ctabFile):
            ctabFile.writelines("{0}\n".format(l))

    bboLib.logMessage("\n", logFile)



def _calcSpreadModelLayersSubset(project, subsetSize, logFile=None, aucFile=None, ctabFile=None, firstLayer=0, layerSubset=[]):
    bboLib.debugMessage("bboPrognosisLib._calcSpreadModelLayersSubset")

    layerList = project["spreadModel"]["trainingLayers"]
    nLayers = len(layerList)

    for iLayer in range(firstLayer, nLayers):
        newLayerSubset = list(layerSubset)
        newLayerSubset.append(layerList[iLayer])
        if (len(newLayerSubset) < subsetSize):
            _calcSpreadModelLayersSubset(project, subsetSize, logFile, aucFile, ctabFile, iLayer + 1, newLayerSubset)
        else:
            _calcSpreadModelOnLayers(project, newLayerSubset, logFile, aucFile, ctabFile)

def _calcSpreadModelOnLayers(project, newLayersList, logFile=None, aucFile=None, ctabFile=None):
    bboLib.debugMessage("bboPrognosisLib._calcSpreadModelOnLayers")
    
    iMethod = project["spreadModel"]["method"]

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    
    project["spreadModel"]["layers"] = newLayersList

    newLayersFields = None
    newLayersBits = None
    i = 1
    for iLayer in project["spreadModel"]["trainingLayers"]:
        l = int(iLayer in newLayersList)
        if (newLayersFields):
            newLayersFields = "{0};L{1}".format(newLayersFields, i)
            newLayersBits = "{0};{1}".format(newLayersBits, l)
        else:
            newLayersFields = "L{0}".format(i)
            newLayersBits = "{0}".format(l)
        i = i + 1


    _calculateSpreadModel(iMethod, project, yearFrom, yearTo)
    _assignSpreadProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
    controlSamplesAUC = _controlSamplesAUC(yearFrom, yearTo, SPREAD_SPOTCODE, SAMPLES_PSPREAD_COLUMN_NAME)

    s = "spread;year;{0};new_pattack".format(newLayersFields)
    bboLib.logMessage(s, logFile)

    i = 0
    for year in range(yearFrom, yearTo + 1):
        s = "{0};{1};{2};{3}".format(iMethod, year, newLayersBits, controlSamplesAUC[i])
        bboLib.logMessage(s, logFile)
        if (aucFile):
            aucFile.writelines("{0}\n".format(s))
        i = i + 1   
            
    spreadMI = _calcMortalityIndexSpread(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    _calcPartialSpotPrognosis(project["spotPrognosis"]["method"], project["targetMapset"], spreadMI, 
                              project["spreadModel"]["outputFN"], project["spotPrognosis"]["spotFN"], 
                              project["spotPrognosis"]["maxDistance"], "spread", 0)

    _spotClassification(project)
    crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)

    if (crossTab):
        l = "{0};{1}".format(iMethod, newLayersBits)
        for v1 in range(0, 4):
            for v2 in range(0, 4):
                l = "{0};{1}".format(l, crossTab[v1][v2])
        bboLib.logMessage(l)
        if (ctabFile):
            ctabFile.writelines("{0}\n".format(l))

    bboLib.logMessage("\n", logFile)



def _calcAttackModelLayersSubset(project, subsetSize, logFile=None, aucFile=None, ctabFile=None, sumctabFile=None, firstLayer=0, layerSubset=[]):
    bboLib.debugMessage("bboPrognosisLib._calcAttackModelLayersSubset")

    layerList = project["attackModel"]["trainingLayers"]
    nLayers = len(layerList)

    for iLayer in range(firstLayer, nLayers):
        newLayerSubset = list(layerSubset)
        newLayerSubset.append(layerList[iLayer])
        if (len(newLayerSubset) < subsetSize):
            _calcAttackModelLayersSubset(project, subsetSize, logFile, aucFile, ctabFile, sumctabFile, iLayer + 1, newLayerSubset)
        else:
            _calcAttackModelOnLayers(project, newLayerSubset, logFile, aucFile, ctabFile, sumctabFile)


def _calcAttackModelOnLayers(project, newLayersList, logFile=None, aucFile=None, ctabFile=None, sumctabFile=None):
    bboLib.debugMessage("bboPrognosisLib._calcAttackModelOnLayers")
    
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    
    project["attackModel"]["layers"] = newLayersList

    newLayersFields = None
    newLayersBits = None
    i = 1
    for iLayer in project["attackModel"]["trainingLayers"]:
        l = int(iLayer in newLayersList)
        if (newLayersFields):
            newLayersFields = "{0};L{1}".format(newLayersFields, i)
            newLayersBits = "{0};{1}".format(newLayersBits, l)
        else:
            newLayersFields = "L{0}".format(i)
            newLayersBits = "{0}".format(l)
        i = i + 1

    for aMethod in project["attackModel"]["trainingMethods"]:

        _calculateAttackModel(aMethod, project, yearFrom, yearTo)
        _spotPrognosis(project, project["yearFrom"], project["yearTo"], False)
        _assignAttackProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "probabilities to control samples")
        _assignPrognosisToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "prognosis to control samples")
        controlStatistics = _controlSamplesStatistics(yearFrom, yearTo, NEW_SPOTCODE, SAMPLES_PATTACK_COLUMN_NAME, logFile)
    
        s = "attack;year;{0};auc;hsmTP;hsmFP;hsmFN;hsmTN;progTP;progFP;progFN;progTN".format(newLayersFields)
        bboLib.logMessage(s, logFile)
    
        i = 0
        for year in range(yearFrom, yearTo + 1):
            s = "{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11}".format(aMethod, year, newLayersBits, controlStatistics[i]["auc"], 
                                         controlStatistics[i]["hsmTP"], controlStatistics[i]["hsmFP"], controlStatistics[i]["hsmFN"], controlStatistics[i]["hsmTN"],
                                         controlStatistics[i]["progTP"], controlStatistics[i]["progFP"], controlStatistics[i]["progFN"], controlStatistics[i]["progTN"])
            bboLib.logMessage(s, logFile)
            if (aucFile):
                aucFile.writelines("{0}\n".format(s))
            i = i + 1   

        #sumCTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], 
        #                                  logFile=logFile, ctabFile=ctabFile, sumctabFile=sumctabFile, 
        #                                  aMethod=aMethod, bitLayers=newLayersBits)

        bboLib.logMessage("\n", logFile)



def _calcISModelLayersSubset(project, subsetSize, logFile=None, aucFile=None, ctabFile=None, firstLayer=0, layerSubset=[]):
    bboLib.debugMessage("bboPrognosisLib._calcISModelLayersSubset")

    layerList = project["attackModel"]["trainingLayers"]
    nLayers = len(layerList)

    for iLayer in range(firstLayer, nLayers):
        newLayerSubset = list(layerSubset)
        newLayerSubset.append(layerList[iLayer])
        if (len(newLayerSubset) < subsetSize):
            _calcISModelLayersSubset(project, subsetSize, logFile, aucFile, ctabFile, iLayer + 1, newLayerSubset)
        else:
            _calcISModelOnLayers(project, newLayerSubset, logFile, aucFile, ctabFile)


def _calcISModelOnLayers(project, newLayersList, logFile=None, aucFile=None, ctabFile=None):
    bboLib.debugMessage("bboPrognosisLib._calcISModelOnLayers")
    
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    
    project["initModel"]["layers"] = newLayersList
    project["spreadModel"]["layers"] = newLayersList
    project["attackModel"]["layers"] = newLayersList

    newLayersFields = None
    newLayersBits = None
    i = 1
    for iLayer in project["training"]["layers"]:
        l = int(iLayer in newLayersList)
        if (newLayersFields):
            newLayersFields = "{0};L{1}".format(newLayersFields, i)
            newLayersBits = "{0};{1}".format(newLayersBits, l)
        else:
            newLayersFields = "L{0}".format(i)
            newLayersBits = "{0}".format(l)
        i = i + 1
    
    lastSpreadMethod = PROGMETHODCODE_NONE
    for initMethod in project["initModel"]["trainingMethods"]:
        _calculateInitModel(initMethod, project, yearFrom, yearTo)
        for spreadMethod in project["spreadModel"]["trainingMethods"]:
            if (lastSpreadMethod != spreadMethod):
                _calculateSpreadModel(spreadMethod, project, yearFrom, yearTo)
                lastSpreadMethod = spreadMethod
            for attackMethod in project["attackModel"]["trainingMethods"]:
                _calculateAttackModel(attackMethod, project, yearFrom, yearTo)
                _assignAttackProbabilitiesToSamples(project, VECTOR_CONTROL_SAMPLES_TEMPLATE, "control samples")
                controlSamplesAUC = _controlSamplesAUC(yearFrom, yearTo, NEW_SPOTCODE, SAMPLES_PATTACK_COLUMN_NAME)

                s = "init;spread;attack;year;{0};new_pattack".format(newLayersFields)
                bboLib.logMessage(s, logFile)

                i = 0
                for year in range(yearFrom, yearTo + 1):
                    s = "{0};{1};{2};{3};{4};{5}".format(initMethod, spreadMethod, attackMethod, year, newLayersBits, controlSamplesAUC[i])
                    bboLib.logMessage(s, logFile)
                    if (aucFile):
                        aucFile.writelines("{0}\n".format(s))
                    i = i + 1   

                _spotPrognosis(project, project["yearFrom"], project["yearTo"])
                crossTab = _spotCrosstabValidation(project, project["yearFrom"], project["yearTo"], logFile=logFile)

                if (crossTab):
                    l = "{0};{1};{2};{3}".format(initMethod, spreadMethod, attackMethod, newLayersBits)
                    for v1 in range(0, 4):
                        for v2 in range(0, 4):
                            l = "{0};{1}".format(l, crossTab[v1][v2])
                    bboLib.logMessage(l)
                    if (ctabFile):
                        ctabFile.writelines("{0}\n".format(l))

    bboLib.logMessage("\n", logFile)

#endregion MODEL_TRAINING



# #################### SPOT AREAS ####################
#region SPOT_AREAS
def _getSpotCells(targetMapset, aspotTemplate, yearFrom, yearTo):
    actualSpotFN = "tmp_bboplib_gsc_actualspot"
    areaList = []

    bboLib.debugMessage("bboPrognosisLib.getSpotCells")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    y0 = yearFrom
    while (y0 <= yearTo):
        spotFN = bboLib.replaceYearParameter(aspotTemplate, y0)
        if (bboLib.validateRaster(spotFN)):
            grass.mapcalc("$actualSpot = if($spotCode == $spot, 1, null())", actualSpot=actualSpotFN, spot=spotFN, spotCode=OLD_SPOTCODE, overwrite=True)
            grass.run_command("r.null", map=actualSpotFN, setnull=0, quiet=True)
            aOld = bboLib.getNotNullCellsNumber(actualSpotFN)
            grass.mapcalc("$actualSpot = if($spotCode == $spot, 1, null())", actualSpot=actualSpotFN, spot=spotFN, spotCode=SPREAD_SPOTCODE, overwrite=True)
            grass.run_command("r.null", map=actualSpotFN, setnull=0, quiet=True)
            aEnlarge = bboLib.getNotNullCellsNumber(actualSpotFN)
            grass.mapcalc("$actualSpot = if($spotCode == $spot, 1, null())", actualSpot=actualSpotFN, spot=spotFN, spotCode=INIT_SPOTCODE, overwrite=True)
            grass.run_command("r.null", map=actualSpotFN, setnull=0, quiet=True)
            aFly = bboLib.getNotNullCellsNumber(actualSpotFN)
            aNew = aEnlarge + aFly
            aAll = aOld + aEnlarge + aFly
            areaList.append((y0, aOld, aEnlarge, aFly, aAll, aNew))
        else:
            areaList.append((y0, None, None, None, None, None))
        y0 = y0 + 1

    bboLib.deleteRaster(actualSpotFN)
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return areaList


def _getSpotAreas(targetMapset, aspotTemplate, us50MaskTemplate, yearFrom, yearTo):
    actualSpotFN = "tmp_bboplib_gsa_actualspot"
    areaList = []

    bboLib.debugMessage("bboPrognosisLib._getSpotAreas")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    y0 = yearFrom
    while (y0 <= yearTo):
        spotFN = bboLib.replaceYearParameter(aspotTemplate, y0)
        us50MaskFN = bboLib.replaceYearParameter(us50MaskTemplate, y0)
        bboLib.debugMessage(spotFN)
        if (bboLib.validateRaster(spotFN)):
            grass.mapcalc("$actualSpot = if($spotCode == $spot, 1, null())", actualSpot=actualSpotFN, spot=spotFN, spotCode=OLD_SPOTCODE, overwrite=True)
            grass.run_command("r.null", map=actualSpotFN, setnull=0, quiet=True)
            aOld = bboLib.getRasterArea(actualSpotFN)
            grass.mapcalc("$actualSpot = if($spotCode == $spot, 1, null())", actualSpot=actualSpotFN, spot=spotFN, spotCode=SPREAD_SPOTCODE, overwrite=True)
            grass.run_command("r.null", map=actualSpotFN, setnull=0, quiet=True)
            aEnlarge = bboLib.getRasterArea(actualSpotFN)
            grass.mapcalc("$actualSpot = if($spotCode == $spot, 1, null())", actualSpot=actualSpotFN, spot=spotFN, spotCode=INIT_SPOTCODE, overwrite=True)
            grass.run_command("r.null", map=actualSpotFN, setnull=0, quiet=True)
            aFly = bboLib.getRasterArea(actualSpotFN)
            aNew = aEnlarge + aFly
            aAll = aOld + aEnlarge + aFly
            if (bboLib.validateRaster(us50MaskFN)):
                aS50 = bboLib.getRasterArea(us50MaskFN)
            else:
                aS50 = -10000
            areaList.append((y0, aOld, aEnlarge, aFly, aAll, aNew, aS50))
        else:
            areaList.append((y0, None, None, None, None, None, None))
        y0 = y0 + 1

    bboLib.deleteRaster(actualSpotFN)
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return areaList


def _getHa(a):
    if (a):
        return a/10000.0
    else:
        return None


def _getSpotAreasHa(targetMapset, aspotTemplate, us50MaskTemplate, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._getSpotAreasHa")
    areaList2 = []
    areaList = _getSpotAreas(targetMapset, aspotTemplate, us50MaskTemplate, yearFrom, yearTo)
    for a in areaList:
        areaList2.append((a[0], _getHa(a[1]), _getHa(a[2]), _getHa(a[3]), _getHa(a[4]), _getHa(a[5]), _getHa(a[6])))
    return areaList2

#endregion SPOT_AREAS



# #################### MASK ####################
#region MASK
def _getSpotMaskSeries(yearFrom, yearTo, spotCode, outputTemplate, targetMapset=None, trainingYears=1):
    bboLib.debugMessage("bboPrognosisLib._calcSpotMaskSeries")

    if (targetMapset):
        userMapset = grass.gisenv()["MAPSET"]  
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)

    year = yearFrom
    while (year <= yearTo):
        _getSpotMask(year, spotCode, outputTemplate, trainingYears)
        year = year + 1

    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)


def _getSpotMask(year, spotCode, outputTemplate, trainingYears=1):
    bboLib.debugMessage("bboPrognosisLib._getSpotMask")

    tmp1 = "tmp_bboplib_cspm_2071"
    tmp2 = "tmp_bboplib_cspm_2072"

    outputFN = bboLib.replaceYearParameter(outputTemplate, year)
    grass.mapcalc("$outMask = null()", outMask=outputFN, overwrite=True)

    nLayers = 0
    while (0 < trainingYears):
        spotFN = bboLib.replaceYearParameter(bboLib.spotTemplate, year, bboLib.forestMapset)
        if (bboLib.validateRaster(spotFN, None, True)):
            nLayers = nLayers + 1
            if ((spotCode == INIT_SPOTCODE) or (spotCode == SPREAD_SPOTCODE)):
                grass.mapcalc("$tmp1 = if($code == $spot, 1, null())", tmp1=tmp1, spot=spotFN, code=spotCode, overwrite=True)
            elif (spotCode == NEW_SPOTCODE):
                grass.mapcalc("$tmp1 = if(1 < $spot, 1, null())", tmp1=tmp1, spot=spotFN, overwrite=True)
            else: # ALLSPOTCODE
                grass.mapcalc("$tmp1 = if(0 < $spot, 1, null())", tmp1=tmp1, spot=spotFN, overwrite=True)
            grass.mapcalc("$tmp2 = if(isnull($outMask), if(isnull($tmp1), null(), $tmp1), $outMask)", tmp2=tmp2, outMask=outputFN, tmp1=tmp1, overwrite=True)
            grass.mapcalc("$outMask = $tmp2", outMask=outputFN, tmp2=tmp2, overwrite=True)
        year = year - 1
        trainingYears = trainingYears - 1

    bboLib.deleteRaster(tmp2)
    bboLib.deleteRaster(tmp1)

    return (0 < nLayers)



def _getTrainingSamplesMaskSeries(yearFrom, yearTo, spotCode, outputTemplate, targetMapset=None, trainingYears=1, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._getTrainingSamplesMaskSeries")

    if (targetMapset):
        userMapset = grass.gisenv()["MAPSET"]  
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)

    year = yearFrom
    while (year <= yearTo):
        _getTrainingSamplesMask(year, spotCode, outputTemplate, trainingYears, useAllSamples)
        year = year + 1

    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)


def _getTrainingSamplesMask(year, spotCode, outputTemplate, trainingYears=1, useAllSamples=False):
    bboLib.debugMessage("bboPrognosisLib._getTrainingSamplesMask")

    tmp1 = "tmp_bboplib_csm_6841"
    tmp2 = "tmp_bboplib_csm_6842"

    outputFN = bboLib.replaceYearParameter(outputTemplate, year)
    grass.mapcalc("$outMask = null()", outMask=outputFN, overwrite=True)

    if (useAllSamples):
        samplesTemplate = SAMPLES_TEMPLATE
    else:
        samplesTemplate = RASTER_TRAINING_SAMPLES_TEMPLATE

    nLayers = 0
    while (0 < trainingYears):
        samplesFN = bboLib.replaceYearParameter(samplesTemplate, year, bboLib.forestMapset)
        if (bboLib.validateRaster(samplesFN, None, True)):
            nLayers = nLayers + 1
            if ((spotCode == INIT_SPOTCODE) or (spotCode == SPREAD_SPOTCODE)):
                grass.mapcalc("$tmp1 = if($code == $samples, 1, if(-$code == $samples, 0, null()))", tmp1=tmp1, samples=samplesFN, code=spotCode, overwrite=True)
            else: # NEWSPOTCODE
                grass.mapcalc("$tmp1 = if(0 < $samples, 1, if($samples < 0, 0, null()))", tmp1=tmp1, samples=samplesFN, overwrite=True)
            grass.mapcalc("$tmp2 = if(isnull($outMask), $tmp1, $outMask)", tmp2=tmp2, outMask=outputFN, tmp1=tmp1, overwrite=True)
            grass.mapcalc("$outMask = $tmp2", outMask=outputFN, tmp2=tmp2, overwrite=True)
        year = year - 1
        trainingYears = trainingYears - 1

    bboLib.deleteRaster(tmp2)
    bboLib.deleteRaster(tmp1)

    return (0 < nLayers)



def _aggregateRasters(valTemplate, maskTemplate, outputFN, year, targetMapset=None, trainingYears=1):
    bboLib.debugMessage("bboPrognosisLib._aggregateRasters")

    tmpVal1 = "tmp_bboplib_aggraster1"

    if (targetMapset):
        userMapset = grass.gisenv()["MAPSET"]  
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)
    
    grass.mapcalc("$outVal = null()", outVal=outputFN, overwrite=True)
    
    nLayers = 0
    while (0 < trainingYears):
        valFN = bboLib.replaceYearParameter(valTemplate, year)
        maskFN = bboLib.replaceYearParameter(maskTemplate, year)
        if (bboLib.validateRaster(valFN) and bboLib.validateRaster(maskFN)):
            nLayers = nLayers + 1
            grass.mapcalc("$tmp1 = if(isnull($outVal), if(isnull($mask), null(), $value), $outVal)", tmp1=tmpVal1, outVal=outputFN, mask=maskFN, value=valFN, overwrite=True)
            grass.mapcalc("$outVal = $tmp1", outVal=outputFN, tmp1=tmpVal1, overwrite=True)
        year = year - 1
        trainingYears = trainingYears - 1

    bboLib.deleteRaster(tmpVal1)

    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)

    return (0 < nLayers)


def _aggregateBBSpots(yearFrom, yearTo, outputFN, targetMapset=None):
    bboLib.debugMessage("bboPrognosisLib._aggregateBBSpots")

    tmpVal1 = "tmp_bboplib_aggbbspot1"

    if (targetMapset):
        userMapset = grass.gisenv()["MAPSET"]  
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)
    
    grass.mapcalc("$outVal = null()", outVal=outputFN, overwrite=True)
    
    year = yearFrom
    while (year <= yearTo):
        bboFN = bboLib.replaceYearParameter(bboLib.spotTemplate, year, bboLib.forestMapset)
        if (bboLib.validateRaster(bboFN)):
            grass.run_command("r.patch", input=outputFN+ ',' + bboFN, output=tmpVal1, quiet=True, overwrite=True)            
            grass.mapcalc("$outVal = $tmp", outVal=outputFN, tmp=tmpVal1, overwrite=True)
        year = year + 1

    bboLib.deleteRaster(tmpVal1)

    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)


#endregion MASK



# #################### MORTALITY INDEX ####################
#region MORTALITY_INDEX
def _calcMortalityIndex(spotMapset, spotTemplate, yearFrom, yearTo, spotCode):
    bboLib.debugMessage("bboPrognosisLib._calcMortalityIndex")

    areaList = _getSpotAreas(spotMapset, spotTemplate, bboLib.updatedS50MaskTemplate, yearFrom - 1, yearTo)

    i = 0
    a0 = 0.0
    miList = []
    while ((i + yearFrom - 1)  <= yearTo):
        a1 = areaList[i][spotCode]
        if (a1 is None):
            a1 = 0.0
        if (0.0 < a1):
            if (0.0 < a0):
                s_mi = a1 / a0
                miList.append((i + yearFrom - 1, s_mi))
            a0 = areaList[i][NEW_SPOTCODE]
        else:
            a0 = 0.0
        i = i + 1
    
    return miList


def _calcMortalityIndexAll(spotMapset, aspotTemplate, yearFrom, yearTo):
    return _calcMortalityIndex(spotMapset, aspotTemplate, yearFrom, yearTo, ALL_SPOTCODE)

def _calcMortalityIndexSpread(spotMapset, aspotTemplate, yearFrom, yearTo):
    return _calcMortalityIndex(spotMapset, aspotTemplate, yearFrom, yearTo, SPREAD_SPOTCODE)

def _calcMortalityIndexInit(spotMapset, aspotTemplate, yearFrom, yearTo):
    return _calcMortalityIndex(spotMapset, aspotTemplate, yearFrom, yearTo, INIT_SPOTCODE)

def _calcMortalityIndexNew(spotMapset, aspotTemplate, yearFrom, yearTo):
    return _calcMortalityIndex(spotMapset, aspotTemplate, yearFrom, yearTo, NEW_SPOTCODE)


def _calcMISeries(yearFrom, yearTo, spotCode):
    bboLib.debugMessage("bboPrognosisLib._calcMISeries")

    miList = _calcMortalityIndex(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo, spotCode)

    valList = []
    y1 = yearFrom
    i = 0
    n = len(miList)
    while (y1 <= yearTo):
        val = None
        if (i < n):
            if (y1 == miList[i][0]):
                val = miList[i][1]
                i = i + 1
        valList.append(val)
        y1 = y1 + 1

    return valList


def _calcMISeriesStatistics(yearFrom, yearTo, spotCode):
    bboLib.debugMessage("bboPrognosisLib._calcMISeriesStatistics")

    intervalLength = 2
    yearMin = 999999
    yearMax = -999999

    lMax = []
    lMin = []
    iMinLength = []
    iMaxLength = []

    mi = _calcMISeries(yearFrom, yearTo, spotCode)

    y0 = 0
    while ((yearFrom + y0) <= yearTo):
        if (mi[y0] is not None):
            if ((y0 + yearFrom) < yearMin):
                yearMin = y0 + yearFrom
            if (yearMax < (y0 + yearFrom)):
                yearMax = y0 + yearFrom
        y0 = y0 + 1

    y0 = 0
    while ((yearFrom + y0) <= yearTo):
        if (y0 < intervalLength):
            isLMin = False
            isLMax = False
        else:
            if (mi[y0] is not None):
                isLMin = True
                isLMax = True
                for y1 in range(y0 - intervalLength, y0 + intervalLength):
                    if (y1 != 0 and 0 <= (y1 + yearFrom) and (y1 + yearFrom) <= yearTo):
                        if (mi[y1] is not None):
                            if (mi[y1] < mi[y0]):
                                isLMin = False
                            if (mi[y0] < mi[y1]):
                                isLMax = False
            else:
                isLMin = False
                isLMax = False
        lMin.append(isLMin)
        lMax.append(isLMax)
        y0 = y0 + 1

    y0 = 0
    i0 = -1
    while ((yearFrom + y0) <= yearTo):
        il = 0
        if (lMin[y0]):
            if (-1 < i0):
                il = y0 - i0
            i0 = y0
        iMinLength.append(il)
        y0 = y0 + 1

    y0 = 0
    i0 = -1
    while ((yearFrom + y0) <= yearTo):
        il = 0
        if (lMax[y0]):
            if (-1 < i0):
                il = y0 - i0
            i0 = y0
        iMaxLength.append(il)
        y0 = y0 + 1

    y0 = 0
    while ((yearFrom + y0) <= yearTo):
        if (yearMin <= (yearFrom + y0) and (yearFrom + y0) <= yearMax):
            bboLib.logMessage(str.format("{0} {1} {2} {3} {4} {5}", yearMin + y0, mi[y0], lMin[y0], iMinLength[y0], lMax[y0], iMaxLength[y0]))
        y0 = y0 + 1

    y0 = 0
    lcYear = -1
    while ((yearFrom + y0) <= yearTo):
        if (lMin[y0]):
            lcYear = y0
        y0 = y0 + 1
    lcYear = yearFrom + lcYear

    perLength = 4
    progYear = yearMax + 1
    perY = progYear - lcYear
    if (perLength <= perY):
        perY = 0

    minMI = 999999
    maxMI = -999999
    sumVal = 0
    sumVal2 = 0
    countVal = 0

    y0 = progYear - yearFrom
    while (0 <= y0):
        if ((yearFrom + y0) <= yearTo):
            if (mi[y0] is not None):
                countVal = countVal + 1
                sumVal = sumVal + mi[y0]
                sumVal2 = sumVal2 + mi[y0] * mi[y0]
                if (mi[y0] < minMI):
                    minMI = mi[y0]
                if (maxMI < mi[y0]):
                    maxMI = mi[y0]
        y0 = y0 - perLength

    avgMI = 0
    stdMI = 0
    if (0 < countVal):
        avgMI = sumVal / countVal
        stdMI = sumVal2 / countVal - avgMI * avgMI
        stdMI = math.sqrt(stdMI)

    optMI = avgMI - stdMI
    if (optMI < 0.0):
      optMI = 0.0  
    pesMI = avgMI + stdMI

    miStatistics = collections.namedtuple("miStatistics", "prognosisYear, periodBeginning, periodLength, periodYear, miMin, miMax, miAvg, miStd, miOptimistics, miPesimistics")
    return miStatistics(progYear, lcYear, perLength, perY, minMI, maxMI, avgMI, stdMI, optMI, pesMI)


def printMISeriesStatistics(yearFrom, yearTo, spotCode=NEW_SPOTCODE):
    bboLib.debugMessage("bboPrognosisLib.printMISeriesStatistics")

    miStat = _calcMISeriesStatistics(yearFrom, yearTo, spotCode)

    grass.message("***")
    grass.message(str.format("prognosis year: {0}", miStat.prognosisYear))
    grass.message(str.format("period beginning: {0}", miStat.periodBeginning))
    grass.message(str.format("period length: {0}", miStat.periodLength))
    grass.message(str.format("period year: {0}", miStat.periodYear))
    grass.message("---")
    grass.message("mortality index")
    grass.message(str.format("minimum: {0}", miStat.miMin))
    grass.message(str.format("maximum: {0}", miStat.miMax))
    grass.message(str.format("average: {0}", miStat.miAvg))
    grass.message(str.format("standard deviation: {0}", miStat.miStd))
    grass.message(str.format("optimistics: {0}", miStat.miOptimistics))
    grass.message(str.format("pesimistics: {0}", miStat.miPesimistics))

#endregion MORTALITY_INDEX



# #################### SPOT PROGNOSIS VALIDATION ####################
#region SPOT_PROGNOSIS_VALIDATION
def spotPrognosisVld(projectFN, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib.spotPrognosisVld")
    project = _readProject(projectFN)
    _spotPrognosis(project, yearFrom, yearTo)


def _spotPrognosis(project, yearFrom, yearTo, classifyPrognosis=True):
    bboLib.debugMessage("bboPrognosisLib._spotPrognosis")

    progMethodId = project["spotPrognosis"]["method"]
    if (progMethodId == SPOTPROGMETHODCODE_MAXPROBABILITY):
        spotPrognosisByAttackProbability(project, yearFrom, yearTo, 0, classifyPrognosis)
    elif (progMethodId == SPOTPROGMETHODCODE_RANDOMTODISTANCE):
        spotPrognosisRandomToDistance(project, yearFrom, yearTo)
    elif (progMethodId == SPOTPROGMETHODCODE_RANDOMGROWING):
        spotPrognosisRandomGrowing(project, yearFrom, yearTo)
    elif (progMethodId == SPOTPROGMETHODCODE_ATTACKTODISTANCE):
        spotPrognosisByAttackToDst(project, yearFrom, yearTo, 0)
    elif (progMethodId == SPOTPROGMETHODCODE_MAXINITSPREADPROB):
        spotPrognosisByMaxInitSpreadProb(project, yearFrom, yearTo, 0)
    else:
        bboLib.errorMessage("Invalid prognosis method")


#prognosis method == 301
def spotPrognosisByAttackProbability(project, yearFrom, yearTo, probOffset, classifyPrognosis=True):
    bboLib.debugMessage("bboPrognosisLib.spotPrognosisByAttackProbability")

    targetMapset = project["targetMapset"]
    attackTemplate = project["attackModel"]["outputFN"]
    progTemplate = project["spotPrognosis"]["spotFN"]
    progIdTemplate = project["spotPrognosis"]["spotIdFN"]
    
    miList = _calcMortalityIndexNew(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    
    for mi in miList:
        miYear = mi[0]
        miValue = mi[1]

        bboLib.debugMessage("spot prognosis validation year={0} mi={1}".format(miYear, miValue))

        spotSourceFN = bboLib.replaceYearParameter(bboLib.spotTemplate, miYear-1, bboLib.forestMapset)
        spotSourceIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, miYear-1, bboLib.forestMapset)
        
        attackProbFN = bboLib.replaceYearParameter(attackTemplate, miYear + probOffset)
        spotProgFN = bboLib.replaceYearParameter(progTemplate, miYear)
        spotProgIdFN = bboLib.replaceYearParameter(progIdTemplate, miYear)

        if (bboLib.validateRaster(spotSourceFN)):
            if (bboLib.validateRaster(attackProbFN)):
                _calcPrognosisByAttackProbability(targetMapset, bboLib.forestS50Mask, 
                                                 spotSourceFN, attackProbFN, miValue, spotProgFN, SPOT_PROGNOSIS_NSTEPS)
                bboLib.spotClassificationFN(targetMapset, 
                                            spotSourceFN, spotSourceIdFN, 
                                            spotProgFN, spotProgIdFN, classifyPrognosis)

def _calcPrognosisByAttackProbability(targetMapset, s50MaskFN, 
                                      spotSource, bbAttackProb, treeMortality, 
                                      spotPrognosis, nSteps):
    bboLib.debugMessage("bboPrognosisLib._calcPrognosisByAttackProbability")

    userMapset = grass.gisenv()["MAPSET"] 
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    bboLib.debugMessage("spot prognosis: {0}   mortality: {1}".format(spotPrognosis, treeMortality))

    actualSpot = "tmp_bboplib_pcalc_spot"
    actualSpot0 = "tmp_bboplib_pcalc_spot0"
    actualNSpot = "tmp_bboplib_pcalc_nspot"
    actualNSpot0 = "tmp_bboplib_pcalc_nspot0"
    actualS50Mask = "tmp_bboplib_pcalc_s50mask"
    tmp1 = "tmp_bboplib_pcalc_tmp1"
    tmp2 = "tmp_bboplib_pcalc_tmp2"

    # prepare actualSpot
    grass.mapcalc("$tmp1 = $spotSource * $s50Mask", tmp1=tmp1, spotSource=spotSource, s50Mask=s50MaskFN, overwrite=True)
    grass.mapcalc("$actualSpot = if(0 < $tmp1, 1, null())", actualSpot=actualSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualSpot0 = $actualSpot", actualSpot0=actualSpot0, actualSpot=actualSpot, overwrite=True)
    grass.run_command("r.null", map=actualSpot0, null=0, quiet=True)
    
    # prepare actualNSpot
    grass.mapcalc("$actualNSpot = if(1 < $tmp1, 1, null())", actualNSpot=actualNSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualNSpot0 = if(1 < $tmp1, 1, 0)", actualNSpot0=actualNSpot0, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualNSpot0, null=0, quiet=True)

    # actual forest mask
    grass.mapcalc("$actualS50Mask = $s50Mask - $actualSpot0", actualS50Mask=actualS50Mask, s50Mask=s50MaskFN, actualSpot0=actualSpot0, overwrite=True)
    grass.run_command("r.null", map=actualS50Mask, setnull=0, quiet=True)

    # spot prognosis
    initArea = bboLib.getRasterArea(actualNSpot)
    targetArea = treeMortality * initArea
    lBound = 0.5
    dStep = 0.25
    grass.mapcalc("$tmp1 = $actualS50Mask * $bbAttackProb", tmp1=tmp1, actualS50Mask=actualS50Mask, bbAttackProb=bbAttackProb, overwrite=True)

    grass.mapcalc("$spotPrognosis = if(1 <= $tmp1, 1, null())", spotPrognosis=spotPrognosis, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=spotPrognosis, setnull=0, quiet=True)
    cArea = bboLib.getRasterArea(spotPrognosis)
    if (targetArea <= cArea):
        nSteps = 0

    while (0 < nSteps):
        grass.mapcalc("$spotPrognosis = if($lBound <= $tmp1, 1)", spotPrognosis=spotPrognosis, lBound=lBound, tmp1=tmp1, overwrite=True)
        grass.run_command("r.null", map=spotPrognosis, setnull=0, quiet=True)
        cArea = bboLib.getRasterArea(spotPrognosis)
        if (cArea < targetArea):
            lBound = lBound - dStep
        if (targetArea < cArea):
            lBound = lBound + dStep
        if (cArea == targetArea):
            nSteps = 0
        nSteps = nSteps - 1
        dStep = dStep / 2.0

    grass.run_command("r.null", map=spotPrognosis, null=0, quiet=True)
    grass.mapcalc("$tmp1 = if(0 < $spotPrognosis, 1, $actualSpot)", spotPrognosis=spotPrognosis, tmp1=tmp1, actualSpot=actualSpot, overwrite=True)
    grass.mapcalc("$spotPrognosis = $tmp1", spotPrognosis=spotPrognosis, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=spotPrognosis, setnull=0, quiet=True)

    bboLib.deleteRaster(actualSpot)
    bboLib.deleteRaster(actualSpot0)
    bboLib.deleteRaster(actualNSpot)
    bboLib.deleteRaster(actualNSpot0)
    bboLib.deleteRaster(actualS50Mask)
    bboLib.deleteRaster(tmp1)
    bboLib.deleteRaster(tmp2)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


#prognosis method == 302
def spotPrognosisRandomToDistance(project, yearFrom, yearTo):
    targetMapset = project["targetMapset"]
    progTemplate = project["spotPrognosis"]["spotFN"]
    progIdTemplate = project["spotPrognosis"]["spotIdFN"]
    progMaxDst = project["spotPrognosis"]["maxDistance"]
    
    bboLib.debugMessage("bboPrognosisLib.spotPrognosisRandomToDistance")

    miList = _calcMortalityIndexNew(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    
    for mi in miList:
        miYear = mi[0]
        miValue = mi[1]

        bboLib.debugMessage("spot prognosis validation year={0} mi={1}".format(miYear, miValue))

        spotFN = bboLib.replaceYearParameter(bboLib.spotTemplate, miYear-1, bboLib.forestMapset)
        spotIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, miYear-1, bboLib.forestMapset)

        if (0 < miValue):
            progFN = bboLib.replaceYearParameter(progTemplate, miYear)
            progIdFN = bboLib.replaceYearParameter(progIdTemplate, miYear)
            s50Mask = bboLib.replaceYearParameter(bboLib.forestS50Mask, miYear)

            if (bboLib.validateRaster(spotFN)):
                if (bboLib.validateRaster(spotIdFN)):
                    _calcPrognosisRandomByDistance(targetMapset, s50Mask, 
                                                  spotFN, miValue, progMaxDst, progFN)
                    bboLib.spotClassificationFN(targetMapset, 
                                                spotFN, spotIdFN, 
                                                progFN, progIdFN)

def _calcPrognosisRandomByDistance(targetMapset, s50MaskFN, 
                                   spotFN, treeMortality, maxDst, progFN):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    bboLib.debugMessage(str.format("spot prognosis: {0}   mortality: {1}   distance: {2}", progFN, treeMortality, maxDst))  

    actualSpot = "tmp_bboplib_rdst_spot"
    actualSpot0 = "tmp_bboplib_rdst_spot0"
    actualNSpot = "tmp_bboplib_rdst_nspot"
    actualNSpot0 = "tmp_bboplib_rdst_nspot0"
    actualS50Mask = "tmp_bboplib_rdst_s50mask"
    actualSpotBuf = "tmp_bboplib_rdst_buf"
    actualSpotBufMask = "tmp_bboplib_rdst_bufmask"
    tmp1 = "tmp_bboplib_rdst_tmp1"

    # prepare actualSpot
    grass.mapcalc("$tmp1 = $spotSource * $s50Mask", tmp1=tmp1, spotSource=spotFN, s50Mask=s50MaskFN, overwrite=True)
    grass.mapcalc("$actualSpot = if(0 < $tmp1, 1, null())", actualSpot=actualSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualSpot0 = $actualSpot", actualSpot0=actualSpot0, actualSpot=actualSpot, overwrite=True)
    grass.run_command("r.null", map=actualSpot0, null=0, quiet=True)
    
    # prepare actualNSpot
    grass.mapcalc("$actualNSpot = if(1 < $tmp1, 1, null())", actualNSpot=actualNSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualNSpot0 = if(1 < $tmp1, 1, 0)", actualNSpot0=actualNSpot0, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualNSpot0, null=0, quiet=True)

    # actual forest mask
    grass.mapcalc("$actualS50Mask = $s50Mask - $actualSpot0", actualS50Mask=actualS50Mask, s50Mask=s50MaskFN, actualSpot0=actualSpot0, overwrite=True)
    grass.run_command("r.null", map=actualS50Mask, setnull=0, quiet=True)

    # spot prognosis
    grass.run_command("r.buffer", input=actualNSpot, output=actualSpotBuf, distances=str(maxDst), quiet=True)
    grass.mapcalc("$tmp1 = $buf * $s50Mask", tmp1=tmp1, buf=actualSpotBuf, s50Mask=actualS50Mask, overwrite=True)
    grass.mapcalc("$bufMask = if(0 < $tmp1, 1, null())", bufMask=actualSpotBufMask, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualSpotBufMask, setnull=0, quiet=True)

    prevSpotCells = bboLib.getNotNullCellsNumber(actualNSpot)
    progCells =  math.ceil(treeMortality * prevSpotCells)
    bboLib.debugMessage("progCells: {0}".format(progCells))

    if (0 < progCells):
        grass.run_command("r.random", input=actualSpotBufMask, raster=tmp1, npoints=progCells, overwrite=True, quiet=True)
        grass.run_command("r.null", map=tmp1, null=0, quiet=True)
        grass.mapcalc("$spotProg = if(0 < $tmp1, 1, $actualSpot)", spotProg=progFN, tmp1=tmp1, actualSpot=actualSpot, overwrite=True)
        grass.run_command("r.null", map=progFN, setnull=0, quiet=True)

    bboLib.deleteRaster(actualSpot)
    bboLib.deleteRaster(actualSpot0)
    bboLib.deleteRaster(actualNSpot)
    bboLib.deleteRaster(actualNSpot0)
    bboLib.deleteRaster(actualS50Mask)
    bboLib.deleteRaster(actualSpotBuf)
    bboLib.deleteRaster(actualSpotBufMask)
    bboLib.deleteRaster(tmp1)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


#prognosis method == 303
def spotPrognosisRandomGrowing(project, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib.spotPrognosisRandomGrowing")

    targetMapset = project["targetMapset"]
    progTemplate = project["spotPrognosis"]["spotFN"]
    progIdTemplate = project["spotPrognosis"]["spotIdFN"]
    
    miList = _calcMortalityIndexNew(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    
    for mi in miList:
        miYear = mi[0]
        miValue = mi[1]

        bboLib.debugMessage("spot prognosis validation year={0} mi={1}".format(miYear, miValue))

        spotFN = bboLib.replaceYearParameter(bboLib.spotTemplate, miYear-1, bboLib.forestMapset)
        spotIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, miYear-1, bboLib.forestMapset)

        if (0 < miValue):
            progFN = bboLib.replaceYearParameter(progTemplate, miYear)
            progIdFN = bboLib.replaceYearParameter(progIdTemplate, miYear)
            s50Mask = bboLib.replaceYearParameter(bboLib.forestS50Mask, miYear)

            if (bboLib.validateRaster(spotFN)):
                if (bboLib.validateRaster(spotIdFN)):
                    _calcPrognosisRandomGrowing(targetMapset, s50Mask, spotFN, miValue, progFN)
                    bboLib.spotClassificationFN(targetMapset, spotFN, spotIdFN, progFN, progIdFN)

def _calcPrognosisRandomGrowing(targetMapset, s50MaskFN, 
                                spotFN, treeMortality, progFN):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    bboLib.debugMessage(str.format("spot prognosis: {0}   mortality: {1}", progFN, treeMortality))  

    actualSpot = "tmp_bboplib_rdst_spot"
    actualSpot0 = "tmp_bboplib_rdst_spot0"
    actualNSpot = "tmp_bboplib_rdst_nspot"
    actualNSpot0 = "tmp_bboplib_rdst_nspot0"
    actualS50Mask = "tmp_bboplib_rdst_s50mask"
    actualSpotBuf = "tmp_bboplib_rdst_buf"
    actualSpotBufMask = "tmp_bboplib_rdst_bufmask"
    tmp1 = "tmp_bboplib_rdst_tmp1"
    
    # prepare actualSpot
    grass.mapcalc("$tmp1 = $spotSource * $s50Mask", tmp1=tmp1, spotSource=spotFN, s50Mask=s50MaskFN, overwrite=True)
    grass.mapcalc("$actualSpot = if(0 < $tmp1, 1, null())", actualSpot=actualSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualSpot0 = $actualSpot", actualSpot0=actualSpot0, actualSpot=actualSpot, overwrite=True)
    grass.run_command("r.null", map=actualSpot0, null=0, quiet=True)
    
    # prepare actualNSpot
    grass.mapcalc("$actualNSpot = if(1 < $tmp1, 1, null())", actualNSpot=actualNSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualNSpot0 = if(1 < $tmp1, 1, 0)", actualNSpot0=actualNSpot0, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualNSpot0, null=0, quiet=True)

    # actual forest mask
    grass.mapcalc("$actualS50Mask = $s50Mask - $actualSpot0", actualS50Mask=actualS50Mask, s50Mask=s50MaskFN, actualSpot0=actualSpot0, overwrite=True)
    grass.run_command("r.null", map=actualS50Mask, setnull=0, quiet=True)

    # spot prognosis
    prevNSpotArea = bboLib.getRasterArea(actualNSpot)
    progNSpotArea =  treeMortality * prevNSpotArea
    maskNSpotArea = 0
    grass.mapcalc("$spotBuf = $actualNSpot", spotBuf=actualSpotBuf, actualNSpot=actualNSpot, overwrite=True)

    while (maskNSpotArea < progNSpotArea):
        grass.run_command("r.grow", input=actualSpotBuf, output=tmp1, old=1, new=1, quiet=True, overwrite=True)
        grass.mapcalc("$spotBuf = $tmp1", tmp1=tmp1, spotBuf=actualSpotBuf, overwrite=True)
        grass.mapcalc("$bufMask = $tmp1 * $s50Mask", tmp1=tmp1, s50Mask=actualS50Mask, bufMask=actualSpotBufMask, overwrite=True)
        grass.run_command("r.null", map=actualSpotBufMask, setnull=0, quiet=True)
        maskNSpotArea = bboLib.getRasterArea(actualSpotBufMask)

    prevSpotCells = bboLib.getNotNullCellsNumber(actualNSpot)
    progCells =  math.ceil(treeMortality * prevSpotCells)
    bboLib.debugMessage("progCells: {0}".format(progCells))

    if (0 < progCells):
        grass.run_command("r.random", input=actualSpotBufMask, raster=tmp1, npoints=progCells, overwrite=True, quiet=True)
        grass.run_command("r.null", map=tmp1, null=0, quiet=True)
        grass.mapcalc("$spotProg = if(0 < $tmp1, 1, $actualSpot)", spotProg=progFN, tmp1=tmp1, actualSpot=actualSpot, overwrite=True)
        grass.run_command("r.null", map=progFN, setnull=0, quiet=True)

    bboLib.deleteRaster(actualSpot)
    bboLib.deleteRaster(actualSpot0)
    bboLib.deleteRaster(actualNSpot)
    bboLib.deleteRaster(actualNSpot0)
    bboLib.deleteRaster(actualS50Mask)
    bboLib.deleteRaster(actualSpotBuf)
    bboLib.deleteRaster(actualSpotBufMask)
    bboLib.deleteRaster(tmp1)
    
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


#prognosis method == 304
def spotPrognosisByAttackToDst(project, yearFrom, yearTo, probOffset):
    bboLib.debugMessage("bboPrognosisLib.spotPrognosisByAttackProbability")

    targetMapset = project["targetMapset"]
    attackTemplate = project["attackModel"]["outputFN"]
    progTemplate = project["spotPrognosis"]["spotFN"]
    progIdTemplate = project["spotPrognosis"]["spotIdFN"]
    progMaxDst = project["spotPrognosis"]["maxDistance"]
    
    miList = _calcMortalityIndexNew(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    
    for mi in miList:
        miYear = mi[0]
        miValue = mi[1]

        bboLib.debugMessage("spot prognosis validation year={0} mi={1}".format(miYear, miValue))

        spotFN = bboLib.replaceYearParameter(bboLib.spotTemplate, miYear-1, bboLib.forestMapset)
        spotIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, miYear-1, bboLib.forestMapset)
        
        attackProbFN = bboLib.replaceYearParameter(attackTemplate, miYear + probOffset)
        progFN = bboLib.replaceYearParameter(progTemplate, miYear)
        progIdFN = bboLib.replaceYearParameter(progIdTemplate, miYear)

        if (bboLib.validateRaster(spotFN)):
            if (bboLib.validateRaster(attackProbFN)):
                _calcPrognosisByAttackToDst(targetMapset, bboLib.forestS50Mask, 
                                           spotFN, attackProbFN, miValue, progMaxDst, 
                                           progFN, SPOT_PROGNOSIS_NSTEPS)
                bboLib.spotClassificationFN(targetMapset, spotFN, spotIdFN, progFN, progIdFN)

def _calcPrognosisByAttackToDst(targetMapset, s50MaskFN, 
                                spotSource, bbAttackProb, treeMortality, maxDst,
                                spotPrognosis, nSteps):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    bboLib.debugMessage(str.format("spot prognosis: {0}   mortality: {1}", spotPrognosis, treeMortality))  

    actualSpot = "tmp_bboplib_pdst_spot"
    actualSpot0 = "tmp_bboplib_pdst_spot0"
    actualNSpot = "tmp_bboplib_pdst_nspot"
    actualNSpot0 = "tmp_bboplib_pdst_nspot0"
    actualS50Mask = "tmp_bboplib_pdst_s50mask"
    actualSpotBuf = "tmp_bboplib_pdst_buf"
    actualSpotBufMask = "tmp_bboplib_pdst_bufmask"    
    tmp1 = "tmp_bboplib_pdst_tmp1"
    tmp2 = "tmp_bboplib_pdst_tmp2"

    # prepare actualSpot
    grass.mapcalc("$tmp1 = $spotSource * $s50Mask", tmp1=tmp1, spotSource=spotSource, s50Mask=s50MaskFN, overwrite=True)
    grass.mapcalc("$actualSpot = if(0 < $tmp1, 1, null())", actualSpot=actualSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualSpot0 = $actualSpot", actualSpot0=actualSpot0, actualSpot=actualSpot, overwrite=True)
    grass.run_command("r.null", map=actualSpot0, null=0, quiet=True)
    
    # prepare actualNSpot
    grass.mapcalc("$actualNSpot = if(1 < $tmp1, 1, null())", actualNSpot=actualNSpot, tmp1=tmp1, overwrite=True)
    grass.mapcalc("$actualNSpot0 = if(1 < $tmp1, 1, 0)", actualNSpot0=actualNSpot0, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualNSpot0, null=0, quiet=True)

    # actual forest mask
    grass.mapcalc("$actualS50Mask = $s50Mask - $actualSpot0", actualS50Mask=actualS50Mask, s50Mask=s50MaskFN, actualSpot0=actualSpot0, overwrite=True)
    grass.run_command("r.null", map=actualS50Mask, setnull=0, quiet=True)

    # spot prognosis
    grass.run_command("r.buffer", input=actualNSpot, output=actualSpotBuf, distances=str(maxDst), quiet=True)
    grass.mapcalc("$tmp1 = $buf * $s50Mask", tmp1=tmp1, buf=actualSpotBuf, s50Mask=actualS50Mask, overwrite=True)
    grass.mapcalc("$bufMask = if(0 < $tmp1, 1, null())", bufMask=actualSpotBufMask, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualSpotBufMask, setnull=0, quiet=True)

    initArea = bboLib.getRasterArea(actualNSpot)
    targetArea = treeMortality * initArea
    lBound = 0.5
    dStep = 0.25
    grass.mapcalc("$tmp1 = $bufMask * $bbAttackProb", tmp1=tmp1, bufMask=actualSpotBufMask, bbAttackProb=bbAttackProb, overwrite=True)

    while (0 < nSteps):
        grass.mapcalc("$spotPrognosis = if($lBound <= $tmp1, 1)", spotPrognosis=spotPrognosis, lBound=lBound, tmp1=tmp1, overwrite=True)
        grass.run_command("r.null", map=spotPrognosis, setnull=0, quiet=True)
        cArea = bboLib.getRasterArea(spotPrognosis)
        if (cArea < targetArea):
            lBound = lBound - dStep
        if (targetArea < cArea):
            lBound = lBound + dStep
        if (cArea == targetArea):
            nSteps = 0
        nSteps = nSteps - 1
        dStep = dStep / 2.0

    grass.run_command("r.null", map=spotPrognosis, null=0, quiet=True)
    grass.mapcalc("$tmp1 = if(0 < $spotPrognosis, 1, $actualSpot)", spotPrognosis=spotPrognosis, tmp1=tmp1, actualSpot=actualSpot, overwrite=True)
    grass.mapcalc("$spotPrognosis = $tmp1", spotPrognosis=spotPrognosis, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=spotPrognosis, setnull=0, quiet=True)

    bboLib.deleteRaster(actualSpot)
    bboLib.deleteRaster(actualSpot0)
    bboLib.deleteRaster(actualNSpot)
    bboLib.deleteRaster(actualNSpot0)
    bboLib.deleteRaster(actualS50Mask)
    bboLib.deleteRaster(actualSpotBuf)
    bboLib.deleteRaster(actualSpotBufMask)
    bboLib.deleteRaster(tmp1)
    bboLib.deleteRaster(tmp2)

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


#prognosis method == 305
def spotPrognosisByMaxInitSpreadProb(project, yearFrom, yearTo, probOffset):
    bboLib.debugMessage("bboPrognosisLib.spotPrognosisByMaxInitSpreadProb")

    targetMapset = project["targetMapset"]
    spotProgTemplate = project["spotPrognosis"]["spotFN"]
    spotIdProgTemplate = project["spotPrognosis"]["spotIdFN"]

    spreadProbTemplate = project["spreadModel"]["outputFN"]
    initProbTemplate = project["initModel"]["outputFN"]
    
    spreadMI = _calcMortalityIndexSpread(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    initMI = _calcMortalityIndexInit(bboLib.forestMapset, bboLib.spotTemplate, yearFrom, yearTo)
    
    spreadSpotProgTemplate = "tmp_bboplib_spmisp_s%Y"
    initSpotProgTemplate = "tmp_bboplib_spmisp_i%Y"

    userMapset = grass.gisenv()["MAPSET"]  
    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=targetMapset)

    _calcPartialSpotPrognosis(project["spotPrognosis"]["spreadMethod"], targetMapset, spreadMI, spreadProbTemplate, 
                              spreadSpotProgTemplate, project["spotPrognosis"]["spreadMaxDistance"], "spread", probOffset)

    _calcPartialSpotPrognosis(project["spotPrognosis"]["initMethod"], targetMapset, initMI, initProbTemplate, 
                              initSpotProgTemplate, project["spotPrognosis"]["initMaxDistance"], "init", probOffset)

    # join spot prognoses
    year = yearFrom
    while (year <= yearTo):
        spotSourceFN = bboLib.replaceYearParameter(bboLib.spotTemplate, year-1, bboLib.forestMapset)
        spotSourceIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, year-1, bboLib.forestMapset)

        spreadSpotProgFN = bboLib.replaceYearParameter(spreadSpotProgTemplate, year)
        initSpotProgFN = bboLib.replaceYearParameter(initSpotProgTemplate, year)
        outSpotProgFN = bboLib.replaceYearParameter(spotProgTemplate, year)
        outSpotIdProgFN = bboLib.replaceYearParameter(spotIdProgTemplate, year)

        if (bboLib.validateRaster(spreadSpotProgFN) and bboLib.validateRaster(initSpotProgFN)):
            grass.message("spot prognosis {0}".format(year))
            grass.mapcalc("$outProg = if(isnull($spreadProg), $initProg, $spreadProg)", outProg=outSpotProgFN, spreadProg=spreadSpotProgFN, initProg=initSpotProgFN, overwrite=True)
            bboLib.spotClassificationFN(targetMapset, spotSourceFN, spotSourceIdFN, outSpotProgFN, outSpotIdProgFN)
        else:
            bboLib.deleteRaster(outSpotProgFN)
            bboLib.deleteRaster(outSpotIdProgFN)

        year = year + 1

    bboLib.deleteYearSeries(targetMapset, spreadSpotProgTemplate, yearFrom, yearTo)
    bboLib.deleteYearSeries(targetMapset, initSpotProgTemplate, yearFrom, yearTo)

    if (targetMapset):
        if (not (userMapset == targetMapset)):
            grass.run_command("g.mapset", mapset=userMapset)


def _calcPartialSpotPrognosis(progMethod, targetMapset, miList, probTemplate, spotProgTemplate, maxDistance=0.0, outputMsg=None, probOffset=0):
    bboLib.debugMessage("bboPrognosisLib._calcPartialSpotPrognosis")

    for mi in miList:
        miYear = mi[0]
        miValue = mi[1]

        if (outputMsg):
            grass.message("{2} spot prognosis year={0} mi={1}".format(miYear, miValue, outputMsg))
        else:
            grass.message("spot prognosis year={0} mi={1}".format(miYear, miValue, outputMsg))

        spotSourceFN = bboLib.replaceYearParameter(bboLib.spotTemplate, miYear-1, bboLib.forestMapset)
        
        probFN = bboLib.replaceYearParameter(probTemplate, miYear + probOffset)
        spotProgFN = bboLib.replaceYearParameter(spotProgTemplate, miYear)

        s50MaskFN = bboLib.replaceYearParameter(bboLib.s50MaskTemplate, miYear, bboLib.forestMapset)

        if (bboLib.validateRaster(spotSourceFN)):
            if (bboLib.validateRaster(probFN)):
                if (progMethod == SPOTPROGMETHODCODE_MAXPROBABILITY):
                    _calcPrognosisByAttackProbability(targetMapset, s50MaskFN, 
                                                      spotSourceFN, probFN, miValue, spotProgFN, SPOT_PROGNOSIS_NSTEPS)
                elif (progMethod == SPOTPROGMETHODCODE_RANDOMTODISTANCE):
                    _calcPrognosisRandomByDistance(targetMapset, s50MaskFN, spotSourceFN, miValue, maxDistance, spotProgFN)
                elif (progMethod == SPOTPROGMETHODCODE_RANDOMGROWING):
                    _calcPrognosisRandomGrowing(targetMapset, s50MaskFN, spotSourceFN, miValue, spotProgFN)
                elif (progMethod == SPOTPROGMETHODCODE_ATTACKTODISTANCE):
                    _calcPrognosisByAttackToDst(targetMapset, s50MaskFN, spotSourceFN, probFN, miValue, maxDistance, spotProgFN, SPOT_PROGNOSIS_NSTEPS)
                else:
                    if (outputMsg):
                        bboLib.errorMessage("unknown {0} spot prognosis method".format(outputMsg))
                    else:
                        bboLib.errorMessage("unknown partial spot prognosis method")

#endregion SPOT_PROGNOSIS_VALIDATION



# #################### SPOT PROGNOSIS ####################
#region SPOT_PROGNOSIS
def spotPrognosis(targetMapset, progMethodId, attackTemplate, progYear, mortalityIndex, progMaxDst, progTemplate, progIdTemplate):
    bboLib.debugMessage("bboPrognosisLib.spotPrognosis")

    bError = True

    spotSourceFN = bboLib.replaceYearParameter(bboLib.spotTemplate, progYear - 1, bboLib.forestMapset)
    spotSourceIdFN = bboLib.replaceYearParameter(bboLib.spotidTemplate, progYear - 1, bboLib.forestMapset)      
    attackProbFN = bboLib.replaceYearParameter(attackTemplate, progYear - 1)

    spotProgFN = bboLib.replaceYearParameter(progTemplate, progYear)
    spotProgIdFN = bboLib.replaceYearParameter(progIdTemplate, progYear)
    bboLib.deleteRaster(spotProgFN)
    bboLib.deleteRaster(spotProgIdFN)

    if (progMethodId == SPOTPROGMETHODCODE_MAXPROBABILITY):
        if (bboLib.validateRaster(spotSourceFN)):
            if (bboLib.validateRaster(attackProbFN)):
                _calcPrognosisByAttackProbability(targetMapset, bboLib.forestS50Mask, spotSourceFN, attackProbFN, mortalityIndex, spotProgFN, SPOT_PROGNOSIS_NSTEPS)
                bError = False
    elif (progMethodId == SPOTPROGMETHODCODE_RANDOMTODISTANCE):
        if (bboLib.validateRaster(spotSourceFN)):
            if (bboLib.validateRaster(spotSourceIdFN)):
                _calcPrognosisRandomByDistance(targetMapset, bboLib.s50Mask, spotSourceFN, mortalityIndex, progMaxDst, spotProgFN)    
                bError = False
    elif (progMethodId == SPOTPROGMETHODCODE_RANDOMGROWING):
        if (bboLib.validateRaster(spotSourceFN)):
            if (bboLib.validateRaster(spotSourceIdFN)):
                _calcPrognosisRandomGrowing(targetMapset, bboLib.s50Mask, spotSourceFN, mortalityIndex, spotProgFN)
                bError = False
    elif (progMethodId == SPOTPROGMETHODCODE_ATTACKTODISTANCE):
        if (bboLib.validateRaster(spotSourceFN)):
            if (bboLib.validateRaster(attackProbFN)):
                _calcPrognosisByAttackToDst(targetMapset, bboLib.forestS50Mask, spotSourceFN, attackProbFN, mortalityIndex, progMaxDst, spotProgFN, SPOT_PROGNOSIS_NSTEPS)
                bError = False
    else:
        bboLib.errorMessage("Invalid prognosis method")

    if(not bError):
        bboLib.spotClassificationFN(targetMapset, spotSourceFN, spotSourceIdFN, spotProgFN, spotProgIdFN)


def findLastSpotYear():
    targetMapset = bboLib.forestMapset

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    y = bboLib.defaultYearTo
    lastSpotYear = 0
    while (bboLib.defaultYearFrom <= y and lastSpotYear == 0):
        rasterName = bboLib.replaceYearParameter(bboLib.spotTemplate, y)
        if grass.find_file(rasterName)['file']:
            lastSpotYear = y
        y = y - 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return lastSpotYear


def findLastPrognoseYear(lastSpotYear, targetMapset, prognoseSpotTemplate):
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    y = bboLib.defaultYearTo
    lastProgYear = lastSpotYear
    while (lastSpotYear < y and lastProgYear == lastSpotYear):
        rasterName = bboLib.replaceYearParameter(prognoseSpotTemplate, y)
        if grass.find_file(rasterName)['file']:
            lastProgYear = y
        y = y - 1

    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return lastProgYear


# unused procedure nextYearPrognosis
def nextYearPrognosis(paramFN):
    params = _readProject(paramFN)
    targetMapset = params["targetMapset"]
    progMethodId = params["spotPrognosis"]["method"]
    progMaxDst = params["spotPrognosis"]["maxDistance"]
    attackTemplate = params["attackModel"]["outputFN"]
    yearFrom = params["yearFrom"]
    yearTo = params["yearTo"]

    miStat = _calcMISeries(yearFrom, yearTo)

    progYear = miStat.prognosisYear
    lastSpotYear = progYear - 1
    bboLib.logMessage("\n")
    bboLib.logMessage("last spot year {0}".format(lastSpotYear))
    bboLib.logMessage("prognosis year {0}".format(progYear))

    bboLib.logMessage("\n")
    bboLib.logMessage("*** neutral prognosis ***")
    progFN = bboLib.replaceYearParameter(params[progSpot], progYear)
    progIdFN = bboLib.replaceYearParameter(params[progSpotId], progYear)
    spotPrognosis(targetMapset, progMethodId, attackTemplate, progYear, miStat.miAvg, progMaxDst, progFN, progIdFN)

    bboLib.logMessage("\n")
    bboLib.logMessage("*** pesimistics prognosis ***")
    progFN = bboLib.replaceYearParameter(params[progPSpot], progYear)
    progIdFN = bboLib.replaceYearParameter(params[progPSpotId], progYear)
    spotPrognosis(targetMapset, progMethodId, attackTemplate, progYear, miStat.miPesimistics, progMaxDst, progFN, progIdFN)

    bboLib.logMessage("\n")
    bboLib.logMessage("*** optimistics prognosis ***")
    progFN = bboLib.replaceYearParameter(params[progOSpot], progYear)
    progIdFN = bboLib.replaceYearParameter(params[progOSpotId], progYear)
    spotPrognosis(targetMapset, progMethodId, attackTemplate, progYear, miStat.miOptimistics, progMaxDst, progFN, progIdFN)
    
    return

#endregion SPOT_PROGNOSIS



# #################### SPOT CROSSTABULATION ####################
#region SPOT_CROSSTABULATION
def spotCrosstabParamVld(projectFN, yearFrom, yearTo, printSeries=False, printTable=True, logFile=None):
    bboLib.debugMessage("bboPrognosisLib.spotCrosstabParamVld")
    project = _readProject(projectFN)
    _spotCrosstabValidation(project, yearFrom, yearTo, printSeries, printTable, logFile)


def _spotCrosstabValidation(project, yearFrom, yearTo, 
                            printSeries=False, printTable=True, 
                            logFile=None, ctabFile=None, sumctabFile=None, 
                            iMethod=None, sMethod=None, aMethod=None, bitLayers=None):
    bboLib.debugMessage("bboPrognosisLib._spotCrosstabValidation")

    targetMapset = project["targetMapset"]
    progTemplate = project["spotPrognosis"]["spotFN"]

    sumCTab = []
    for v1 in range(0, 4):
        l = [0, 0, 0, 0]
        sumCTab.append(l)

    nYears = 0
    for year in range(yearFrom, yearTo + 1):
        spotFN = bboLib.replaceYearParameter(bboLib.spotTemplate, year, bboLib.forestMapset)
        s50MaskFN = bboLib.replaceYearParameter(bboLib.s50MaskTemplate, year, bboLib.forestMapset)
        progFN = bboLib.replaceYearParameter(progTemplate, year, targetMapset)
        if (bboLib.validateRaster(spotFN) is not None):
            if (bboLib.validateRaster(progFN) is not None):
                nYears = nYears + 1
                bboLib.logMessage("\nspot cross tabulation {0}".format(year), logFile)
                ctab = _spotCrossTable(targetMapset, s50MaskFN, spotFN, progFN, printSeries, printTable, logFile)
                _writeCrossTable(ctabFile, ctab, year, iMethod, sMethod, aMethod, bitLayers)
                bboLib.logMessage("", logFile)
                for v1 in range(0, 4):
                    for v2 in range(0, 4):
                        sumCTab[v1][v2] = sumCTab[v1][v2] + ctab[v1][v2]

    if (printTable):
        bboLib.logMessage("\nsummary for years {0} - {1}".format(yearFrom, yearTo), logFile)
        _printCrossTable(sumCTab, logFile)
        bboLib.logMessage("\n\n", logFile)
    
    _writeCrossTable(sumctabFile, sumCTab, None, iMethod, sMethod, aMethod, bitLayers)

    return sumCTab


def _printCrossTable(crossTab, logFile=None):
    bboLib.debugMessage("bboPrognosisLib._printCrossTable")

    t = ["forest", "old spot", "spread", "init"]
    bboLib.logMessage("|{0: ^11}|{1: ^48s}".format("recorded", "spot prognosis"), logFile)
    bboLib.logMessage("|{0: ^11}|{1:-^48}".format("spots", ""), logFile)
    bboLib.logMessage("{4: <12}|{0:>12}{1:>12}{2:>12}{3:>12}".format(t[0], t[1], t[2], t[3], "|"), logFile)
    bboLib.logMessage("|{0:->11}|{0:-^48}".format(""), logFile)

    for v1 in range(0, 4):
        s = "|{:<11}|".format(t[v1])
        for v2 in range(0, 4):
            s = s + "{0:12}".format(crossTab[v1][v2])
        bboLib.logMessage(s, logFile)
    bboLib.logMessage("|{0:-^11}|{0:-^48}".format(""), logFile)


def _writeCrossTableHeader(csvFile, bYear, bInit, bSpread, bAttack, layers):
    bboLib.debugMessage("bboPrognosisLib._writeCrossTableHeader")

    if (csvFile):
        if (bYear):
            h = "year"
        else:
            h = None

        if (bInit):
            if (h):
                h = "{0};{1}".format(h, "iMethod")
            else:
                h = "iMethod"

        if (bSpread):
            if (h):
                h = "{0};{1}".format(h, "sMethod")
            else:
                h = "sMethod"

        if (bAttack):
            if (h):
                h = "{0};{1}".format(h, "aMethod")
            else:
                h = "aMethod"

        if (layers):
            i = 1
            for l in layers:
                h = "{0};L{1}".format(h, i)
                i = i + 1

        crosstabFields = ["forest", "oldspot", "spread", "init"]
        for v1 in range(0, 4):
            for v2 in range(0, 4):
                h = "{0};{1}_{2}".format(h, crosstabFields[v1], crosstabFields[v2])

        csvFile.writelines("{0}\n".format(h))


def _writeCrossTable(csvFile, crossTab, year, iMethod, sMethod, aMethod, bitLayers):
    bboLib.debugMessage("bboPrognosisLib._writeCrossTable")

    if (csvFile):
        if (crossTab):
            if (year):
                l = "{0}".format(year)
            else:
                l = None

            if (iMethod):
                if (l):
                    l = "{0};{1}".format(l, iMethod)
                else:
                    l = "{0}".format(iMethod)

            if (sMethod):
                if (l):
                    l = "{0};{1}".format(l, sMethod)
                else:
                    l = "{0}".format(sMethod)

            if (aMethod):
                if (l):
                    l = "{0};{1}".format(l, aMethod)
                else:
                    l = "{0}".format(aMethod)

            if (bitLayers):
                l = "{0};{1}".format(l, bitLayers)

            for v1 in range(0, 4):
                for v2 in range(0, 4):
                    l = "{0};{1}".format(l, crossTab[v1][v2])

            csvFile.writelines("{0}\n".format(l))


def _spotCrossTable(targetMapset, s50MaskFN, actSpotFN, progSpotFN, printSeries=True, printTable=True, logFile=None):
    bboLib.debugMessage("bboPrognosisLib._spotCrosstab")

    spot1 = "tmp_bboplib_sct_spot1"
    spot2 = "tmp_bboplib_sct_spot2"
    spot3 = "tmp_bboplib_sct_spot3"
    s50Mask0 = "tmp_bboplib_sct_s50mask0"
    
    if (bboLib.validateRaster(s50MaskFN) is None):
        return

    if (bboLib.validateRaster(actSpotFN) is None):
        return

    if (bboLib.validateRaster(progSpotFN) is None):
        return
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=targetMapset)

    grass.mapcalc("$s50Mask0 = if(0 < $s50Mask, 0, -1)", overwrite=True, s50Mask=s50MaskFN, s50Mask0=s50Mask0)
    grass.run_command("r.null", map=s50Mask0, null=-1, quiet=True)

    grass.mapcalc("$spot3 = $actSpot", overwrite=True, spot3=spot3, actSpot=actSpotFN)
    grass.run_command("r.null", map=spot3, null=-1, quiet=True)
    grass.mapcalc("$spot1 = if(0 < $spot3, $spot3, $s50Mask0)", overwrite=True, spot1=spot1, spot3=spot3, s50Mask0=s50Mask0)
    grass.run_command("r.null", map=spot1, setnull=-1, quiet=True)

    grass.mapcalc("$spot3 = $progSpot", overwrite=True, spot3=spot3, progSpot=progSpotFN)
    grass.run_command("r.null", map=spot3, null=-1, quiet=True)
    grass.mapcalc("$spot2 = if(0 < $spot3, $spot3, $s50Mask0)", overwrite=True, spot2=spot2, spot3=spot3, s50Mask0=s50Mask0)
    grass.run_command("r.null", map=spot2, setnull=-1, quiet=True)

    m = []
    if (printSeries):
        bboLib.logMessage("{0} {1} {2}".format(actSpotFN, progSpotFN, "n"), logFile)

    for v1 in range(0, 4):
        l = []
        for v2 in range(0, 4):
            grass.mapcalc("$spot3 = if($spot1==$v1 && $spot2==$v2, 1, null())", overwrite=True, spot3=spot3, spot2=spot2, spot1=spot1, v1=v1, v2=v2)
            n = bboLib.getNotNullCellsNumber(spot3)
            if (printSeries):
                bboLib.logMessage("{0} {1} {2}".format(v1, v2, n), logFile)
            l.append(n)
        m.append(l)

    if (printTable):
        _printCrossTable(m, logFile)
       
    bboLib.deleteRaster(spot1)
    bboLib.deleteRaster(spot2)
    bboLib.deleteRaster(spot3)
    bboLib.deleteRaster(s50Mask0)
    
    # finish calculation, restore settings
    if (not (userMapset == targetMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
    
    return m


def _writeAUCHeader(csvFile, bYear, bInit, bSpread, bAttack, layers):
    bboLib.debugMessage("bboPrognosisLib._writeAUCHeader")

    if (csvFile):
        if (bYear):
            h = "year"
        else:
            h = None

        if (bInit):
            if (h):
                h = "{0};{1}".format(h, "iMethod")
            else:
                h = "iMethod"

        if (bSpread):
            if (h):
                h = "{0};{1}".format(h, "sMethod")
            else:
                h = "sMethod"

        if (bAttack):
            if (h):
                h = "{0};{1}".format(h, "aMethod")
            else:
                h = "aMethod"

        if (layers):
            i = 1
            for l in layers:
                h = "{0};L{1}".format(h, i)
                i = i + 1

        csvFile.writelines("{0};auc\n".format(h))


def _writeAUC(csvFile, auc, year, iMethod, sMethod, aMethod, bitLayers):
    bboLib.debugMessage("bboPrognosisLib._writeAUC")

    if (csvFile):
        if (year):
            l = "{0}".format(year)
        else:
            l = None

        if (iMethod):
            if (l):
                l = "{0};{1}".format(l, iMethod)
            else:
                l = "{0}".format(iMethod)

        if (sMethod):
            if (l):
                l = "{0};{1}".format(l, sMethod)
            else:
                l = "{0}".format(sMethod)

        if (aMethod):
            if (l):
                l = "{0};{1}".format(l, aMethod)
            else:
                l = "{0}".format(aMethod)

        if (bitLayers):
            l = "{0};{1}".format(l, bitLayers)

        csvFile.writelines("{0};{1}\n".format(l, auc))

#endregion SPOT_CROSSTABULATION



# #################### SAMPLES ####################
#region SAMPLES
def cleanSamplesSeries(yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib.cleanSpotSamplesSeries")

    bboLib.deleteYearSeries(bboLib.forestMapset, SAMPLES_TEMPLATE, yearFrom, yearTo, True)
    bboLib.deleteYearSeries(bboLib.forestMapset, RASTER_TRAINING_SAMPLES_TEMPLATE, yearFrom, yearTo, True)
    bboLib.deleteYearSeries(bboLib.forestMapset, RASTER_CONTROL_SAMPLES_TEMPLATE, yearFrom, yearTo, True)
    bboLib.deleteVectorYearSeries(bboLib.shpMapset, VECTOR_SAMPLES_TEMPLATE, yearFrom, yearTo, True)
    bboLib.deleteVectorYearSeries(bboLib.shpMapset, VECTOR_TRAINING_SAMPLES_TEMPLATE, yearFrom, yearTo, True)
    bboLib.deleteVectorYearSeries(bboLib.shpMapset, VECTOR_CONTROL_SAMPLES_TEMPLATE, yearFrom, yearTo, True)


def _samplesToVector(samplesTemplate, vectorTemplate, year):
    bboLib.debugMessage("bboPrognosisLib._samplesToVector")
    
    rasterFN = bboLib.replaceYearParameter(samplesTemplate, year, bboLib.forestMapset)
    vectorFN = bboLib.replaceYearParameter(vectorTemplate, year)
    bboLib.deleteVector(vectorFN)
    if (bboLib.validateRaster(rasterFN)):
        grass.message("samples to vector {0}".format(vectorFN))
        grass.run_command("r.to.vect", type="point", input=rasterFN, output=vectorFN, column="abundance", quiet=True, overwrite=True)       



def generateSamplesSeries(projectFN):
    bboLib.debugMessage("bboPrognosisLib.generateSpotSamplesSeries")

    project = _readProject(projectFN)
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
   
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=bboLib.forestMapset)
   
    # generate samples
    _generatePresenceSamples(project)
    _generateAbsenceSamples(project)
    _generateSamples(project)

    # convert raster HSM samples to vector representation
    grass.run_command("g.mapset", mapset=bboLib.shpMapset)
    year = yearFrom
    while (year <= yearTo):
        _samplesToVector(RASTER_TRAINING_SAMPLES_TEMPLATE, VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
        _samplesToVector(RASTER_CONTROL_SAMPLES_TEMPLATE, VECTOR_CONTROL_SAMPLES_TEMPLATE, year)
        _multiTrainingVectorSamples(project, year)
        year = year + 1    
    
    _addProbabilityColumns(VECTOR_TRAINING_SAMPLES_TEMPLATE, yearFrom, yearTo)
    _addProbabilityColumns(VECTOR_CONTROL_SAMPLES_TEMPLATE, yearFrom, yearTo)

    _addPrognosisColumns(VECTOR_TRAINING_SAMPLES_TEMPLATE, yearFrom, yearTo)
    _addPrognosisColumns(VECTOR_CONTROL_SAMPLES_TEMPLATE, yearFrom, yearTo)

    _addLayerFieldsToSamples(project)
    _addAuxiliaryColumnsToSamples(project)
    
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
        

def _generatePresenceSamples(project):    
    bboLib.debugMessage("bboPrognosisLib._generatePresenceSamples")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=bboLib.forestMapset)
    
    spots2MaskFN = "tmp_bboplib_gps1"
    spots3MaskFN = "tmp_bboplib_gps2"
    train3MaskFN = "tmp_bboplib_gps3"
    tmp1FN = "tmp_bboplib_gps4"

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    trainingSetPerc = project["samples"]["trainingSetPerc"]

    for year in range(yearFrom, yearTo + 1):
        spotsFN = bboLib.replaceYearParameter(bboLib.spotTemplate, year)
        if (bboLib.validateRaster(spotsFN)):
            samplesFN = bboLib.replaceYearParameter(SAMPLES_TEMPLATE, year)
            trainingFN = bboLib.replaceYearParameter(RASTER_TRAINING_SAMPLES_TEMPLATE, year)
            controlFN = bboLib.replaceYearParameter(RASTER_CONTROL_SAMPLES_TEMPLATE, year)
            bboLib.deleteRaster(samplesFN)
            bboLib.deleteRaster(trainingFN)
            bboLib.deleteRaster(controlFN)
            
            grass.mapcalc("$trainingSamples = null()", trainingSamples=trainingFN, overwrite=True)
            grass.mapcalc("$controlSamples = null()", controlSamples=controlFN, overwrite=True)

            grass.mapcalc("$spotsMask = if($spots == 2, 2, null())", spotsMask=spots2MaskFN, spots=spotsFN, overwrite=True)
            nSamples = bboLib.getCellsNumber(spots2MaskFN, 2)
            if (0 < nSamples):
                tSamples = int(nSamples * trainingSetPerc)
                if (0 < tSamples):
                    grass.message("presence samples code 2 year {0}: {1}/{2}".format(year, nSamples, tSamples))
                    grass.run_command("r.random", input=spots2MaskFN, cover=spotsFN, n=tSamples, raster=trainingFN, quiet=True, overwrite=True)
                    grass.mapcalc("$controlSamples = if(isnull($trainingSamples), $spots2Mask, null())", controlSamples=controlFN, spots2Mask=spots2MaskFN, trainingSamples=trainingFN, overwrite=True)

            grass.mapcalc("$spotsMask = if($spots == 3, 3, null())", spotsMask=spots3MaskFN, spots=spotsFN, overwrite=True)
            nSamples = bboLib.getCellsNumber(spots3MaskFN, 3)
            if (0 < nSamples):
                tSamples = int(nSamples * trainingSetPerc)
                if (0 < tSamples):
                    grass.message("presence samples code 3 year {0}: {1}/{2}".format(year, nSamples, tSamples))
                    grass.run_command("r.random", input=spots3MaskFN, cover=spotsFN, n=tSamples, raster=train3MaskFN, quiet=True, overwrite=True)
                    grass.mapcalc("$tmp = if(isnull($trainingSamples), $train3Mask, $trainingSamples)", tmp=tmp1FN, train3Mask=train3MaskFN, trainingSamples=trainingFN, overwrite=True)
                    grass.mapcalc("$trainingSamples = $tmp", tmp=tmp1FN, trainingSamples=trainingFN, overwrite=True)
                    grass.mapcalc("$tmp = if(isnull($controlSamples), if(isnull($training3Mask), $spots3Mask, null()), $controlSamples)", tmp=tmp1FN, training3Mask=train3MaskFN, controlSamples=controlFN, spots3Mask=spots3MaskFN, overwrite=True)                  
                    grass.mapcalc("$controlSamples = $tmp", tmp=tmp1FN, controlSamples=controlFN, overwrite=True)
    
    bboLib.deleteRaster(tmp1FN)
    bboLib.deleteRaster(train3MaskFN)
    bboLib.deleteRaster(spots3MaskFN)
    bboLib.deleteRaster(spots2MaskFN)

    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def _generateAbsenceSamples(project):    
    bboLib.debugMessage("bboPrognosisLib._generatePresenceSamples")

    samplesMaskFN = "tmp_gensamplesser_mask"

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=bboLib.forestMapset)
    
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    absenceMulti = project["samples"]["absenceMulti"]

    #create innitial samples mask
    _aggregateBBSpots(yearFrom, yearTo, samplesMaskFN)

    for year in range(yearFrom, yearTo + 1):
        s50MaskFN = bboLib.replaceYearParameter(bboLib.s50MaskTemplate, year)
        trainingFN = bboLib.replaceYearParameter(RASTER_TRAINING_SAMPLES_TEMPLATE, year)
        controlFN = bboLib.replaceYearParameter(RASTER_CONTROL_SAMPLES_TEMPLATE, year)
        if (bboLib.validateRaster(trainingFN)):
            grass.message("training absence samples {0}".format(year))
            _generateCodedAbsenceSamples(trainingFN, s50MaskFN, samplesMaskFN, absenceMulti, 2)
            _generateCodedAbsenceSamples(trainingFN, s50MaskFN, samplesMaskFN, absenceMulti, 3)
        if (bboLib.validateRaster(controlFN)):
            grass.message("control absence samples {0}".format(year))
            _generateCodedAbsenceSamples(controlFN, s50MaskFN, samplesMaskFN, 1, 2)
            _generateCodedAbsenceSamples(controlFN, s50MaskFN, samplesMaskFN, 1, 3)
            
    bboLib.deleteRaster(samplesMaskFN)
    
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def _generateCodedAbsenceSamples(samplesFN, s50MaskFN, samplesMaskFN, absenceMulti, spotCode):
    bboLib.debugMessage("bboPrognosisLib._generateCodedAbsenceSamples")
    
    tmp1FN = "tmp_bboplib_gcas100"
    actualCodedFN = "tmp_bboplib_gcas101"
    actualS50MaskFN = "tmp_bboplib_gcas102"
    absenceFN = "tmp_bboplib_gcas103"
    
    if (not bboLib.validateRaster(samplesFN)):
        bboLib.warningMessage("empty samples layer ({0})".format(samplesFN))
        return

    if (not bboLib.validateRaster(s50MaskFN)):
        bboLib.warningMessage("empty spruce forest mask layer ({0})".format(s50MaskFN))
        return

    grass.mapcalc("$actualCoded = if($spotCode == $samples, $spotCode, null())", actualCoded=actualCodedFN, samples=samplesFN, spotCode=spotCode, overwrite=True)
    grass.mapcalc("$actualS50Mask = if(isnull($s50Mask), null(), if(isnull($samplesMask), 1, null()))", actualS50Mask=actualS50MaskFN, s50Mask=s50MaskFN, samplesMask=samplesMaskFN, overwrite=True)

    # generate absence samples
    nPresence = bboLib.getCellsNumber(actualCodedFN)
    nMask = bboLib.getCellsNumber(actualS50MaskFN)
    if (nPresence == 0):
        bboLib.warningMessage("empty samples layer {0} code {1}".format(samplesFN, spotCode))
        return
    if (nMask == 0):
        bboLib.warningMessage("empty mask layer {0} code {1}".format(s50MaskFN, spotCode))
        return
    
    nAbsence = int(absenceMulti * nPresence)
    grass.message("absence samples for {0}: {1}/{2}".format(samplesFN, nPresence, nAbsence))
    if (0 < nAbsence):
        if (nMask <= nAbsence):
            grass.mapcalc("$absence = -$actualS50Mask * $spotCode", absence=absenceFN, actualS50Mask=actualS50MaskFN, spotCode=spotCode, overwrite=True)
        else:
            grass.run_command("r.random", input=actualS50MaskFN, cover=actualS50MaskFN, n=nAbsence, raster=tmp1FN, quiet=True, overwrite=True)
            grass.mapcalc("$absence = -$tmp1 * $spotCode", absence=absenceFN, tmp1=tmp1FN, spotCode=spotCode, overwrite=True)   
        grass.run_command("r.patch", input=samplesFN + ',' + absenceFN, output=tmp1FN, quiet=True, overwrite=True)
        grass.mapcalc("$samples = $tmp1", samples=samplesFN, tmp1=tmp1FN, overwrite=True)   
        #update samples mask
        grass.run_command("r.patch", input=samplesMaskFN + ',' + samplesFN, output=tmp1FN, quiet=True, overwrite=True)
        grass.mapcalc("$mask = $tmp1", mask=samplesMaskFN, tmp1=tmp1FN, overwrite=True)

    bboLib.deleteRaster(tmp1FN)
    bboLib.deleteRaster(actualCodedFN)
    bboLib.deleteRaster(actualS50MaskFN)
    bboLib.deleteRaster(absenceFN)

       
def _generateSamples(project):    
    bboLib.debugMessage("bboPrognosisLib._generateSamples")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=bboLib.forestMapset)
    
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    for year in range(yearFrom, yearTo + 1):
        grass.message("samples {0}".format(year))
        trainingFN = bboLib.replaceYearParameter(RASTER_TRAINING_SAMPLES_TEMPLATE, year)
        controlFN = bboLib.replaceYearParameter(RASTER_CONTROL_SAMPLES_TEMPLATE, year)
        samplesFN = bboLib.replaceYearParameter(SAMPLES_TEMPLATE, year)
        if (bboLib.validateRaster(trainingFN) and bboLib.validateRaster(controlFN)):
            grass.run_command("r.patch", input=trainingFN + ',' + controlFN, output=samplesFN, quiet=True, overwrite=True)



def _multiTrainingVectorSamples(project, year):    
    bboLib.debugMessage("bboPrognosisLib._multiTrainingVectorSamples")

    rasterPresenceFN = "tmp_gentvsamples_ras1"
    vectorPresenceFN = "tmp_gentvsamples_vec1"
    vectorTmpFN = "tmp_gentvsamples_tmp1"
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=bboLib.forestMapset)
    
    presenceMulti = project["samples"]["presenceMulti"]

    rasterTrainingFN = bboLib.replaceYearParameter(RASTER_TRAINING_SAMPLES_TEMPLATE, year)
    if (bboLib.validateRaster(rasterTrainingFN) and 1 < presenceMulti):
        grass.message("multi training presence samples {0}".format(rasterTrainingFN))
        grass.mapcalc("$presence = if(0 < $samples, $samples, null())", presence=rasterPresenceFN, samples=rasterTrainingFN, overwrite=True)
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)
        vectorTrainingFN = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
        grass.run_command("r.to.vect", type="point", input=rasterPresenceFN+"@"+bboLib.forestMapset, output=vectorPresenceFN, column="abundance", quiet=True, overwrite=True)
        layersList = "{0}".format(vectorTrainingFN)
        for i in range(1, presenceMulti):
            layersList = "{0},{1}".format(layersList, vectorPresenceFN)
        grass.run_command("v.patch", input=layersList, output=vectorTmpFN, flags="neb", quiet=True, overwrite=True)
        bboLib.deleteVector(vectorTrainingFN)
        grass.run_command("g.rename", vector="{0},{1}".format(vectorTmpFN, vectorTrainingFN), quiet=True, overwrite=True)
        bboLib.deleteVector(vectorTmpFN)
        bboLib.deleteVector(vectorPresenceFN)
        grass.run_command("g.mapset", mapset=bboLib.forestMapset)       
        
    bboLib.deleteRaster(rasterPresenceFN)
    
    if (not (userMapset == bboLib.forestMapset)):
        grass.run_command("g.mapset", mapset=userMapset)



def _addProbabilityColumns(vectorTemplate, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._addProbabilityColumns")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)
    
    tmp = "tmp_bboplib_apc_n0"
    grass.mapcalc("$tmp = 0.0", tmp=tmp, overwrite=True)

    year = yearFrom
    while (year <= yearTo):
        samplesLayer = bboLib.replaceYearParameter(vectorTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("probability columns {0}".format(samplesLayer))
            # add probability columns
            grass.run_command("v.what.rast", map=samplesLayer, raster=tmp, column=SAMPLES_PINIT_COLUMN_NAME, quiet=True, overwrite=True)
            grass.run_command("v.what.rast", map=samplesLayer, raster=tmp, column=SAMPLES_PSPREAD_COLUMN_NAME, quiet=True, overwrite=True)
            grass.run_command("v.what.rast", map=samplesLayer, raster=tmp, column=SAMPLES_PATTACK_COLUMN_NAME, quiet=True, overwrite=True)
        year = year + 1

    bboLib.deleteRaster(tmp)  

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def _addPrognosisColumns(vectorTemplate, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._addPrognosisColumns")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)
    
    year = yearFrom
    while (year <= yearTo):
        samplesLayer = bboLib.replaceYearParameter(vectorTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("prognosis columns {0}".format(samplesLayer))
            grass.run_command("v.db.addcolumn", map=samplesLayer, columns="{0} integer".format(SAMPLES_HSM_COLUMN_NAME), quiet=True, overwrite=True)
            grass.run_command("v.db.addcolumn", map=samplesLayer, columns="{0} integer".format(SAMPLES_PROG_COLUMN_NAME), quiet=True, overwrite=True)
            grass.run_command("v.db.update", map=samplesLayer, layer=1, column=SAMPLES_HSM_COLUMN_NAME, value=PROGNOSISNULLVALUE, quiet=True, overwrite=True)
            grass.run_command("v.db.update", map=samplesLayer, layer=1, column=SAMPLES_PROG_COLUMN_NAME, value=PROGNOSISNULLVALUE, quiet=True, overwrite=True)
        year = year + 1

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def _assignProbabilitiesToSamples(project):
    bboLib.debugMessage("bboPrognosisLib._assignProbabilitiesToSamples")
    _assignInitProbabilities(project)
    _assignSpreadProbabilities(project)
    _assignAttackProbabilities(project)


def _assignInitProbabilities(project):
    bboLib.debugMessage("bboPrognosisLib._assignInitProbabilities")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
  
    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign init probabilities {0}".format(year))
            _assignValuesToDField(year, VECTOR_TRAINING_SAMPLES_TEMPLATE, project["initModel"]["outputFN"], project["targetMapset"], SAMPLES_PINIT_COLUMN_NAME)
            _assignValuesToDField(year, VECTOR_CONTROL_SAMPLES_TEMPLATE, project["initModel"]["outputFN"], project["targetMapset"], SAMPLES_PINIT_COLUMN_NAME)


def _assignSpreadProbabilities(project):
    bboLib.debugMessage("bboPrognosisLib._assignSpreadProbabilities")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
  
    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign spread probabilities {0}".format(year))
            _assignValuesToDField(year, VECTOR_TRAINING_SAMPLES_TEMPLATE, project["spreadModel"]["outputFN"], project["targetMapset"], SAMPLES_PSPREAD_COLUMN_NAME)
            _assignValuesToDField(year, VECTOR_CONTROL_SAMPLES_TEMPLATE, project["spreadModel"]["outputFN"], project["targetMapset"], SAMPLES_PSPREAD_COLUMN_NAME)


def _assignAttackProbabilities(project):
    bboLib.debugMessage("bboPrognosisLib._assignAttackProbabilities")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
  
    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign attack probabilities {0}".format(year))
            _assignValuesToDField(year, VECTOR_TRAINING_SAMPLES_TEMPLATE, project["attackModel"]["outputFN"], project["targetMapset"], SAMPLES_PATTACK_COLUMN_NAME)
            _assignValuesToDField(year, VECTOR_CONTROL_SAMPLES_TEMPLATE, project["attackModel"]["outputFN"], project["targetMapset"], SAMPLES_PATTACK_COLUMN_NAME)



def _assignAttackProbabilitiesToSamples(project, vectorSamplesTemplate, msg):
    bboLib.debugMessage("bboPrognosisLib._assignAttackProbabilitiesToSamples")
    
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(vectorSamplesTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign attack probabilities to {0} {1}".format(msg, year))
            _assignValuesToDField(year, vectorSamplesTemplate, project["attackModel"]["outputFN"], project["targetMapset"], SAMPLES_PATTACK_COLUMN_NAME)


def _assignInitProbabilitiesToSamples(project, vectorSamplesTemplate, msg):
    bboLib.debugMessage("bboPrognosisLib._assignInitProbabilitiesToSamples")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
  
    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(vectorSamplesTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign init probabilities to {0} {1}".format(msg, year))
            _assignValuesToDField(year, vectorSamplesTemplate, project["initModel"]["outputFN"], project["targetMapset"], SAMPLES_PINIT_COLUMN_NAME)


def _assignSpreadProbabilitiesToSamples(project, vectorSamplesTemplate, msg):
    bboLib.debugMessage("bboPrognosisLib._assignSpreadProbabilitiesToSamples")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
  
    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(vectorSamplesTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign spread probabilities to {0} {1}".format(msg, year))
            _assignValuesToDField(year, vectorSamplesTemplate, project["spreadModel"]["outputFN"], project["targetMapset"], SAMPLES_PSPREAD_COLUMN_NAME)


def _assignPrognosisToSamples(project, vectorSamplesTemplate, msg):
    bboLib.debugMessage("bboPrognosisLib._assignPrognosisToSamples")
    
    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    for year in range(yearFrom, yearTo + 1):
        samplesLayer = bboLib.replaceYearParameter(vectorSamplesTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("Assign prognosis to {0} {1}".format(msg, year))
            _assignValuesToDField(year, vectorSamplesTemplate, project["attackModel"]["hsmFN"], project["targetMapset"], SAMPLES_HSM_COLUMN_NAME)
            _assignValuesToDField(year, vectorSamplesTemplate, project["spotPrognosis"]["spotFN"], project["targetMapset"], SAMPLES_PROG_COLUMN_NAME)


def _addFieldsToSamples(samplesTemplate, fieldsList, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib._addFieldsToSamples")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)
      
    tmp = "tmp_bboplib_alfs_n0"
    grass.mapcalc("$tmp = $nval", tmp=tmp, nval=ATTRIBUTENULLVALUE, overwrite=True)

    year = yearFrom
    while (year <= yearTo):
        samplesLayer = bboLib.replaceYearParameter(samplesTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("layer columns to {0}".format(samplesLayer))
            for fname in fieldsList:
                grass.run_command("v.what.rast", map=samplesLayer, raster=tmp, column=fname, quiet=True, overwrite=True)
        year = year + 1

    bboLib.deleteRaster(tmp)  

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)


def _addLayerFieldsToSamples(project):
    bboLib.debugMessage("bboPrognosisLib._addModelLayerFields")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    fieldsList = project["samples"]["fields"]
    layersList = project["samples"]["layers"]
    
    if (fieldsList and layersList and yearFrom <= yearTo):
        if (len(fieldsList) == len(layersList)):
            _addFieldsToSamples(VECTOR_TRAINING_SAMPLES_TEMPLATE, fieldsList, yearFrom, yearTo)
            _addFieldsToSamples(VECTOR_CONTROL_SAMPLES_TEMPLATE, fieldsList, yearFrom, yearTo)


def _assignValuesToSamples(project):
    bboLib.debugMessage("bboPrognosisLib._assignValuesToSamples")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)

    if (project["samples"]["fields"] and project["samples"]["layers"]):
        fieldNames = project["samples"]["fields"]
        layerTemplates = project["samples"]["layers"]
        nFields = len(fieldNames)
        year = yearFrom
        while (year <= yearTo):
            samplesLayer = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
            if (bboLib.validateVector(samplesLayer)):
                grass.message("Assign values year {0}".format(year))
                iField = 0
                while (iField < nFields):
                    _assignValuesToDField(year, VECTOR_TRAINING_SAMPLES_TEMPLATE, layerTemplates[iField], None, fieldNames[iField])
                    _assignValuesToDField(year, VECTOR_CONTROL_SAMPLES_TEMPLATE, layerTemplates[iField], None, fieldNames[iField])
                    iField = iField + 1
            year = year + 1

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)



def _addAuxiliaryColumnsToSamples(project):
    bboLib.debugMessage("bboPrognosisLib._addAuxiliaryColumnsToSamples")

    yearFrom = project["yearFrom"]
    yearTo = project["yearTo"]
    
    if (yearFrom <= yearTo):
        _addAuxiliaryColumns(VECTOR_TRAINING_SAMPLES_TEMPLATE, yearFrom, yearTo, 1)
        _addAuxiliaryColumns(VECTOR_CONTROL_SAMPLES_TEMPLATE, yearFrom, yearTo, 0)


def _addAuxiliaryColumns(vectorTemplate, yearFrom, yearTo, trainingValue=-9):
    bboLib.debugMessage("bboPrognosisLib._addAuxiliaryColumns")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)
    
    year = yearFrom
    while (year <= yearTo):
        samplesLayer = bboLib.replaceYearParameter(vectorTemplate, year)
        if (bboLib.validateVector(samplesLayer)):
            grass.message("auxiliary columns to {0}".format(samplesLayer))
            grass.run_command("v.db.addcolumn", map=samplesLayer, columns="{0} integer".format(SAMPLES_YEAR_COLUMN_NAME), quiet=True, overwrite=True)
            grass.run_command("v.db.update", map=samplesLayer, layer=1, column=SAMPLES_YEAR_COLUMN_NAME, value=year, quiet=True, overwrite=True)
            grass.run_command("v.db.addcolumn", map=samplesLayer, columns="{0} integer".format(SAMPLES_TRAINING_COLUMN_NAME), quiet=True, overwrite=True)
            grass.run_command("v.db.update", map=samplesLayer, layer=1, column=SAMPLES_TRAINING_COLUMN_NAME, value=trainingValue, quiet=True, overwrite=True)
            grass.run_command("v.db.addcolumn", map=samplesLayer, columns="{0} integer".format(SAMPLES_PRESENCE_COLUMN_NAME), quiet=True, overwrite=True)
            grass.run_command("v.db.update", map=samplesLayer, layer=1, column=SAMPLES_PRESENCE_COLUMN_NAME, value=0, quiet=True, overwrite=True)
            grass.run_command("v.db.update", map=samplesLayer, layer=1, column=SAMPLES_PRESENCE_COLUMN_NAME, value=1, where="0 < abundance", quiet=True, overwrite=True)
        year = year + 1

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
        


def _assignValuesToDField(year, vectorTemplate, rasterTemplate, rasterMapset, columnName, defaultValue=None):
    bboLib.debugMessage("bboPrognosisLib._assignValuesToDField")
    
    tmp1 = "tmp_assignvalues_tmp1"
    if (defaultValue is None):
        defaultValue = ATTRIBUTENULLVALUE
        
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)

    vectorFN = bboLib.replaceYearParameter(vectorTemplate, year)
    rasterFN = bboLib.replaceYearParameter(rasterTemplate, year, rasterMapset)
    if (bboLib.validateVector(vectorFN)):
        bboLib.debugMessage("assign {0} to {1} ".format(rasterFN, vectorFN))
        grass.run_command("v.db.update", map=vectorFN, layer=1, column=columnName, value=defaultValue, quiet=True, overwrite=True)
        if (bboLib.validateRaster(rasterFN)):
            grass.mapcalc("$tmp = $val", tmp=tmp1, val=rasterFN, overwrite=True)
            grass.run_command("r.null", map=tmp1, null=0, quiet=True)
            grass.run_command("v.what.rast", map=vectorFN, raster=tmp1, column=columnName, quiet=True, overwrite=True)

    bboLib.deleteRaster(tmp1)
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)



def exportSamplesSeries(projectFN):
    bboLib.debugMessage("bboPrognosisLib.exportSamplesSeries")

    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)

    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]

    tmp = "tmp_bbolib_ess_patch"
    
    project = _readProject(projectFN)
    bboLib.setDebug(project)

    yearFrom = int(project["yearFrom"])
    yearTo = int(project["yearTo"])

    _assignProbabilitiesToSamples(project)
    _assignValuesToSamples(project)

    columnList = "cat,abundance,pinit,pspread,pattack,hsm,prog"
    if (project["samples"]["fields"]):
        for f in project["samples"]["fields"]:
            columnList = columnList + "," + f
    columnList = columnList + ",year,train,presence"

    #year = yearFrom
    #while (year <= yearTo):
        #spotSamples = bboLib.replaceYearParameter(RASTER_TRAINING_SAMPLES_TEMPLATE, year, bboLib.forestMapset)
        #if (bboLib.validateRaster(spotSamples)):
            #grass.message("Export samples {0}".format(year))
            #_exportSamples(columnList, VECTOR_TRAINING_SAMPLES_TEMPLATE, ASCII_TRAINING_SAMPLES_TEMPLATE, CSV_TRAINING_SAMPLES_TEMPLATE, year)
            #_exportSamples(columnList, VECTOR_CONTROL_SAMPLES_TEMPLATE, ASCII_CONTROL_SAMPLES_TEMPLATE, CSV_CONTROL_SAMPLES_TEMPLATE, year)
        #year = year + 1

    # export control samples
    year = yearFrom
    layersList = ""
    while (year <= yearTo):
        controlFN = bboLib.replaceYearParameter(VECTOR_CONTROL_SAMPLES_TEMPLATE, year)
        if (len(layersList) < 1):
            layersList = "{0}".format(controlFN)
        else:
            layersList = "{0},{1}".format(layersList, controlFN)
        year = year + 1
    grass.run_command("v.patch", input=layersList, output=tmp, flags="neb", quiet=True, overwrite=True)
    controlCSVFN = os.path.join(dbName, locName, "_data\\samples", CSV_CONTROL_SAMPLES_FILENAME)
    bboLib.deleteFile(controlCSVFN)
    grass.run_command("v.db.select", map=tmp, file=controlCSVFN, columns=columnList, separator=";", quiet=True, overwrite=True) 
    bboLib.deleteVector(tmp)

    # export training samples
    year = yearFrom
    layersList = ""
    while (year <= yearTo):
        controlFN = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year)
        if (len(layersList) < 1):
            layersList = "{0}".format(controlFN)
        else:
            layersList = "{0},{1}".format(layersList, controlFN)
        year = year + 1
    grass.run_command("v.patch", input=layersList, output=tmp, flags="neb", quiet=True, overwrite=True)
    trainingCSVFN = os.path.join(dbName, locName, "_data\\samples", CSV_TRAINING_SAMPLES_FILENAME)
    bboLib.deleteFile(trainingCSVFN)
    grass.run_command("v.db.select", map=tmp, file=trainingCSVFN, columns=columnList, separator=";", quiet=True, overwrite=True) 
       
    bboLib.deleteVector(tmp)
    
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)
       

def _exportSamples(columnList, vectorSamplesTemplate, asciiSamplesTemplate, csvSamplesTemplate, year):
    bboLib.debugMessage("bboPrognosisLib._exportSamples")

    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]

    samplesLayer = bboLib.replaceYearParameter(vectorSamplesTemplate, year)
    if (bboLib.validateVector(samplesLayer)):
        #ascFN = bboLib.replaceYearParameter(asciiSamplesTemplate, year)
        #outFN = os.path.join(dbName, locName, "_data\\samples", ascFN)
        #grass.run_command("v.out.ascii", input=samplesLayer, output=outFN, flags="c", column=columnList, format="point", separator=";", quiet=True, overwrite=True)
        csvFN = bboLib.replaceYearParameter(csvSamplesTemplate, year)
        outFN = os.path.join(dbName, locName, "_data\\samples", csvFN)
        grass.run_command("v.db.select", map=samplesLayer, file=outFN, columns=columnList, separator=";", quiet=True, overwrite=True) 


def _getTrainingSamples(year, spotCode, outputTemplate, trainingYears=1):
    bboLib.debugMessage("bboPrognosisLib._getTrainingSamples")
    # TODO spotCode is not considered
    
    outputFN = bboLib.replaceYearParameter(outputTemplate, year)

    layersList = ""
    nLayers = 0
    while (0 < trainingYears):
        samplesFN = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year, bboLib.shpMapset)
        if (bboLib.validateVector(samplesFN)):
            samplesFN = bboLib.replaceYearParameter(VECTOR_TRAINING_SAMPLES_TEMPLATE, year, bboLib.shpMapset)
            nLayers = nLayers + 1
            if (nLayers == 1):
                layersList = "{0}".format(samplesFN)
            else:
                layersList = "{0},{1}".format(layersList, samplesFN)
        year = year - 1
        trainingYears = trainingYears - 1

    bboLib.deleteVector(outputFN)
    if (1 < nLayers):
        grass.run_command("v.patch", input=layersList, output=outputFN, flags="neb", quiet=True, overwrite=True)
    if (1 == nLayers):
        grass.run_command("g.copy", vector="{0},{1}".format(layersList, outputFN), quiet=True, overwrite=True)
        
    return (0 < nLayers)


def _calcControlSamplesStatistics(yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib.controlSamplesStatistics")

    samplesStat = {}
    grass.message("ATTACK NEW SAMPLES")
    allStat = _controlSamplesAUC(yearFrom, yearTo, NEW_SPOTCODE, SAMPLES_PATTACK_COLUMN_NAME)
    grass.message(allStat)
    samplesStat["new_pattack"] = allStat
    grass.message("\n\n")

    grass.message("ATTACK SPREAD SAMPLES")
    spreadStat = _controlSamplesAUC(yearFrom, yearTo, SPREAD_SPOTCODE, SAMPLES_PATTACK_COLUMN_NAME)
    grass.message(spreadStat)
    samplesStat["spread_pattack"] = spreadStat
    grass.message("\n\n")

    grass.message("ATTACK INIT SAMPLES")
    initStat = _controlSamplesAUC(yearFrom, yearTo, INIT_SPOTCODE, SAMPLES_PATTACK_COLUMN_NAME)
    grass.message(initStat)
    samplesStat["init_pattack"] = initStat
    grass.message("\n\n")

    grass.message("SPREAD SAMPLES")
    spreadStat = _controlSamplesAUC(yearFrom, yearTo, SPREAD_SPOTCODE, SAMPLES_PSPREAD_COLUMN_NAME)
    grass.message(spreadStat)
    samplesStat["spread_pspread"] = spreadStat
    grass.message("\n\n")

    grass.message("INIT SAMPLES")
    initStat = _controlSamplesAUC(yearFrom, yearTo, INIT_SPOTCODE, SAMPLES_PINIT_COLUMN_NAME)
    grass.message(initStat)
    samplesStat["init_pinit"] = initStat
    grass.message("\n\n")

    return samplesStat


def _readSamples(rowList):
    bboLib.debugMessage("bboPrognosisLib._readSamples")

    abundanceCol = -1
    pinitCol = -1
    pspreadCol = -1
    pattackCol = -1
    hsmCol = -1
    progCol = -1

    nCols = len(rowList["columns"])
    for iCol in range(0, nCols):
        colName = rowList["columns"][iCol]
        if (colName == SAMPLES_ABUNDANCE_COLUMN_NAME):
            abundanceCol = iCol
        if (colName == SAMPLES_PINIT_COLUMN_NAME):
            pinitCol = iCol
        if (colName == SAMPLES_PSPREAD_COLUMN_NAME):
            pspreadCol = iCol
        if (colName == SAMPLES_PATTACK_COLUMN_NAME):
            pattackCol = iCol
        if (colName == SAMPLES_HSM_COLUMN_NAME):
            hsmCol = iCol
        if (colName == SAMPLES_PROG_COLUMN_NAME):
            progCol = iCol

    if (abundanceCol < 0):
        grass.fatal("missing column {0}".format(SAMPLES_ABUNDANCE_COLUMN_NAME))

    if (pattackCol < 0):
        bboLib.warningMessage("missing column {0}".format(SAMPLES_PATTACK_COLUMN_NAME))

    if (pspreadCol < 0):
        bboLib.warningMessage("missing column {0}".format(SAMPLES_PSPREAD_COLUMN_NAME))

    if (pinitCol < 0):
        bboLib.warningMessage("missing column {0}".format(SAMPLES_PINIT_COLUMN_NAME))

    if (hsmCol < 0):
        bboLib.warningMessage("missing column {0}".format(SAMPLES_HSM_COLUMN_NAME))

    if (progCol < 0):
        bboLib.warningMessage("missing column {0}".format(SAMPLES_PROG_COLUMN_NAME))
    
    samplesList = []
    for iRow in rowList["values"]:
        r = rowList["values"][iRow]
        s = {}
        try:
            s[SAMPLES_ABUNDANCE_COLUMN_NAME] = int(r[abundanceCol])
            if (0 <= pinitCol):
                s[SAMPLES_PINIT_COLUMN_NAME] = float(r[pinitCol])
            else:
                s[SAMPLES_PINIT_COLUMN_NAME] = None
            if (0 <= pspreadCol):
                s[SAMPLES_PSPREAD_COLUMN_NAME] = float(r[pspreadCol])
            else:
                s[SAMPLES_PSPREAD_COLUMN_NAME] = None
            if (0 <= pattackCol):
                s[SAMPLES_PATTACK_COLUMN_NAME] = float(r[pattackCol])
            else:
                s[SAMPLES_PATTACK_COLUMN_NAME] = None
            if (0 <= hsmCol):
                s[SAMPLES_HSM_COLUMN_NAME] = int(r[hsmCol])
            else:
                s[SAMPLES_HSM_COLUMN_NAME] = None
        except ValueError:
            bboLib.errorMessage("Exception ValueError")
            continue

        try:
            if (0 <= progCol):
                s[SAMPLES_PROG_COLUMN_NAME] = int(r[progCol])
            else:
                s[SAMPLES_PROG_COLUMN_NAME] = 0     
        except ValueError:
            s[SAMPLES_PROG_COLUMN_NAME] = 0     

        samplesList.append(s)
        
    return samplesList


def _samplesColumnStatistics(samplesList, columnName, year):
    bboLib.debugMessage("bboPrognosisLib._samplesColumnStatistics")

    minVal = 1.0
    maxVal = 0.0
    sumVal = 0.0
    sumVal2 = 0.0
    nSamples = 0
    for s in samplesList:
        if (s[SAMPLES_ABUNDANCE_COLUMN_NAME] < 0):
            val = s[columnName]
            sumVal = sumVal + val
            sumVal2 = sumVal2 + val*val
            nSamples = nSamples + 1
            if (val < minVal):
                minVal = val
            if (maxVal < val):
                maxVal = val
    if (0 < nSamples):
        avgVal = sumVal / nSamples
        stdVal = math.sqrt(sumVal2 / nSamples - avgVal*avgVal)
    else:
        avgVal = None
        stdVal = None
        minVal = None
        maxVal = None

    columnStats = {"nospot": {"min": minVal, "max": maxVal, "avg": avgVal, "std": stdVal, "n": nSamples}}

    minVal = 1.0
    maxVal = 0.0
    sumVal = 0.0
    sumVal2 = 0.0
    nSamples = 0
    for s in samplesList:
        if (s[SAMPLES_ABUNDANCE_COLUMN_NAME] > 0):
            val = s[columnName]
            sumVal = sumVal + val
            sumVal2 = sumVal2 + val*val
            nSamples = nSamples + 1
            if (val < minVal):
                minVal = val
            if (maxVal < val):
                maxVal = val
    if (0 < nSamples):
        avgVal = sumVal / nSamples
        d = sumVal2 / nSamples - avgVal*avgVal
        if (0 < d):
            stdVal = math.sqrt(d)
        else:
            stdVal = 0.0
    else:
        avgVal = None
        stdVal = None
        minVal = None
        maxVal = None

    columnStats["spot"] = {"min": minVal, "max": maxVal, "avg": avgVal, "std": stdVal, "n": nSamples}

    rocSteps = 20
    roc = [(0.0, 0.0)]
    alphaStep = 1.0 / rocSteps
    alpha = 1.0 - alphaStep
    while (0.0 < alpha):
        fp = 0.0
        tp = 0.0
        fn = 0.0
        tn = 0.0
        for s in samplesList:
            val = s[columnName]
            if (0 < s[SAMPLES_ABUNDANCE_COLUMN_NAME]):
                if (alpha < val):
                    tp = tp + 1.0
                else:
                    fn = fn + 1.0
            else:
                if (alpha < val):
                    fp = fp + 1.0
                else:
                    tn = tn + 1.0
        if (0 < (tp + fn) and 0 < (fp + tn)):
            tpr = tp / (tp + fn)
            fpr = fp / (fp + tn)
            roc.append((fpr, tpr))
        alpha = alpha - alphaStep
    roc.append((1.0, 1.0))

    auc = 0.0
    n = len(roc)
    for i in range(1, n):
        a = (roc[i][0] - roc[i - 1][0]) * (roc[i][1] + roc[i - 1][1]) / 2.0
        auc = auc + a

    columnStats["auc"] = auc
    columnStats["year"] = year
    columnStats["n"] = len(samplesList)

    hsmTP = 0
    hsmTN = 0
    hsmFN = 0
    hsmFP = 0
    i = 0
    for s in samplesList:
        i = i + 1
        if (0 < s[SAMPLES_ABUNDANCE_COLUMN_NAME]):
            if (1 == s[SAMPLES_HSM_COLUMN_NAME]):
                hsmTP = hsmTP + 1
            else:
                hsmFN = hsmFN + 1
        else:
            if (0 == s[SAMPLES_HSM_COLUMN_NAME]):
                hsmTN = hsmTN + 1
            else:
                hsmFP = hsmFP + 1

    columnStats["hsmTP"] = hsmTP
    columnStats["hsmTN"] = hsmTN
    columnStats["hsmFN"] = hsmFN
    columnStats["hsmFP"] = hsmFP

    progTP = 0
    progFP = 0
    progTN = 0
    progFN = 0
    i = 0
    for s in samplesList:
        i = i + 1
        if (0 < s[SAMPLES_ABUNDANCE_COLUMN_NAME]):
            if (1 == s[SAMPLES_PROG_COLUMN_NAME]):
                progTP = progTP + 1
            else:
                progFN = progFN + 1
        else:
            if (0 == s[SAMPLES_PROG_COLUMN_NAME]):
                progTN = progTN + 1
            else:
                progFP = progFP + 1

    columnStats["progTP"] = progTP
    columnStats["progTN"] = progTN
    columnStats["progFN"] = progFN
    columnStats["progFP"] = progFP

    return columnStats


def _samplesAUC(yearFrom, yearTo, spotCode, samplesTemplate, columnName):
    bboLib.debugMessage("bboPrognosisLib._samplesAUC")
    
    userMapset = grass.gisenv()["MAPSET"]  
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)

    samplesAUC = []
    year = yearFrom
    while (year <= yearTo):
        vectorFN = bboLib.replaceYearParameter(samplesTemplate, year, bboLib.shpMapset)
        if (bboLib.validateVector(vectorFN)):
            grass.message("samples AUC for year {0}, column {1}".format(year, columnName))
            if (spotCode == NEW_SPOTCODE):
                rowList = grass.vector_db_select(map=vectorFN)
            else:
                sqlWhere = "abundance={0} or abundance=-{0}".format(spotCode)
                rowList = grass.vector_db_select(map=vectorFN, where=sqlWhere)
            samplesList = _readSamples(rowList)
            cs = _samplesColumnStatistics(samplesList, columnName, year)
            samplesAUC.append(cs["auc"])
        year = year + 1

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return samplesAUC


def _controlSamplesAUC(yearFrom, yearTo, spotCode, columnName):
    bboLib.debugMessage("bboPrognosisLib._controlSamplesAUC")
    return _samplesAUC(yearFrom, yearTo, spotCode, VECTOR_CONTROL_SAMPLES_TEMPLATE, columnName)


def _trainingSamplesAUC(yearFrom, yearTo, spotCode, columnName):
    bboLib.debugMessage("bboPrognosisLib._trainingSamplesAUC")
    return _samplesAUC(yearFrom, yearTo, spotCode, VECTOR_TRAINING_SAMPLES_TEMPLATE, columnName)


def _samplesStatistics(yearFrom, yearTo, spotCode, samplesTemplate, columnName, logFile=None):
    bboLib.debugMessage("bboPrognosisLib._controlSamplesStatistics")
    
    userMapset = grass.gisenv()["MAPSET"]
    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=bboLib.shpMapset)

    samplesStatistics = []
    year = yearFrom
    while (year <= yearTo):
        vectorFN = bboLib.replaceYearParameter(samplesTemplate, year, bboLib.shpMapset)
        if (bboLib.validateVector(vectorFN)):
            if (spotCode == NEW_SPOTCODE):
                bboLib.logMessage("new spotcode> {0}".format(vectorFN))
                rowList = grass.vector_db_select(map=vectorFN)
            else:
                sqlWhere = "abundance={0} or abundance=-{0}".format(spotCode)
                bboLib.logMessage("abundance> {0} {1}".format(vectorFN, sqlWhere))
                rowList = grass.vector_db_select(map=vectorFN, where=sqlWhere)
            samplesList = _readSamples(rowList)
            cs = _samplesColumnStatistics(samplesList, columnName, year)
            samplesStatistics.append(cs)
        year = year + 1

    if (not (userMapset == bboLib.shpMapset)):
        grass.run_command("g.mapset", mapset=userMapset)

    return samplesStatistics


def _controlSamplesStatistics(yearFrom, yearTo, spotCode, columnName, logFile=None):
    bboLib.debugMessage("bboPrognosisLib._controlSamplesStatistics")
    return _samplesStatistics(yearFrom, yearTo, spotCode, VECTOR_CONTROL_SAMPLES_TEMPLATE, columnName, logFile=None)


def _trainingSamplesStatistics(yearFrom, yearTo, spotCode, columnName, logFile=None):
    bboLib.debugMessage("bboPrognosisLib._trainingSamplesStatistics")
    return _samplesStatistics(yearFrom, yearTo, spotCode, VECTOR_TRAINING_SAMPLES_TEMPLATE, columnName, logFile=None)

#endregion SAMPLES



# #################### INTERFACE TO R ####################
#region INTERFACE_TO_R

def exportRasterToTxt(rastersList, outputFN):
    bboLib.debugMessage("bboPrognosisLib.exportRasterToTxt output={0}".format(outputFN))
    rastersLst = None
    for r in rastersList:
        if rastersLst is None:
            rastersLst = r
        else:
            rastersLst = rastersLst + "," + r
    grass.run_command("r.out.xyz", input=rastersLst, output=outputFN, separator=";", overwrite=True)

def exportRasterSeriesToTxt(templatesList, outputFN, yearFrom, yearTo):
    bboLib.debugMessage("bboPrognosisLib.exportRasterSeriesTxt output={0}".format(outputFN))
    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    expFN = os.path.join(dbName, locName, "_data\\export", "tmp_proglib_exp.txt")
    outFile = open(outputFN, 'w')
    for y in range(yearFrom, yearTo + 1):
        rastersStringLst = bboLib.replaceYearParameter(templatesList, y)
        if bboLib.validateRastersStringList(rastersStringLst):
            exportRasterSeriesToTxt(rastersStringLst, expFN)
            expFile = open(expFN, 'r')
            for line in expFile:
                outFile.write(line)
            expFile.close()
    outFile.close()
    os.remove(expFN)

def exportInitRasters(maskName, params, outputFN, yearFrom, yearTo):
    templatesList = _getInitTemplatesAsString(maskName, params)
    exportRasterSeriesToTxt(templatesList, outputFN, yearFrom, yearTo)

def exportSpreadRasters(maskName, params, outputFN, yearFrom, yearTo):
    templatesList = _getSpreadTemplatesAsString(maskName, params)
    exportRasterSeriesToTxt(templatesList, outputFN, yearFrom, yearTo)

#endregion INTERFACE_TO_R



# #################### EXPORT TO AAI ####################
#region EXPORT_TO_AAI
def exportPrognosisLayersToAAI(sourceMapset, outputPrefix, outTemplate, yearFrom, yearTo):
    dbName = grass.gisenv()["GISDBASE"]
    locName = grass.gisenv()["LOCATION_NAME"]
    targetDir = os.path.join(dbName, locName, "_data\\prognoses")
    sourceTemplate = outputPrefix + outTemplate
    bboLib.exportRasterYearToAAI(sourceMapset, sourceTemplate, yearFrom, yearTo, targetDir)


def exportPrognosisToAAI(paramFN, yearFrom, yearTo):
    params = _readProject(paramFN)
    sourceMapset = params["targetMapset"]
    outputPrefix = params["outputPrefix"]

    #init
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, INIT_PROBABILITY_TEMPLATE, yearFrom, yearTo)
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, INIT_POTENTIAL_TEMPLATE, yearFrom, yearTo)
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, INIT_RESISTANCE_TEMPLATE, yearFrom, yearTo)
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, INIT_COSTDST_TEMPLATE, yearFrom, yearTo)

    #spread
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, SPREAD_PROBABILITY_TEMPLATE, yearFrom, yearTo)
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, SPREAD_POTENTIAL_TEMPLATE, yearFrom, yearTo)
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, SPREAD_RESISTANCE_TEMPLATE, yearFrom, yearTo)
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, SPREAD_COSTDST_TEMPLATE, yearFrom, yearTo)

    #attack
    exportPrognosisLayersToAAI(sourceMapset, outputPrefix, ATTACK_OUTPUT_TEMPLATE, yearFrom, yearTo)

#endregion EXPORT_TO_AAI
