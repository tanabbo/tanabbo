#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.mngmt_onp
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates bark beetle spot prognosis
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates ONP prognoses of bark beetle spots
#% keywords: bark beetle scenario
#%end
#%option G_OPT_R_INPUT
#% key: totalspot
#% answer: bb_spot_2011@forest
#% description: All bark beetle spots (totalspot)
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
#% key: tmoptimistic
#% type: double
#% answer: 0.5
#% description: Optimistic tree mortality (e.g. 0.31 or 4.9)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: progoptimistic
#% answer: prog_optimistic
#% description: Output optimistic bark beetle spot prognosis (progoptimistic)
#% required: yes
#%end
#%option
#% key: tmnormal
#% type: double
#% answer: 1.0
#% description: Normal tree mortality (e.g. 0.31 or 4.9)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: prognormal
#% answer: prog_normal
#% description: Output normal bark beetle spot prognosis (prognormal)
#% required: yes
#%end
#%option
#% key: tmpesimistic
#% type: double
#% answer: 3.0
#% description: Pesimistic tree mortality (e.g. 0.31 or 4.9)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: progpesimistic
#% answer: prog_pesimistic
#% description: Output pesimistic bark beetle spot prognosis (progpesimistic)
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
    targetMapset = "bb_prognosis"
    nSteps = 25

    s50Mask = bboLib.checkInputRaster(options, "s50mask")
    spotSource = bboLib.checkInputRaster(options, "totalspot")
    bbAttackProb = bboLib.checkInputRaster(options, "attackprob")

    tmOptimistic = float(options["tmoptimistic"])
    progOptimistic = bboLib.checkOutputRaster(options, "progoptimistic")
    tmNormal = float(options["tmnormal"])
    progNormal = bboLib.checkOutputRaster(options, "prognormal")
    tmPesimistic = float(options["tmpesimistic"])
    progPesimistic = bboLib.checkOutputRaster(options, "progpesimistic")

    bboLib.spotPrognosis(targetMapset, s50Mask, spotSource, bbAttackProb, tmOptimistic, progOptimistic, nSteps)
    bboLib.spotPrognosis(targetMapset, s50Mask, spotSource, bbAttackProb, tmNormal, progNormal, nSteps)
    bboLib.spotPrognosis(targetMapset, s50Mask, spotSource, bbAttackProb, tmPesimistic, progPesimistic, nSteps)

    grass.message(_("Done."))      


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
