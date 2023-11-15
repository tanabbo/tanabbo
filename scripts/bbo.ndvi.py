#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.ndvi
# AUTHOR(S):	Ivan Barka, Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Computes NDVI index for Landsat scene
# COPYRIGHT:	This program is free software under the GNU General Public
#		        License (>=v2). Read the file COPYING that comes with GRASS
#		        for details.
#
#############################################################################

#%module
#% description: Computes Normalized Difference Vegetation Index (NDVI) for Landsat scene.
#% keywords: raster NDVI
#%end
#%option G_OPT_R_INPUT
#% key: tm3
#% description: Name of raster to use as red band (TM3)
#% required : yes
#%end
#%option G_OPT_R_INPUT
#% key: tm4
#% description: Name of raster to use as infrared band (TM4)
#% required : yes
#%end
#%option G_OPT_R_OUTPUT
#% key: output_ndvi
#% description: Name of output raster with NDVI index
#% required : yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
import bboLib

def main():

    #bboLib.copyLandsat("landsat_vi", "ls_%Y_lc8.toar.%b", "landsat", "ls_%Y_%B", 2001, 2014, 1, 11)
    #bboLib.calcNDVI("landsat", "ls_%Y_%B", "ndvi_%Y", 2008, 2014)
    #bboLib.calcVCI("landsat", "ls_%Y_%B", "vci_%Y", 2001, 2014)
    #bboLib.calcNSC2("landsat", "ls_%Y_%B", "nsc2_%Y", 2001, 2014)
    #return

    tm4 = options['tm4']
    tm3 = options['tm3']
    output_ndvi = options['output_ndvi']

    if not tm3:
        grass.fatal(_("Required parameter <TM3> not set"))

    if not tm4:
        grass.fatal(_("Required parameter <TM4> not set"))

    #check if input files exists
    if not grass.find_file(tm3)['file']:
        grass.fatal(_("<%s> does not exist.") % tm3)
    if not grass.find_file(tm4)['file']:
        grass.fatal(_("<%s> does not exist.") % tm4)

    mapset = grass.gisenv()['MAPSET']  

    grass.mapcalc("$output = 1.0 * ( $tm4 - $tm3 ) / ( $tm4 + $tm3 )", output = output_ndvi, tm3 = tm3, tm4 = tm4)

    # set history for site map
    grass.raster_history(output_ndvi)

    grass.message(_("Done."))    

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
