#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.samples_generate
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Generate spot samples
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Generates spot samples
#% keywords: bark beetle spot sample
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
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPrognosisLib


def main():         
    projectFN = options["param"]

    bboPrognosisLib.generateSamplesSeries(projectFN)

    # finish calculation, restore settings
    bboLib.doneMessage() 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
