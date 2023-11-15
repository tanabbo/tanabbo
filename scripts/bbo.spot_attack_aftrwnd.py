#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.spot_attack_aftrwnd
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates probability of bark beetle attack after windthrow
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates probability of of bark beetle attack after windthrow
#% keywords: bark beetle attack probability windthrow
#%end
#%option G_OPT_R_INPUT
#% key: totalspot
#% answer: bb_spot_2011@forest
#% description: Total spot area (totalspot)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: s50mask
#% answer: s50Mask@forest
#% description: Spruce forest mask (s50mask)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: attackprob
#% answer: bb_attack_prob@bb_prognosis
#% description: Bark beetle attack probability (attackprob)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: wndthrow
#% answer: wndth_2011@forest
#% description: Windthrow area (wndthrow)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: wndattprob
#% answer: bb_wndattack_prob
#% description: Attack probability after wind throow (wndattprob)
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
    tmp1 = "tmp_bb_prognosis1"
    tmp2 = "tmp_bb_prognosis2"
    tmp3 = "tmp_bb_prognosis3"    
    actualSpot0 = "tmp_actual_spot0"

    spotSource = bboLib.checkInputRaster(options, "totalspot")
    s50Mask = bboLib.checkInputRaster(options, "s50mask")
    attackProb = bboLib.checkInputRaster(options, "attackprob")
    wndThrow = bboLib.checkInputRaster(options, "wndthrow")
    wndAttackProb = bboLib.checkOutputRaster(options, "wndattprob")

    userMapset = grass.gisenv()["MAPSET"]  
    if userMapset != targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)
    
    # prepare actualSpot
    grass.mapcalc("$tmp1 = $spotSource * $s50Mask", tmp1=tmp1, spotSource=spotSource, s50Mask=s50Mask, overwrite=True)
    grass.mapcalc("$actualSpot0 = if(0 < $tmp1, 1, null())", actualSpot0=actualSpot0, tmp1=tmp1, overwrite=True)
    grass.run_command("r.null", map=actualSpot0, null=0, quiet=True)

    # probability of bark beetle attack after windthrow
    grass.mapcalc("$tmp1 = if(0 < $wndThrow * $s50Mask, 2, 0)", tmp1=tmp1, wndThrow=wndThrow, s50Mask=s50Mask, overwrite=True, quiet=True)
    grass.run_command("r.null", map=tmp1, null=0, quiet=True)
    grass.mapcalc("$tmp2 = $attackProb", overwrite=True, tmp2=tmp2, attackProb=attackProb)
    grass.run_command("r.null", map=tmp2, null=0, quiet=True)
    grass.mapcalc("$tmp3 = max($tmp1,$tmp2)", overwrite=True, tmp3=tmp3, tmp1=tmp1, tmp2=tmp2)
    grass.run_command("r.null", map=tmp3, null=0, quiet=True)
    grass.mapcalc("$tmp1 = $s50Mask - $actualSpot0", tmp1=tmp1, s50Mask=s50Mask, actualSpot0=actualSpot0, overwrite=True, quiet=True)
    grass.mapcalc("$tmp2 = $tmp1 * $tmp3", overwrite=True, tmp1=tmp1, tmp3=tmp3, tmp2=tmp2)
    bboLib.rescaleRaster(tmp2, wndAttackProb)

    bboLib.deleteRaster(actualSpot0)
    bboLib.deleteRaster(tmp3)
    bboLib.deleteRaster(tmp2)
    bboLib.deleteRaster(tmp1)

    # finish calculation, restore settings
    if userMapset != targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))      


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
