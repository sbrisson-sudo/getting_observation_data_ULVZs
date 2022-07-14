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

import numpy as np
import matplotlib.pyplot as plt
from time import sleep

import os
import sys

import argparse 
import logging
from tqdm import tqdm

from obspy.core.event import read_events
from obspy.clients.fdsn import mass_downloader
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.mass_downloader.domain import GlobalDomain
from obspy.clients.fdsn.header import FDSNException


from station_inventory import MyInventory

# custom modules
sys.path.append('/home/sbrisson/documents/Geosciences/stage-BSL/tools/bsl_toolbox')

#-------------------------
# configuration

# data provider 

def initiate_client(client = "IRIS"):
    try:
        client_wf = Client("IRIS")
    except FDSNException:
        print(f"Unable to connect to client {client}, retrying in 5s.")
        sleep(5)
        initiate_client(client)


# time bounds (seconds)
tmin_after_event = 500.
tmax_after_event = 2500.

#-------------------------


def download_waveform_data(event,stations):
    """
    event : obspy event file
    stations : custom station inventory class instance
    """

    origin_time = event.preferred_origin().time

    # Location priorities:
    location_priorities = ("","00", "10", "01", "02")

    # Channel priorities
    channel_priorities = ("BH[ZNE12]", "LH[ZNE12]")

    # Mass downloader over IRIS
    # mdl = mass_downloader.MassDownloader( providers= ["IRIS"], configure_logging=False )
    mdl = mass_downloader.MassDownloader( providers= ["IRIS"])

    # Data directories
    stations_dir = "stations"
    wf_dir = "waveforms"

    print(f"Saving station metadata in directory {stations_dir} and waveforms in {wf_dir}")

    # Global domain (stations filtered to be inside directionnal domain)
    global_domain = GlobalDomain()

    # log to a file and not in stdout
    logger = logging.getLogger("obspy.clients.fdsn.mass_downloader")

    # remove console handler
    logger.removeHandler(logger.handlers[0])

    handler = logging.FileHandler('mass_downloader.log')
    logger.addHandler(handler) 

    # DOWNLOAD DATA

    # This loop might seem quite inefficient to you and it is. However, 
    # the MassDownloader does not always download all the data requested if the
    # list of stations is too large. Then, the user should re-run the MassDownloader
    # a couple of times. As an alternative, we here run it for each station.

    for nw_code,st_code in tqdm(zip(stations.stations["nw"],stations.stations["code"]), total=stations.len(),unit="station"):
        
        # print(f"Downloading data for station {nw_code:<2}.{st_code:<4} ({i/stations_in.len()*100:.0f}%).", end="\r")

        # set Restrictions
        restrictions = mass_downloader.Restrictions( 
            starttime   = origin_time +tmin_after_event,
            endtime     = origin_time +tmax_after_event,
            location_priorities = location_priorities,
            channel_priorities = channel_priorities,
            reject_channels_with_gaps = True,
            minimum_interstation_distance_in_m=1E2,
            network = nw_code, station = st_code 
            )
        # Start download
        mdl.download(
            global_domain, 
            restrictions, 
            mseed_storage = wf_dir, 
            stationxml_storage = stations_dir,
            print_report=False )

    print("Done.")


if __name__ == "__main__":
    
    # command line argument parser

    parser = argparse.ArgumentParser()

    parser.add_argument("-e",dest='event_file', type=str, help='obspy compatible event file')

    parser.add_argument("-r",dest='receivers_file', type=str, help='receivers.dat file')

    args = parser.parse_args()
    

    # read event information
    events = read_events(args.event_file)
    event = events[0]

    # read station information
    stations = MyInventory()
    stations.read_fromDat(args.receivers_file)

    # downlaod data

    download_waveform_data(event, stations)

    
        
