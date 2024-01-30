#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.Traps
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Generate point file of traps installation
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Generate point file of traps installation
#% keywords: traps, forest edges
#%end
#%option G_OPT_R_INPUT
#% key: s50mask
#% description: Raster for forest mask (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: bb_spot_merged
#% description: Raster for forest loss (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_R_INPUT
#% key: forest_edge
#% description: Raster for forest edge (binary: 1 or no-data)
#% required: yes
#%end
#%option G_OPT_F_INPUT
#% key: distance
#% type: double
#% description: Distance between traps (meters)
#% answer: 50
#% required: yes
#%end
#%option G_OPT_V_OUTPUT
#% key: pheromone_trap
#% description: Output point layer for pheromone traps
#% answer: pheromone_trap
#% required: yes
#%end

import grass.script as gs
import numpy as np
import geopandas as gpd
import pyproj
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points, transform
from scipy.ndimage import binary_dilation


def generate_and_filter_points(forest_edge_mask, s50mask, forest_transform,
                               forest_crs):
    rows, cols = np.where(forest_edge_mask == 1)
    geometries_mask = [Point(forest_transform * (col + 0.5, row + 0.5))
                       for col, row in zip(cols, rows)]
    gdf_mask = gpd.GeoDataFrame(geometry=geometries_mask)
    gdf_mask.set_crs(forest_crs, inplace=True)

    mask_polygon_features = [
        shape(shape_val) for shape_val, val in
        features.shapes(s50mask.astype(np.uint8), transform=forest_transform)
        if val == 1
    ]

    if not mask_polygon_features:
        raise ValueError("No valid geometries found in s50mask!")

    mask_gdf = gpd.GeoDataFrame({'geometry': mask_polygon_features})
    mask_gdf.crs = forest_crs

    gdf_mask_within = sjoin(gdf_mask, mask_gdf, how="inner", op="within")
    all_centroids_mask_filtered = gdf_mask_within['geometry'].values

    return all_centroids_mask_filtered


def determine_utm_zone(centroid):
    zone_number = (int((centroid.x + 180) / 6) % 60) + 1
    return f"EPSG:326{zone_number:02}" if centroid.y > 0 else \
        f"EPSG:327{zone_number:02}"


def generate_filtered_centroids_shp(edge, forest_transform, forest_crs,
                                    all_centroids_mask_filtered, output_file_path):
    rows, cols = np.where(edge == 1)
    geometries = [Point(forest_transform * (col + 0.5, row + 0.5))
                  for col, row in zip(cols, rows)]
    gdf = gpd.GeoDataFrame(geometry=geometries)
    gdf.set_crs(forest_crs, inplace=True)

    all_centroids = [(geometry.x, geometry.y) for geometry in gdf.geometry]
    utm_zone = determine_utm_zone(Point(all_centroids[0]))

    project_to_utm = pyproj.Transformer.from_crs(forest_crs, utm_zone,
                                                 always_xy=True).transform
    project_to_wgs84 = pyproj.Transformer.from_crs(utm_zone, forest_crs,
                                                   always_xy=True).transform
    all_centroids_mask_utm = [transform(project_to_utm, Point(c))
                              for c in all_centroids_mask_filtered]

    final_centroids_mask_utm = []
    for point in all_centroids_mask_utm:
        if final_centroids_mask_utm:
            nearest = nearest_points(point, MultiPoint(final_centroids_mask_utm))
        else:
            nearest = [None, Point(9999, 9999)]

        if point.distance(nearest[1]) > 50:
            final_centroids_mask_utm.append(point)
    final_centroids_mask = [transform(project_to_wgs84, point)
                            for point in final_centroids_mask_utm]
    
    # Calculate the number of traps
    num_traps = len(final_centroids_mask)

    print("Trap installation point generation is complete.")
    print(f"The number of traps is {num_traps}.")

def main():
    options, flags = gs.parser()
if __name__ == "__main__":
    main()