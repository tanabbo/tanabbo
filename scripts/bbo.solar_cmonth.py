#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.solar_cmonth
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates summary corrected solar irradiation for months
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates summary corrected solar irradiation for months.
#% keywords: solar irradiation
#%end
#%flag
#% key: c
#% description: Clean mapset
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
    cleanMapset = flags["c"]
    bboSolarLib.sumMonth(bboLib.solarMapset, bboLib.srdayPrefix, bboLib.srmonthPrefix, "corected solar irradiation for month")


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
