import xarray
import numpy as np
import csv
import pandas as pd
import numpy as np
import geopandas as gpd
import os
import glob
import matplotlib.pyplot as plt
from itertools import product
from shapely.geometry import Point

# method to return a sequence of a given length and step
def arange(start, step, count):
    return np.arange(start, start + (step * count), step)

def createRegularGrid(data,latitude = "lat",longitude="lon",res =0.25,grid_value = "center"):
    """
    :param data: xarray.DataArray
    :return:
    """
    latmin, latmax , lonmin, lonmax = data[latitude].values[0],data[latitude].values[-1],data[longitude].values[0],data[longitude].values[-1]


    if grid_value == "center":
        x = arange(lonmin,res,(lonmax-lonmin)/res +1 )
        y = arange(latmin,res,(latmax-latmin)/res +1)
    elif grid_value == "bottom_left_corner":
        pixel_center = res / 2
        x = arange(lonmin + pixel_center ,res,(lonmax-lonmin)/res +1 )
        y = arange(latmin + pixel_center ,res,(latmax-latmin)/res +1 )

    geometry = [Point(p) for p in product(x,y)]
    crs = {'init': 'epsg:4326'}
    gdf = gpd.GeoDataFrame(pd.DataFrame({"id":range(len(geometry ))}), crs=crs, geometry=geometry)

    return gdf


def getCmap(n, name='prism'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)