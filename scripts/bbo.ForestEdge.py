#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.ForestEdge
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Identify edges of objects within bb_spot_merged adjacent to forest areas
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Identify edges of objects within bb_spot_merged adjacent to forest areas
#% keyword: forest edge
#%end
#%option G_OPT_R_INPUT
#% key: s50mask
#% description: Name of raster to use as forest mask (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: bb_spot_merged
#% description: Name of raster to use as object mask (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: forest_edge
#% description: Output raster with forest edges
#% answer: forest_edge
#% required: yes
#%end

import grass.script as gs
import rasterio
import numpy as np
from scipy.ndimage import binary_erosion, label

def process_forest_edge(s50mask, bb_spot_merged, forest_edge):
    # Export rasters from GRASS GIS for processing
    gs.run_command('r.out.gdal', input=s50mask, output="temp_forest_mask.tif", format='GTiff', createopt='COMPRESS=LZW', overwrite=True)
    gs.run_command('r.out.gdal', input=bb_spot_merged, output="temp_object_mask.tif", format='GTiff', createopt='COMPRESS=LZW', overwrite=True)

    # Read the rasters using rasterio
    with rasterio.open("temp_forest_mask.tif") as forest_src:
        forest_mask = forest_src.read(1).astype(bool)
        profile = forest_src.profile

    with rasterio.open("temp_object_mask.tif") as object_src:
        object_mask = object_src.read(1).astype(bool)

    # Label the objects in the object mask
    labeled_array, _ = label(object_mask)

    # Identify edges of each object
    edge_mask = np.zeros_like(labeled_array, dtype=np.bool_)
    for i in range(1, labeled_array.max() + 1):
        object_slice = (labeled_array == i)
        object_border = object_slice & np.logical_not(binary_erosion(object_slice))
        edge_mask = np.logical_or(edge_mask, object_border)

    # Filter edges to keep only those adjacent to forest areas
    forest_edge_mask = edge_mask & forest_mask

    # Count the number of edge pixels
    num_edge_pixels = np.sum(forest_edge_mask)

    # Calculate the length of the treated forest edges
    length_of_edges = num_edge_pixels * 30  # Assuming each pixel represents 30 meters

    # Write the result to a file
    profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open("temp_forest_edge.tif", 'w', **profile) as dst:
        dst.write(forest_edge_mask.astype(rasterio.uint8) * 255, 1)

    # Import the processed data back into GRASS GIS
    gs.run_command('r.in.gdal', input="temp_forest_edge.tif", output=forest_edge, overwrite=True)

    # Print the desired information
    print("Forest edge processing complete.")
    print(f"The number of pixels is {num_edge_pixels}.")
    print(f"Length of treated forest edges equals {length_of_edges} meters.")

def main():
    options, flags = gs.parser()
    process_forest_edge(options['s50mask'], options['bb_spot_merged'], options['forest_edge'])
if __name__ == "__main__":
    main()
