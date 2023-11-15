#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.model_build
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Build models
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Build models
#% keywords: build init, spot and attack probability model
#%end
#%option
#% key: param
#% type: string
#% answer: prognosis1.json
#% description: Project parameters
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
    projectFN = options["param"]

    bboPrognosisLib.buildModel(projectFN)

    # finish calculation, restore settings
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
