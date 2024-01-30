#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.Antiattractant
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Generate raster of antiattractant installation
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Generate raster of antiattractant installation
#% keyword: antiattractant
#% keyword: TANABBO
#%end
#%option G_OPT_R_INPUT
#% key: forest_edge_buffer
#% description: Input raster with forest edge buffer
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: bb_spot_merged
#% description: Name of raster to use as forest loss (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_OUTPUT
#% key: antiattractant
#% description: Output raster with antiattractant placement (binary)
#% answer: antiattractant
#% required: yes
#%end

import grass.script as gs
import numpy as np
import tempfile
import os


def read_grass_raster(raster_name):
    
    # Create a unique temporary file
    fd, temp_file_path = tempfile.mkstemp()
    os.close(fd)

    # Export the raster to the temporary ASCII file
    gs.run_command('r.out.ascii', input=raster_name, output=temp_file_path)

    # Read the ASCII file into a numpy array
    raster_array = np.loadtxt(temp_file_path)

    # Remove the temporary file
    os.remove(temp_file_path)

    return raster_array

def write_grass_raster(raster_name, data):
    # Create a unique temporary file
    fd, temp_file_path = tempfile.mkstemp()
    os.close(fd)

    # Save the numpy array to the temporary ASCII file
    np.savetxt(temp_file_path, data, fmt='%d')

    # Import the data from the temporary ASCII file into a new GRASS raster
    gs.run_command('r.in.ascii', input=temp_file_path, output=raster_name, overwrite=True)

    # Remove the temporary file
    os.remove(temp_file_path)

def process_antiattractant(forest_edge_buffer_layer, bb_spot_merged_layer, output_layer):
    # Import rasters into numpy arrays
    forest_edge_buffer = read_grass_raster(forest_edge_buffer_layer).astype(bool)
    bb_spot_merged = read_grass_raster(bb_spot_merged_layer).astype(bool)

    # Initialize the output mask with the current forest edge buffer
    antiattractant_mask = np.copy(forest_edge_buffer)

    # Iterate over each pixel, skipping the first row to avoid index errors
    for row in range(1, forest_edge_buffer.shape[0]):
        for col in range(forest_edge_buffer.shape[1]):
            # If the pixel in forest_edge_buffer is True and the pixel to the north in bb_spot_merged is also True
            if forest_edge_buffer[row, col] and bb_spot_merged[row-1, col]:
                antiattractant_mask[row, col] = False

    # Convert the boolean mask back to an integer type suitable for writing to a TIFF
    antiattractant = antiattractant_mask.astype(np.uint8)

    # Export the result back into GRASS GIS
    write_grass_raster(output_layer, antiattractant)

    # Count pixels with value of 1
    num_pixels = np.sum(antiattractant == 1)

    # Calculate length of treated forest edges
    length_of_edges = num_pixels * 30

    # Calculate the number of trees with antiattractant
    num_trees_min = length_of_edges // 20
    num_trees_medium = length_of_edges // 10
    num_trees_max = length_of_edges // 5

    # Print the results
    print("Antiattractant installation pixel generation is complete.")
    print(f"The number of antiattractant pixels is {num_pixels}")
    print(f"The length of treated forest edges is {length_of_edges} m")
    print(f"The number of trees with antiattractant is {num_trees_min} (min)")
    print(f"The number of trees with antiattractant is {num_trees_medium} (medium)")
    print(f"The number of trees with antiattractant is {num_trees_max} (max)")

def main():
    options, flags = gs.parser()
    process_antiattractant(options['forest_edge_buffer'], options['bb_spot_merged'], options['antiattractant'])
if __name__ == "__main__":
    main()
