#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.MergeLoss
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Merge raster layers into a binary raster layer
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Merge raster layers into a binary raster layer
#% keyword: raster
#% keyword: merge
#%end
#%option G_OPT_R_INPUTS
#% key: input_rasters
#% description: Names of raster layers to be merged into a binary raster
#% required: yes
#%end

import grass.script as gscript

def merge_raster_layers(input_rasters, output_raster):
    # Set region to match the first input raster
    gscript.run_command('g.region', raster=input_rasters[0])

    # Create a temporary raster for the binary output
    temp_raster = "temp_binary_output"
    gscript.mapcalc(f"{temp_raster} = if(" + " || ".join([f"isnull({r}) == 0" for r in input_rasters]) + ", 1, 0)", overwrite=True)

    # Rename the temporary raster to the desired output raster name
    gscript.run_command('g.rename', raster=f"{temp_raster},{output_raster}", overwrite=True)

def main():
    input_rasters = options['input_rasters'].split(',')
    output_raster = "bb_spot_merged1.tif"  # Hardcoded output filename
    merge_raster_layers(input_rasters, output_raster)

if __name__ == "__main__":
    options, flags = gscript.parser()
    main()
