#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_samples_assign
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Assigns probabilities to samples
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#%description: Assigns probabilities and independend variables to samples
#%keywords: bark beetle sample probability independend variable
#%end
#%option
#% key: project
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
    projectFN = options["project"]

    bboPrognosisLib.assignSpotSamplesSeries(projectFN)

    # finish calculation, restore settings
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
