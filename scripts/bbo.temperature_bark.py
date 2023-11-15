#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.temperature_bark
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Simulates mean and maximal bark temperature
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Simulates mean and maximal bark temperature.
#% keywords: bark temperature
#%end
#%option
#% key: dayfrom
#% type: integer
#% options: 1-365
#% answer: 1
#% description: Day from (1 - 365)
#% required : yes
#%end
#%option
#% key: dayto
#% type: integer
#% options: 1-365
#% answer: 365
#% description: Day to (1 - 365)
#% required : yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib


def main():   
    atempMapset = bboLib.atMapset
    atMeanPrefix = bboLib.atMeanPrefix
    atMaxPrefix = bboLib.atMaxPrefix

    targetMapset = bboLib.btMapset
    btMeanPrefix = bboLib.btMeanPrefix
    btMaxPrefix = bboLib.btMaxPrefix
    btEffPrefix = bboLib.btEffPrefix

    solarMapset = bboLib.solarMapset
    srPrefix = bboLib.srdayPrefix

    s50maskName = bboLib.forestS50Mask + "@" + bboLib.forestMapset

    mean_a1 = -0.173
    mean_a2 = 0.0008518
    mean_a3 = 1.054
    
    max_a1 = 1.656
    max_a2 = 0.002955
    max_a3 = 0.534
    max_a4 = 0.01884

    eff_a1 = -310.667
    eff_a2 = 9.603

    dayFrom = int(options["dayfrom"])
    dayTo = int(options["dayto"])

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    dayTo += 1
    for iDay in range(dayFrom, dayTo):
        grass.message("bark temperature day " + str(iDay))
        srName = bboLib.validateRaster(bboLib.rasterDayMapset(srPrefix,  iDay, solarMapset))
        atmeanName = bboLib.validateRaster(bboLib.rasterDayMapset(atMeanPrefix,  iDay, atempMapset))
        atmaxName = bboLib.validateRaster(bboLib.rasterDayMapset(atMaxPrefix, iDay, atempMapset))
        #
        meanName = bboLib.rasterDay(btMeanPrefix, iDay)
        maxName = bboLib.rasterDay(btMaxPrefix, iDay)
        effName = bboLib.rasterDay(btEffPrefix,  iDay)
        bboLib.deleteRaster(meanName)
        bboLib.deleteRaster(maxName)
        bboLib.deleteRaster(effName)

        if (srName != None and atmeanName != None and atmaxName != None):
            #grass.mapcalc("$output = $s50mask * ($a1 + ($a2 * $sol) + ($a3 * $atmean))", 
            #              output=meanName, s50mask=s50maskName,
            #              a1=mean_a1, a2=mean_a2, a3=mean_a3, sol=srName, atmean=atmeanName, overwrite=True)
            #grass.mapcalc("$output = $s50mask * ($a1 + ($a2 * $sol) + ($a3 * $atmax) + ($a4 * $atmean))",
            #              output=maxName, s50mask=s50maskName,
            #              a1=max_a1, a2=max_a2, a3=max_a3, a4=max_a4, sol=srName, atmax=atmaxName, atmean=atmeanName, overwrite=True)
            #grass.mapcalc("$output = ($a1 + $a2*$btmax) / 24.0",
            #              output=effName,
            #              a1=eff_a1, a2=eff_a2, btmax=maxName, overwrite=True)
            grass.mapcalc("$output = ($a1 + ($a2 * $sol) + ($a3 * $atmean))", 
                          output=meanName,
                          a1=mean_a1, a2=mean_a2, a3=mean_a3, sol=srName, atmean=atmeanName, overwrite=True)
            grass.mapcalc("$output = ($a1 + ($a2 * $sol) + ($a3 * $atmax) + ($a4 * $atmean))",
                          output=maxName,
                          a1=max_a1, a2=max_a2, a3=max_a3, a4=max_a4, sol=srName, atmax=atmaxName, atmean=atmeanName, overwrite=True)
            grass.mapcalc("$output = ($a1 + $a2*$btmax) / 24.0",
                          output=effName,
                          a1=eff_a1, a2=eff_a2, btmax=maxName, overwrite=True)

    # set history for site map
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
