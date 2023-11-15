#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.export_samples
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Exports spot samples
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Exports spot samples
#% keywords: export bark beetle spot samples asc csv
#%end
#%option
#% key: filename
#% type: string
#% answer: prognosis1.json
#% description: Model parameters
#% required: yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
import math
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboPrognosisLib


def main():
    projectFN = options["filename"]

    bboPrognosisLib.exportSamplesSeries(projectFN)

    # finish calculation, restore settings
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
