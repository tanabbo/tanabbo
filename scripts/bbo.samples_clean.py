#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.samples_clean
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Cleans spot samples
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Cleans spot samples
#% keywords: clean bark beetle spot samples
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
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPrognosisLib

def main():         
    yearFrom = int(options["yearfrom"])
    yearTo = int(options["yearto"])

    bboPrognosisLib.cleanSamplesSeries(yearFrom, yearTo)

    # finish calculation, restore settings
    bboLib.doneMessage()


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
