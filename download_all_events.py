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
from genericpath import exists
import os,sys

from obspy.core.event import read_events

sys.path.append('/home/gcl/BR/sbrisson/getting_observation_data_ULVZs')

from station_inventory import MyInventory
from download_waveform_data import download_waveform_data
from mseed2obspy_stream import mseed2obspy_stream

#-------------------------
# configuration

in_file = "events_list_indonesia2africa_fe.txt"

events_dir = "events_usgs_cmtslt"
stations_dir = "stations_usgs_cmtslt"
mseed_data_dir = "mseed_data"
pkl_data_dir = "obspy_pkl_data"


#-------------------------

if __name__ == "__main__":


    cur_dir = os.path.dirname(os.path.abspath(__file__))
    
    with open(in_file, "r") as f:
        date_mag = f.readlines()

    for line in date_mag[1:]:

        os.chdir(cur_dir)

        # get event and receivers list file names

        date_str = line.split()[0]
        mag = float(line.split()[1])

        date = datetime.strptime(date_str, "%Y/%m/%d")
        date_str2 = date.strftime("%d-%b-%Y")
        date_str3 = date.strftime("%Y-%m-%d")

        event_id = f"{mag:.1f}_{date_str2}"
        event_id2 = f"{date_str3}_{mag}"

        print(f"Downloading data for event {event_id2}")

        event_filename = os.path.join(events_dir, f"{event_id}.cmtsolution")

        stations_filename = os.path.join(stations_dir, f"{event_id}_receivers.dat")

        # load metadata

        try:
            # read event information
            events = read_events(event_filename)
            event = events[0]

        except FileNotFoundError:
            print(f"Error, unable to open event file for event {event_id2}")
            continue

        try:
            # read station information
            stations = MyInventory()
            stations.read_fromDat(stations_filename)

        except FileNotFoundError:
            print(f"Error, unable to open station file for event {event_id2}")
            continue

        # change dir
        os.chdir(mseed_data_dir)
        if not(os.path.exists(event_id2)):
            os.mkdir(event_id2)
        os.chdir(event_id2)

        # dowload data
        download_waveform_data(event, stations)

        # get pickle file name
        pkl_filename = os.path.join(cur_dir, pkl_data_dir+f"/{event_id2}.pkl")

        # convert to obspy stream 
        mseed2obspy_stream(event, pkl_filename)







