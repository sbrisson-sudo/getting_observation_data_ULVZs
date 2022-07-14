#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 2022
@author: Sylvain Brisson sylvain.brisson@ens.fr
"""

import numpy as np
import matplotlib.pyplot as plt

import os
import sys

from datetime import datetime




# obspy imports
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException

# custom modules
sys.path.append('/home/sbrisson/documents/Geosciences/stage-BSL/tools/bsl_toolbox')

# global cmt request
from data_acquisition.globalcmt_request import GlobalCMT_search



#-------------------------
# configuration

# date of event, format : YYYY/MM/DD
date = "2011/08/30"

# minimum/maximum magnitude
Mw_min = 6.0
Mw_max = 7.0


def get_events_usgs(date, Mw_min, Mw_max):
    """Return all the events matching the conditions in the USGS catalog.

    Args:
        date (string): date of event, YYYY/MM/DD
        Mw_min (float)
        Mw_max (float)
    """
    
    client_cmt = Client("USGS")

    nb_sec = 24*60*60
    
    try:
        events_usgs = client_cmt.get_events(
            starttime   = date,
            endtime     = date + nb_sec, 
            minmagnitude= Mw_min,
            maxmagnitude= Mw_max,
            includeallorigins=True
            )
        print(">> USGS catalogue")
        print(events_usgs)
        
    except FDSNNoDataException:
        print(">> No matching event in USGS catalogue")
        return []
    
    
def get_events_gcmt(date, Mw_min, Mw_max):
    """Return all the events matching the conditions in the USGS catalog.

    Args:
        date (string): date of event, YYYY/MM/DD
        Mw_min (float)
        Mw_max (float)
    """
    
    gcmt = GlobalCMT_search(
        date = datetime.strptime(date, '%Y/%m/%d'),
        Mw_min = 6.2,
    )     
    events_gcmt = gcmt.get_cmt_solution()
    
    if len(events_gcmt) != 0:
        print(">> Global CMT catalogue")
        print(events_gcmt)
    else:
        print(">> No matching event in USGS catalogue")
        

if __name__ == "__main__":
    
    # 1. get events
    
    events_usgs = get_events_usgs(date, Mw_min, Mw_max)
    events_gcmt = get_events_gcmt(date, Mw_min, Mw_max)
    
    if len(events_gcmt) == 0 and len(events_usgs) == 0:
        print("ERROR : no events found, exiting...")
        exit()
        
    # 2. Choosing event
    
    
    
    
    
    pass