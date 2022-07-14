#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 2022
@author: Sylvain Brisson sylvain.brisson@ens.fr


Tools to use the obspy massdownloader
INPUTS : 
    - obspy event file
    - domain limits for station search

"""

from datetime import datetime
import os
import re
import subprocess


#-------------------------
# configuration

events_dir = "events_usgs_cmtslt"
mseed_data_dir = "mseed_data"
pkl_data_dir = "obspy_pkl_data"

out_fig_dir = "great_circles_figures"

event_id2_re = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<magnitude>\d\.\d)"

plot_file = "/home/gcl/BR/sbrisson/bsl_internship_toolbox/plotting/A3Dmodel_map_greatCircles.py"

#-------------------------

if __name__ == "__main__":

    for f in os.listdir(pkl_data_dir):

        search = re.search(event_id2_re, f)

        if not(search): continue 

        year = int(search["year"])
        month = int(search["month"])
        day = int(search["day"])

        date = datetime(year,month,day)

        mag = float(search["magnitude"])

        date_str2 = date.strftime("%d-%b-%Y")
        date_str3 = date.strftime("%Y-%m-%d")

        event_id = f"{mag:.1f}_{date_str2}"
        event_id2 = f"{date_str3}_{mag}"

        print(f"Plotting {event_id2}")

        event_file = os.path.join(events_dir, f"{event_id}.cmtsolution")
        receivers_file = os.path.join(mseed_data_dir, f"{event_id2}/receivers.dat")
        out_file = os.path.join(out_fig_dir, f"{event_id2}_map_GC.png")

        subprocess.call([plot_file, "--event", event_file, "--receivers",receivers_file,"-o",out_file,"--hotspots"])











