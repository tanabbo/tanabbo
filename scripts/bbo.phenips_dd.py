#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.phenips_dd
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates degree days
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates degree days
#% keywords: bark beetle phenips
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPhenipsLib


def main():
    bboPhenipsLib.atDDCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                           bboLib.phenipsDDThreshold, 
                           bboLib.phenipsMapset, bboLib.phenipsATDDPrefix)
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
