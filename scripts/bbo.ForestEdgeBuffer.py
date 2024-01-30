#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.ForestEdgeBuffer
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Generate forest edge buffer
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Generate forest edge buffer
#% keyword: forest edge
#%end
#%option G_OPT_R_INPUT
#% key: s50mask_upd
#% description: Name of raster to use as forest mask (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: bb_spot_merged
#% description: Name of raster to use as forest loss (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: forest_edge_buffer
#% description: Output raster with forest edge buffer
#% answer: forest_edge_buffer
#% required: yes
#%end

import grass.script as gs
import rasterio
import numpy as np
from scipy.ndimage import binary_dilation

def process_forest_edge(s50mask_upd, bb_spot_merged, forest_edge_buffer):
    # Export rasters from GRASS GIS for processing
    gs.run_command('r.out.gdal', input=s50mask_upd, output="temp_forest_mask.tif", format='GTiff', createopt='COMPRESS=LZW', overwrite=True)
    gs.run_command('r.out.gdal', input=bb_spot_merged, output="temp_loss_mask.tif", format='GTiff', createopt='COMPRESS=LZW', overwrite=True)

    # Read the rasters using rasterio
    with rasterio.open("temp_forest_mask.tif") as forest_src:
        forest_mask = forest_src.read(1).astype(bool)
        forest_profile = forest_src.profile

    with rasterio.open("temp_loss_mask.tif") as loss_src:
        loss_mask = loss_src.read(1).astype(bool)

    # Create a dilation of the loss mask
    dilated_loss_mask = binary_dilation(loss_mask, iterations=1)

    # Find the edge pixels: pixels that are in the dilated loss mask AND in the updated forest mask
    edge_pixels = np.logical_and(dilated_loss_mask, forest_mask)

    # Count the number of edge pixels
    num_edge_pixels = np.sum(edge_pixels)

    # Calculate the length of the treated forest edges
    length_of_edges = num_edge_pixels * 30  # Assuming each pixel represents 30 meters

    # Convert the edge pixels mask back to uint8 for raster output
    # Edge pixels are marked as 1, others as 0
    edge_pixels_uint8 = edge_pixels.astype(np.uint8) * 255

    # Write the result to a temporary file
    forest_profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open("temp_forest_edge_buffer.tif", 'w', **forest_profile) as dst:
        dst.write(edge_pixels.astype(rasterio.uint8), 1)

    # Import the processed data back into GRASS GIS
    gs.run_command('r.in.gdal', input="temp_forest_edge_buffer.tif", output=forest_edge_buffer, overwrite=True)
    
    print("Forest edge buffer processing complete.")
    print(f"The number of pixels is {num_edge_pixels}.")
    print(f"Length of treated forest edges is {length_of_edges} meters.")

def main():
    options, flags = gs.parser()
    process_forest_edge(options['s50mask_upd'], options['bb_spot_merged'], options['forest_edge_buffer'])
if __name__ == "__main__":
    main()
