#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.solar_cyear
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates summary corrected solar irradiation for year
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates summary corrected solar irradiation for year.
#% keywords: solar irradiation
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboSolarLib


def main():   
    bboSolarLib.sumYear(bboLib.solarMapset, bboLib.srmonthPrefix, bboLib.sryearPrefix, "corrected summary solar irradiation for year")


if __name__ == "__main__":
    options, flags = grass.parser()
    main()