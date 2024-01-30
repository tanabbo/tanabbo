#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.UpdateMask
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Update forest mask by excluding areas of forest loss indicated by the merged raster
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Update forest mask by excluding areas of forest loss indicated by the merged raster
#% keyword: raster
#% keyword: update
#%end
#%option G_OPT_R_INPUT
#% key: merged_raster
#% description: Merged raster layer (binary) indicating areas of forest loss
#% answer: bb_spot_merged1.tif
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: mask_raster
#% description: Original forest mask raster layer (binary)
#% answer: s50mask.tif
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: output_raster
#% description: Output raster layer with the updated forest mask (binary)
#% answer: s50mask_upd.tif
#% required: yes
#%end

import grass.script as gscript

def update_mask(merged_raster, mask_raster, output_raster):
    # Set the computational region to the mask raster
    gscript.run_command('g.region', raster=mask_raster)

    # Create a temporary raster for the updated mask
    temp_raster = "temp_updated_mask"
    gscript.mapcalc(f"{temp_raster} = if(isnull({merged_raster}), {mask_raster}, null())", overwrite=True)

    # Rename the temporary raster to the desired output raster name
    gscript.run_command('g.rename', raster=f"{temp_raster},{output_raster}", overwrite=True)

def main():
    merged_raster = options['merged_raster']
    mask_raster = options['mask_raster']
    output_raster = options['output_raster']

    update_mask(merged_raster, mask_raster, output_raster)

if __name__ == "__main__":
    options, flags = gscript.parser()
    main()
