#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.risk_cdef
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates cumulative deficit risk
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates cumulative deficit risk
#% keywords: cumulative deficit risk
#% keywords:TANABBO
#%end
#%option
#% key: dayfrom
#% type: integer
#% options: 1-365
#% answer: 104
#% description: Day from (1 - 365)
#% required : yes
#%end
#%option
#% key: dayto
#% type: integer
#% options: 1-365
#% answer: 106
#% description: Day to (1 - 365)
#% required : yes
#%end
#%option
#% key: threshold
#% type: double
#% answer: 20.0
#% description: Risk threshold
#% required: yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
import bboLib
import bboDroughtLib


def main():
    targetMapset = bboLib.hydroMapset

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])
    threshold = float(options["threshold"])

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))

    bboDroughtLib.calcRiskForecastCDEF(dayFrom, dayTo, threshold)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)

    grass.message(_("Done."))    



if __name__ == "__main__":
    options, flags = grass.parser()
    main()
