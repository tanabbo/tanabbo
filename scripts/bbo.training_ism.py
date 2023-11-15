#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.training_ism
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Initiation/spread model methods training
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Initiation/spread model methods training
#% keywords: model methods training
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
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboPrognosisLib

def main():
    projectFN = options["filename"]

    bboPrognosisLib.runInitSpreadModelTraining(projectFN)

    grass.message(_("Done.")) 

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
