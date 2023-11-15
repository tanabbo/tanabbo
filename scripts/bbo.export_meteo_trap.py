#!/usr/bin/env python
#
############################################################################
#
# MODULE:       bbo.export_meteo_trap
# AUTHOR(S):	Miroslav Blazenec, Rastislav Jakus, Milan Koren
# PURPOSE:      Calculates effective temperature
# COPYRIGHT:	This program is free software under the GNU General Public
#		License (>=v2). Read the file COPYING that comes with GRASS
#		for details.
#
#############################################################################

#%module
#% description: Export meteorological data for a trap
#% keywords: meteo data
#%end
#%option
#% key: idbbtrap
#% type: integer
#% answer: 1
#% options: 1-99
#% description: Trap ID
#% required: yes
#%end
#%option
#% key: dayfrom
#% type: integer
#% answer: 1
#% options: 1-365
#% description: Day from
#% required: yes
#%end
#%option
#% key: dayto
#% type: integer
#% answer: 365
#% options: 1-365
#% description: Day to
#% required: yes
#%end

import sys
import os
import grass.script as grass
import atexit
import string
sys.path.append(os.path.join(os.environ["GISBASE"], "scripts"))
import bboLib


def exportSeries(dayFrom, dayTo, idTrap, exportList, shpName):
    outLine = "day"
    for c in exportList:
        outLine = outLine + "," + c[2]
    grass.message(outLine)
    for iDay in range(dayFrom, dayTo + 1):
        outLine = str(iDay)
        for c in exportList:
            rasterName = bboLib.validateRaster(bboLib.rasterDayMapset(c[0], iDay, c[1]))
            if (rasterName != None):
                grass.run_command("v.what.rast", map=shpName, raster=rasterName, column="val", quiet=True)
                params = grass.parse_command("v.db.select", map=shpName, columns="val", where="cat={0}".format(idTrap), separator="=", flags="v")
                outLine = outLine + "," + str(round(float(params["val"].strip()),2))
            else:
                outLine = outLine + ",?"
        grass.message(outLine)


def main():
    dayFrom = int(options['dayfrom'])
    dayTo = int(options['dayto'])
    idTrap = int(options['idbbtrap'])

    targetMapset = bboLib.shpMapset
    bbTrapName = bboLib.shpBBTrap + "@" + bboLib.shpMapset

    if dayTo < dayFrom:
        grass.fatal(_("Parameter <dayfrom> must be less or equal than <dayto>"))

    userMapset = grass.gisenv()["MAPSET"]  
    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=targetMapset)

    params = grass.parse_command("v.db.select", map=bbTrapName, columns="val", where="cat={0}".format(idTrap), separator="=", flags="v")
    if (len(params) < 1):
        grass.fatal("Trap ID={0} does not exists".format(idTrap))

    # ["dem", "aspect", "slope"], "dem", ["dem", "aspect", "slope"]
    # ["_swarming", "_swarming_span", "_infestation"], "bb_infestation", ["swarming", "swarming_span", "infestation"]
       
    exportSeries(dayFrom, dayTo, idTrap, 
                 [(bboLib.srdayPrefix, bboLib.solarMapset, "sr"), 
                  (bboLib.atMaxPrefix, bboLib.atMapset, "at_max"), 
                  (bboLib.atMeanPrefix, bboLib.atMapset, "at_mean"),
                  (bboLib.btMaxPrefix, bboLib.btMapset, "bt_max"),
                  (bboLib.btMeanPrefix, bboLib.btMapset, "bt_mean"),
                  (bboLib.btEffPrefix, bboLib.btMapset, "bt_eff"),
                  (bboLib.infestationDDPrefix, bboLib.infestationMapset, "at_dd")
                 ], 
                 bbTrapName)     

    if not userMapset == targetMapset:
        grass.run_command("g.mapset", mapset=userMapset)
    grass.message(_("Done."))    


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
