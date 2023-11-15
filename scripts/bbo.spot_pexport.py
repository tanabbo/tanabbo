#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_pexport
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Export probabilities
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Export probabilities
#% keywords: bark beetle spot probability
#%end
#%option
#% key: param
#% type: string
#% answer: prognosis1.json
#% description: Model parameters
#% required: yes
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
#% answer: 2017
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
    paramFN = options["param"]
    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])

    if (yearTo < yearFrom):
        grass.fatal("yearfrom must be less or equal to YearTo")

    bboPrognosisLib.exportPrognosisToAAI(paramFN, yearFrom, yearTo)

    # finish calculation, restore settings
    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
