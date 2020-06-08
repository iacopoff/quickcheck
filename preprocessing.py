import xarray as xr
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import os
import glob
# create domain

#keep in memory


# extract datasets




class Load():
    """
    document the scope of the class
    """

    def __init__(self, *args):
        """
        parameters:
        satellite = path to the netcdf input; string
        variable = the variable of interest; string
        ground stations
        """
        print(f"--- initialise {args[3]} ---")
        self.satellite = xr.open_dataset(args[0], mask_and_scale=True)
        self.lat = self.search(list(self.satellite.variables.keys()), "lat")[0]
        self.lon = self.search(list(self.satellite.variables.keys()), "lon")[0]
        if self.lat == "lat":
            self.satellite.rename({"lat": "latitude", "lon": "longitude"}, inplace=True)
            self.lat = "latitude"
            self.lon = "longitude"
        self.satellite = self.satellite[args[1]]
        self.gs = args[2]

    def _extract_coordinates(self):
        self.x = self.gs.geometry.x
        self.y = self.gs.geometry.y
        self.name = self.gs.name
        self.time = pd.to_datetime(self.satellite.time.values)

    def search(self,x, f):
        return ([s for s in x if f in s])

    def extract(self):
        print("extracting...")
        self._extract_coordinates()
        self.dc = {}
        for n,(x,y) in enumerate(zip(self.gs.geometry.x,self.gs.geometry.y)):
            self.dc[n] = self.satellite.sel(latitude=y, longitude=x, method="nearest").values
            if np.all(np.isnan(self.dc[n])) is True or np.all(np.isnan(self.dc[n])) is None:
                print("extracting point outside the domain: nan array returned")

        self.df = pd.DataFrame(self.dc)
        self.df.columns = self.name
        self.df["time"] = self.time

    def set_parameters(self,*args):
        self.var_time_name = args[0]
        self.out_dir = args[1]


    def save_extracted(self, shp_output_name, csv_output_name):
        print(f"saving...to {self.out_dir}")
        #self.gs.columns = ["name", "geometry"]
        #self.gs["name"] = self.gs["name"].apply(str)
        self.gs.to_file(os.path.join(self.out_dir, shp_output_name), driver='ESRI Shapefile')
        self.df.to_csv(os.path.join(self.out_dir, csv_output_name), index=False)







def extraction(datacontainer):
    c = 0
    for iDS in datacontainer.request.datasets:
        print(f"processing dataset {glob.glob(os.path.join(datacontainer.sourcesPath[iDS][0],iDS+'*.nc'))[0]}")
        estimates = Load(glob.glob(os.path.join(datacontainer.sourcesPath[iDS][0], f"{iDS}*.nc"))[0], datacontainer.request.extractVar[c],
                         datacontainer.referenceSpatial, iDS)

        # load datasets

        # check satellite/dataset info for example the time variable name
        print(estimates.satellite)

        # set time variable name and output path, pixel resolution
        estimates.set_parameters("time",
                                 datacontainer.request.outDir)

        # extract pixels
        # the argument is a threshold, if the station is within that threshold then
        # the neighbour pixel is also sampled and the average is computed
        estimates.extract()

        # save extracted
        estimates.save_extracted(f"{iDS}_{datacontainer.request.extract}_estimates.shp", f"{iDS}_{datacontainer.request.extract}_estimates.csv")

        c += 1

    print("done")
