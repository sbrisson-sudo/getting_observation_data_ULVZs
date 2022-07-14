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

out_fig_dir = "wf_figures"

event_id2_re = r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<magnitude>\d\.\d)"

# plot_file = "/home/gcl/BR/sbrisson/bsl_internship_toolbox/plotting/waveforms_recordSection_azimuth_colored.py"

plot_file = "/home/gcl/BR/sbrisson/bsl_internship_toolbox/plotting/waveforms_recordSection_azimuth.py"

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
        event_id2 = f"{date_str3}_{mag:.1f}"

        print(f"Plotting {event_id2}")

        wf_file = os.path.join(pkl_data_dir, f"{event_id2}.pkl")
    
        out_file_S = os.path.join(out_fig_dir, f"{event_id2}_wf_S.png")
        out_file_sS = os.path.join(out_fig_dir, f"{event_id2}_wf_sS.png")

        # ~/bsl_internship_toolbox/plotting/waveforms_recordSection_azimuth_colored.py ${WF_FILE} -c T --phase-ref S Sdiff --phases S --norm trace --event-metadata -o ${OUT_PREFIX}.waveforms.png -az -130 -108 -t -20 130

        subprocess.call([plot_file, wf_file, "-c", "T", "--phase-ref","S", "Sdiff", "--norm", "trace", "--event-metadata", "-t", "-20", "100" ,"--phases", "S", "Sdiff", "sS", "sSdiff", "-o", out_file_S, "-s", "5"])
        # subprocess.call([plot_file, wf_file, "-c T --phase-ref S Sdiff --norm trace --event-metadata -t -20 100 --phases S Sdiff -o", out_file_sS])











