#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_dynamics_class
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Classification of bark beetle spot series
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Classification of bark beetle spot series
#% keywords: bark beetle spot series classification
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

    bboLib.spotClassificationDataSeries(yearFrom, yearTo)

    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
