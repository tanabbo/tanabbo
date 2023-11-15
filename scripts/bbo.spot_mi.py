#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_mi
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates prognose of mortality index
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates prognose of mortality index
#% keywords: bark beetle spot mortality index
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
    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])

    if (yearTo < yearFrom):
        grass.fatal("yearfrom must be less or equal to YearTo")

    miStat = bboPrognosisLib.miSeries(yearFrom, yearTo)

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

    # finish calculation, restore settings
    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
