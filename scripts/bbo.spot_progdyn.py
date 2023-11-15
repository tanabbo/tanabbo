#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_progdyn
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Dynamics of prognosis
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Manual calculation of spot dynamics
#% keywords: bark beetle spot prognosis dynamics
#%end
#%option G_OPT_R_INPUT
#% key: prevspot
#% answer: bb_spot_1986@forest
#% description: Raster of initial spots
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: prevspotid
#% answer: bb_spotid_1986@forest
#% description: IDs of initial spots
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: actspot
#% answer: prognosis
#% description: Raster of spot prognosis
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: actspotid
#% answer: prognosis_id
#% description: Output IDs of prognosed spots
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: actedst
#% answer: prognosis_edst
#% description: Output distance of spot enlargements
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: acteid
#% answer: prognosis_edstid
#% description: Output IDs of spot enlargements
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: actfdst
#% answer: prognosis_fdst
#% description: Output distance of new spots
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: actfid
#% answer: prognosis_fdstid
#% description: Output IDs of new spots
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

    prevSpot = bboLib.checkInputRaster(options, "prevspot")
    prevSpotId = bboLib.checkInputRaster(options, "prevspotid")
    actSpot = bboLib.checkInputRaster(options, "actspot")
    actSpotId = bboLib.checkOutputRaster(options, "actspotid")
    actEDst = bboLib.checkOutputRaster(options, "actedst")
    actEId = bboLib.checkOutputRaster(options, "acteid")
    actFDst = bboLib.checkOutputRaster(options, "actfdst")
    actFId = bboLib.checkOutputRaster(options, "actfid")

    bboLib.spotClassificationFN(targetMapset, 
                                prevSpot, prevSpotId, 
                                actSpot, actSpotId, actFDst, actEDst, actFId, actEId)

    # finish calculation, restore settings
    grass.message(_("Done."))      


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
