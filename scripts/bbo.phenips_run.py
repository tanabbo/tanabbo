#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.phenips_run
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Run PHENIPS model
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Runs PHENIPS model
#% keywords: bark beetle phenips
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib
import bboPhenipsLib


def main():
    targetMapset = bboLib.phenipsMapset
    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    bboPhenipsLib.atDDCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                           bboLib.phenipsDDThreshold, 
                           bboLib.phenipsMapset, bboLib.phenipsATDDPrefix)

    bboPhenipsLib.swarmingCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                               bboLib.phenipsSwarmingDDThreshold, bboLib.phenipsFlightThreshold,
                               bboLib.phenipsMapset, 
                               bboLib.rasterMonth(bboLib.phenipsSwarmingName, 1), 
                               bboLib.phenipsATDDPrefix)

    bboPhenipsLib.infestationCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                                  bboLib.phenipsInfestationDDThreshold, bboLib.phenipsFlightThreshold,
                                  bboLib.phenipsMapset, 
                                  bboLib.rasterMonth(bboLib.phenipsSwarmingName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsInfestationName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsInfestationSpan, 1),
                                  bboLib.phenipsATDDPrefix)

    bboPhenipsLib.developmentCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                                  bboLib.phenipsDDThreshold, 
                                  bboLib.phenipsInfestationDDThreshold, bboLib.phenipsFlightThreshold,
                                  bboLib.phenipsDevelopmentSumThreshold,
                                  bboLib.phenipsMapset, 
                                  bboLib.rasterMonth(bboLib.phenipsInfestationName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsDevelopmentName, 1),
                                  bboLib.rasterMonth(bboLib.phenipsDevelopmentSpanName, 1),
                                  bboLib.phenipsBTDDPrefix)

    bboLib.deleteDaySeries(bboLib.phenipsATDDPrefix)

    bboPhenipsLib.calcGenerations(bboLib.phenipsToDay)

    bboPhenipsLib.stageCalc(bboLib.phenipsFromDay, bboLib.phenipsToDay,
                            bboLib.phenipsMapset, 
                            bboLib.phenipsSwarmingName,
                            bboLib.phenipsInfestationName,
                            bboLib.phenipsDevelopmentName,
                            bboLib.phenipsStagePrefix)

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done.")) 


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
