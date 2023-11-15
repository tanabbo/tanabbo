#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.nsc2
# AUTHOR(S):	Ivan Barka, Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Computes NSC2 index for Landsat scene
# COPYRIGHT:	This program is free software under the GNU General Public
#		        License (>=v2). Read the file COPYING that comes with GRASS
#		        for details.
#
#############################################################################

#%module
#% description: Computes New Synthetic Channel 2 Index (NSC2) for Landsat scene.
#% keywords: raster
#% keywords: NSC2
#% keywords:bark beetle outbreak
#% keywords:TANABBO
#% keywords: ips typographus
#%end
#%option G_OPT_R_INPUT
#% key: tm1
#% description: Name of raster to use as blue band (TM1)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: tm2
#% description: Name of raster to use as green band (TM2)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: tm3
#% description: Name of raster to use as red band (TM3)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: tm4
#% description: Name of raster to use as near infrared band (TM4)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: tm5
#% description: Name of raster to use middle infrared band (TM5)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: tm7
#% description: Name of raster to use as far infrared band (TM7)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: output_nsc2
#% description: Name of output raster with NSC2 index
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
    tm1 = options['tm1']
    tm2 = options['tm2']
    tm3 = options['tm3']
    tm4 = options['tm4']
    tm5 = options['tm5']
    tm7 = options['tm7']
    output_nsc2 = options['output_nsc2']

    if not tm1:
        grass.fatal(_("Required parameter <TM1> not set"))
    if not tm2:
        grass.fatal(_("Required parameter <TM2> not set"))
    if not tm3:
        grass.fatal(_("Required parameter <TM3> not set"))
    if not tm4:
        grass.fatal(_("Required parameter <TM4> not set"))
    if not tm5:
        grass.fatal(_("Required parameter <TM5> not set"))
    if not tm7:
        grass.fatal(_("Required parameter <TM7> not set"))

    #check if input files exists
    if not grass.find_file(tm1)['file']:
        grass.fatal(_("<%s> does not exist.") % tm1)
    if not grass.find_file(tm2)['file']:
        grass.fatal(_("<%s> does not exist.") % tm2)
    if not grass.find_file(tm3)['file']:
        grass.fatal(_("<%s> does not exist.") % tm3)
    if not grass.find_file(tm4)['file']:
        grass.fatal(_("<%s> does not exist.") % tm4)
    if not grass.find_file(tm5)['file']:
        grass.fatal(_("<%s> does not exist.") % tm5)
    if not grass.find_file(tm7)['file']:
        grass.fatal(_("<%s> does not exist.") % tm7)

    mapset = grass.gisenv()['MAPSET']  

    grass.mapcalc("$output = ( 0.1283 * $tm1 ) + ( 0.1126 * $tm2 ) + ( 0.3487 * $tm3 ) - ( 0.5011 * $tm4 ) + ( 0.5352 * $tm5 ) + ( 0.5581 * $tm7 )", 
	              output = output_nsc2,
				  tm1 = tm1, tm2 = tm2, tm3 = tm3, tm4 = tm4, tm5 = tm5, tm7 = tm7)
    
    # set history for site map
    grass.raster_history(output_nsc2)

    grass.message(_("Done."))    

if __name__ == "__main__":
    options, flags = grass.parser()
    tmp = None
    atexit.register(cleanup)
    main()
