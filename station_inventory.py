#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 2022
@author: Sylvain Brisson sylvain.brisson@ens.fr
"""

# imports

import pandas as pd

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import shapely.geometry as sgeom

# to have better defined great circles
# https://stackoverflow.com/questions/40270990/cartopy-higher-resolution-for-great-circle-distance-line
class LowerThresholdOthographic(ccrs.Orthographic):
    @property
    def threshold(self):
        return 1e3

class MyStation:
    def __init__(self, code, nw, lat, lon):
        self.code= code
        self.nw  = nw
        self.lat = lat
        self.lon = lon
        
class MyInventory:
    
    def __init__(self, in_file = False):
        self.stations = pd.DataFrame({'code':[],'nw':[],'lat':[],'lon':[]})
        if in_file:
            self.read_fromDat(in_file)
        
    def append(self, station):
        self.stations.loc[len(self.stations.index)] = [station.code, station.nw, station.lat, station.lon]
        
    def plot(self):
                
        fig = plt.figure(figsize=(6,6))
        ax = plt.axes(projection=ccrs.PlateCarree())
        # ax.add_feature(cfeature.LAND)
        # ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.scatter(self.stations["lon"],self.stations["lat"], transform = ccrs.PlateCarree(), marker="v", ec="k", s = 100, label=self.stations["nw"])
        
        extent = ax.get_extent()
        ax.stock_img()
        ax.set_extent(extent, crs=ccrs.PlateCarree())


        # add box with orthographic projection
        meanLon = (extent[0]+extent[1])/2
        meanLat = (extent[2]+extent[3])/2
        sub_ax = fig.add_axes([0.65, 0.65, 0.2, 0.2],projection=LowerThresholdOthographic(central_latitude=meanLat, central_longitude=meanLon))
        sub_ax.add_feature(cfeature.LAND)
        sub_ax.add_feature(cfeature.OCEAN)

        print(extent)
        extent_box = sgeom.box(extent[0], extent[2], extent[1], extent[3])
        sub_ax.add_geometries([extent_box], ccrs.PlateCarree(), facecolor='none', edgecolor='blue', linewidth=2)
        
    def __repr__(self):
        return self.stations.__repr__()
    def len(self):
        return self.stations.shape[0]
    def nb_networks(self):
        return self.stations["nw"].drop_duplicates().shape[0]
    
    def write(self, out_file = "receivers.dat"):
        """Write to receivers.dat file"""
        f = open(out_file, 'w')
        f.write(f"Nombre de stations:\n{len(self.stations.index)}\nnw stn lat lon:\n")
        for index, row in self.stations.iterrows():

            # pad station and network codes  with underscores
            code_stn = row['code'] + "_"*(5-len(row['code']))
            code_nw = row['nw'] + "_"*(2-len(row['nw']))

            f.write(f"{code_nw} {code_stn} {row['lat']:2.4f} {row['lon']:2.4f}\n")
        f.close()

    def read_fromDat(self, in_file="receivers.dat"):

        df = pd.read_csv(in_file, header = 2, sep = "\s+")

        df.rename(columns = {'stn':'code', 'lon:':'lon'}, inplace = True) 
        self.stations = df

        df["code"] = [code.replace("_","") for code in df["code"]]   
        df["nw"] = [code.replace("_","") for code in df["nw"]]   

if __name__ == "__main__":

    in_file = "test_data/receivers.dat"
    out_file = "test_data/receivers.dat.out"
    check_out_file = "test_data/receivers.csv"

    stations = MyInventory(in_file)

    print(stations)
    stations.plot()
    plt.show()

    stations.stations.to_csv(check_out_file)

    stations.write(out_file)
    