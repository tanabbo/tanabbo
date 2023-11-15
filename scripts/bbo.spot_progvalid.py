#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_progvalid
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Spot prognosis validation
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Manual crosstabulation of spot prognosis
#% keywords: bark beetle spot prognosis validation
#%end
#%option G_OPT_R_INPUT
#% key: s50mask
#% answer: s50mask@forest
#% description: Spruce mask (s50mask)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: actspot
#% answer: bb_spot_1987@forest
#% description: Recorded bark beetle spots
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: progspot
#% answer: p1_spot_1987@bb_prognosis
#% description: Prognosis of bark beetle spots
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
    spot1 = "tmp_progvalid1"
    spot2 = "tmp_progvalid2"
    spot3 = "tmp_progvalid3"
    s50Mask0 = "tmp_progvalid_s50mask0"

    s50Mask = bboLib.checkInputRaster(options, "s50mask")
    actSpot = bboLib.checkInputRaster(options, "actspot")
    progSpot = bboLib.checkInputRaster(options, "progspot")

    bboPrognosisLib.spotCrosstabFN(bboLib.forestMapset, s50Mask, actSpot, progSpot)

    bboLib.deleteRaster(spot1)
    bboLib.deleteRaster(spot2)
    bboLib.deleteRaster(spot3)
    bboLib.deleteRaster(s50Mask0)

    # finish calculation, restore settings
    grass.message(_("Done."))      


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
