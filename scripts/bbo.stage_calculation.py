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

    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

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
