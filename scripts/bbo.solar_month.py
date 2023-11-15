#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.solar_month
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates summary potential solar irradiation for months
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Calculates summary potential solar irradiation for months.
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
    bboSolarLib.sumMonth(bboLib.solarMapset, bboLib.psrdayPrefix, bboLib.psrmonthPrefix, "potential solar irradiation for month")
    grass.message(_("Done."))    


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
