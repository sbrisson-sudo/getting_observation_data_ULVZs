#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 2022
@author: Sylvain Brisson sylvain.brisson@ens.fr



This read waveforms data under MSEED format and stations metadata under XML format 
into an obspy stream object and save it under a serialized (pickle) format
"""

import numpy as np
import matplotlib.pyplot as plt

import os
import sys

from datetime import datetime

import argparse

import obspy
from obspy import read, Stream
from obspy.core.event import read_events
from obspy.geodetics import gps2dist_azimuth,locations2degrees


#-------------------------
# configuration

stations_dir = "stations"
wf_dir = "waveforms"

sampling_rate = 10.0 # sr for interpolation

# corners periods for filtering (in seconds)
ifmin = 20.0
ifmax = 10.0

#-------------------------


def mseed2obspy_stream(event, out_file, verbose=False):
    """
    event : event obspy object
    out_file : output file name
    """

    origin = event.preferred_origin()

    # loading station metadata
    try:
        stations2 = obspy.read_inventory(stations_dir+"/*")
    except:
        print("Issue with reading stations metadata")
        return 
    print(f"{len(stations2)} stations.")

    # writting in a receivers.dat file
    out_file_stn_base = "receivers.dat"
    out_file_stn = out_file_stn_base
    n = 1
    while os.path.exists(out_file_stn):
        out_file_stn = f"{out_file_stn_base}.{n}"
        n += 1 

    if verbose: print(f"Writting stations metadata in {out_file_stn}")

    with open(out_file_stn, 'w') as out:
        header = ["Number of stations is:",len(stations2),"nw stn lat lon:"]
        out.writelines(f"{l}\n" for l in header)
        for nw in stations2:
            nw_code = nw.code
            for stn in nw:
                code = stn.code
                lat,lon = stn.latitude,stn.longitude
                out.write(f"{nw_code:<2} {code[:4]:<4} {lat:8.4f}  {lon:8.4f}\n")

    # Reading waveform data into a stream obspy object
    st = Stream()
    try:
        for waveform in os.listdir(wf_dir):
            st += read(os.path.join(wf_dir, waveform))
    except:
        print("Issue with reading waveform data")
        return 
    dist_list = []

    # computing aditionnal metadata
    for tr in st:
        
        st_coordinates = stations2.get_coordinates(tr.id)
        st_lat = st_coordinates["latitude"]
        st_lon = st_coordinates["longitude"]
        
        tr.stats.coordinates = st_coordinates
        
        tr.stats.evla = origin.latitude
        tr.stats.evlo = origin.longitude
        tr.stats.evde = origin.depth / 1000.
        tr.stats.event_origin_time = origin.time
                
        _,b_az,_ = gps2dist_azimuth(st_lat, st_lon, origin.latitude, origin.longitude)
        dist = locations2degrees(st_lat, st_lon, origin.latitude, origin.longitude)
        
        tr.stats.back_azimuth = b_az # for rotation
        tr.stats.distance = dist
        
        dist_list.append(dist)

    if verbose: print(f"Distances between {min(dist_list):.1f}° and {max(dist_list):.1f}°")

    # interpolating and triming
    if verbose: print("Interpolating...")
    st.interpolate(sampling_rate=sampling_rate)


    # rotating it
    if verbose: print("Rotating NE->RT...")
    stations3 = set([tr.stats.station for tr in st])
    st._trim_common_channels()

    for station in stations3:                       
        try:
            st.select(station=station).rotate('NE->RT')
        except ValueError:
            print(f"Couldn't rotate:\n{st.select(station=station)}")

    # filtering it
    if verbose: print("Filtering...")
    st.filter('bandpass', freqmin=1/ifmin, freqmax=1/ifmax)

    # saving it into serialized stream object (pickle format)
    if verbose: print(f">> Writting {out_file}")
    st.write(out_file, format='PICKLE')


if __name__ == "__main__":

    # command line argument parser

    parser = argparse.ArgumentParser()

    parser.add_argument("-e",dest='event_file', type=str, help='obspy compatible event file', required=True)

    parser.add_argument("-o",dest='out_file', type=str, help='output file name (without extension)', required=True)

    args = parser.parse_args()

    # read event information
    events = read_events(args.event_file)
    event = events[0]

    out_file = args.out_file + ".pkl"

    mseed2obspy_stream(event, out_file, verbose=True)




    