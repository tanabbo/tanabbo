#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.vci
# AUTHOR(S):	Ivan Barka, Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Computes VCI index for Landsat scene
# COPYRIGHT:	This program is free software under the GNU General Public
#		        License (>=v2). Read the file COPYING that comes with GRASS
#		        for details.
#
#############################################################################

#%module
#% description: Computes Vegetation Condition Index (VCI) for Landsat scene.
#% keywords: raster
#% keywords: VCI
#% keywords:bark beetle outbreak
#% keywords:TANABBO
#% keywords: ips typographus
#%end
#%option G_OPT_R_INPUT
#% key: tm4
#% description: Name of raster to use as near infrared band (TM4)
#% required : yes
#%end
#%option G_OPT_R_INPUT
#% key: tm7
#% description: Name of raster to use as far infrared band (TM7)
#% required : yes
#%end
#%option G_OPT_R_OUTPUT
#% key: output_vci
#% description: Name of output raster with VCI index
#%end

import sys
import os
import grass.script as grass
import atexit
import string

def cleanup():
    if tmp:
        grass.run_command('g.remove', rast = tmp, quiet = True)

def main():
    tm4 = options['tm4']
    tm7 = options['tm7']
    output_vci = options['output_vci']

    if not tm4:
        grass.fatal(_("Required parameter <TM4> not set"))
    if not tm7:
        grass.fatal(_("Required parameter <TM7> not set"))

    #check if input files exists
    if not grass.find_file(tm4)['file']:
        grass.fatal(_("<%s> does not exist.") % tm4)
    if not grass.find_file(tm7)['file']:
        grass.fatal(_("<%s> does not exist.") % tm7)

    mapset = grass.gisenv()['MAPSET']  
    
    grass.mapcalc("$output = 1.0 * $tm7 / $tm4", output = output_vci, tm4 = tm4, tm7 = tm7)

    # set history for site map
    grass.raster_history(output_vci)

    grass.message(_("Done."))    

if __name__ == "__main__":
    options, flags = grass.parser()
    tmp = None
    atexit.register(cleanup)
    main()
