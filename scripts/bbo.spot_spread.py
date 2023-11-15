#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_spread
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Validation: spread probability of a spot
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Spot spread probability
#% keywords: bark beetle spread probability
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
#% answer: 1980
#% description: First year
#% required: yes
#%end
#%option
#% key: yearto
#% type: integer
#% answer: 2025
#% description: Last year
#% required: yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboPrognosisLib


def main():         
    paramFN = options["param"]
    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])
    
    bboPrognosisLib.spreadProbability(paramFN, yearFrom, yearTo)

    # finish calculation, restore settings
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
