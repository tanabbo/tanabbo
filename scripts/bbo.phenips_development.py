#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.phenips_development
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates effective temperature
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Simulates bark beetle within tree development
#% keywords: bark beetle development
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
    bboPhenipsLib.developmentCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                                  bboLib.phenipsDDThreshold, 
                                  bboLib.phenipsInfestationDDThreshold, bboLib.phenipsFlightThreshold,
                                  bboLib.phenipsDevelopmentSumThreshold,
                                  bboLib.phenipsMapset, 
                                  bboLib.rasterMonth(bboLib.phenipsInfestationName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsDevelopmentName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsDevelopmentSpanName, 1), 
                                  bboLib.phenipsBTDDPrefix)
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
