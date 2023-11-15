#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_prognosis
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates bark beetle spot prognosis
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Manual bark beetle spot prognosis
#% keywords: bark beetle spot prognosis
#%end
#%option G_OPT_R_INPUT
#% key: totalspot
#% answer: bb_spot_1986@forest
#% description: All bark beetle spots (totalspot)
#% required: yes
#%end
#%option
#% key: yearinit
#% type: integer
#% answer: 1986
#% description: Initial year
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: s50mask
#% answer: s50mask@forest
#% description: Spruce mask (s50mask)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: attackprob
#% answer: bb_attack_prob@bb_prognosis
#% description: Bark beetle attack probability (attackprob)
#% required: yes
#%end
#%option
#% key: treemortality
#% type: double
#% answer: 1.0
#% description: Tree mortality (e.g. 0.31 or 4.9)
#% required: yes
#%end
#%option
#% key: yearprog
#% type: integer
#% answer: 1987
#% description: Year of prognosis
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: spotprognosis
#% answer: prognosis
#% description: Output bark beetle spot prognosis (spotprognosis)
#% required: yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPrognosisLib


def main():
    targetMapset = "bb_prognosis"
    nSteps = 25

    s50MaskFN = bboLib.checkInputRaster(options, "s50mask")
    bbAttackProb = bboLib.checkInputRaster(options, "attackprob")
    spotPrognosis = bboLib.checkOutputRaster(options, "spotprognosis")
    treeMortality = float(options["treemortality"])
    yearInit = int(options["yearinit"])
    yearPrognosis = int(options["yearprog"])
    spotFN = bboLib.rasterYear(bboLib.spotPrefix, yearInit, bboLib.forestMapset)

    bboPrognosisLib.spotPrognosisCalc(targetMapset, s50MaskFN, 
                                      spotFN, bbAttackProb, treeMortality, spotPrognosis, bboPrognosisLib.spotPrognosisNSteps)

    # finish calculation, restore settings
    grass.message(_("Done."))      


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
