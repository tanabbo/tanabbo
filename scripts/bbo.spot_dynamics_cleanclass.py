#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_dynamics_clean
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Clean bark beetle spots classification
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Clean bark beetle spot classification
#% keywords: bark beetle spot classification clean
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
import bboLib

def main():
    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])

    bboLib.cleanSpotClassification(yearFrom, yearTo)

    # finish calculation, restore settings
    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
