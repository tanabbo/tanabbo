#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_dynamics_xdst
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates distance to active bark beetle spots
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates distance to active bark beetle spots for series
#% keywords: active bark beetle spot distance
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

    bboLib.distanceToActiveSpotsSeries(bboLib.forestMapset, yearFrom, yearTo)

    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
