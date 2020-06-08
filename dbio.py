import csv
import numpy as np
import pandas as pd
import geopandas as gpd
import glob
import os

def readFile4comparison(request,datacontainer,keepnan=False):
    """
    reads the dataset paths from a configuration file
    :param configFile:
    :param estimates: this is a list of datasets name.
    :param observation: this is the name of the observation dataset in the config file
    :return:
            sources_path: location of estimates
            obs_shp: geopandas dataframe
            obs_timeseries: pandas dataframe
            [start_est_time,end_est_time]: start and end  time  of the estimate datasets
            [start_st,end_st]: start and end time of observations
    """

    with open(request.configPath, 'r') as dest_f:
        data_iter = csv.reader(dest_f,
                               delimiter=',',
                               quotechar='"')
        data = [data for data in data_iter]

    data = np.asarray(data, dtype=str)
    # analysis time
    start_est_time = pd.to_datetime(data[(data[:, 0] == "analysis_time"),3],format="%d/%m/%Y").values[0]
    end_est_time = pd.to_datetime(data[(data[:, 0] == "analysis_time"), 4], format="%d/%m/%Y").values[0]

    sources_path = {}
    for ds in request.datasets:
        print(ds)
        sources_path[ds] = data[(data[:, 0] == ds), 13]

    if request.groundStations:
        # case where we have ground data as reference stored in a csv file
        # load shapefiles
        obs_dir = data[(data[:, 0] == request.reference), 13]
        obs_name = data[(data[:, 0] == request.reference), 0]
        obs_shp = gpd.read_file(os.path.join(obs_dir[0], obs_name[0] + ".shp"))
        # load timeseries
        obs_timeseries = pd.read_csv(os.path.join(obs_dir[0], obs_name[0] +  ".csv"))
    else:
        # case where we are using an extracted dataset as reference
        # load shapefiles
        obs_dir = data[(data[:, 0] == request.reference), 14]
        obs_name = data[(data[:, 0] == request.reference), 0]
        obs_shp = gpd.read_file(glob.glob(os.path.join(obs_dir[0], obs_name[0]) + "*_estimates.shp")[0])

        # load timeseries
        obs_timeseries = pd.read_csv(glob.glob(os.path.join(obs_dir[0], obs_name[0]) + "*_estimates.csv")[0])


    obs_timeseries.columns =  obs_timeseries.columns.str.lower()
    try:
        obs_timeseries["time"] = pd.to_datetime(obs_timeseries.time,format = "%d/%m/%Y %H:%M")
    except:
        pass
    try:
        obs_timeseries["time"] = pd.to_datetime(obs_timeseries.time, format="%Y-%m-%d %H:%M:%S")
    except:
        pass
    try:
        obs_timeseries["time"] = pd.to_datetime(obs_timeseries.time, format="%d/%m/%Y")
    except:
        pass
    start_st = obs_timeseries.time.values[0]
    end_st  = obs_timeseries.time.values[-1]

    es_ts_dict, gs_ts_dict = load_estimates(request.datasets,obs_timeseries,request.inDir,
                   request.analysisType,[start_est_time,end_est_time],[start_st,end_st],
                   request.reference,keepnan)

    res = datacontainer(predicted = es_ts_dict,reference=gs_ts_dict,referenceSpatial=obs_shp,
                        referenceTimeSeries=obs_timeseries,timeDomain=[start_est_time,end_est_time])

    res.request = request

    return res



def readFile4extraction(request,datacontainer):


    with open(request.configPath, 'r') as dest_f:
        data_iter = csv.reader(dest_f,
                               delimiter=',',
                               quotechar='"')
        data = [data for data in data_iter]

    data = np.asarray(data, dtype=str)

    sources_path = {}
    for ds in request.datasets:
        print(ds)
        sources_path[ds] = data[(data[:, 0] == ds), 13]

    observation_spatial = request.extract


    obs_dir = data[(data[:, 0] == observation_spatial), 13]
    obs_name = data[(data[:, 0] == observation_spatial), 0]
    obs_shp = gpd.read_file(os.path.join(obs_dir[0],obs_name[0])+".shp")

    res = datacontainer(sourcesPath=sources_path,referenceSpatial=obs_shp)

    res.request = request

    return res


def load_estimates(datasets,gs_ts,dir,analysis_type,analysis_time_domain,station_time_domain,reference,keepnan=True):
    """

    :param datasets:
    :param gs_ts:
    :param dir:
    :param analysis_type:
    :param analysis_time_domain:
    :param station_time_domain:
    :return:
    """
    gs_ts = gs_ts.set_index("time")
    if keepnan:
        gs_ts = gs_ts.resample("D").apply(lambda x: np.sum(x.values))
    else:
        gs_ts = gs_ts.resample("D").sum()

    gs_ts = gs_ts.reset_index()

    es_ts_dict = {}
    gs_ts_dict = {}
    deleted_datasets = []
    for iDS in datasets:
        print(f" ------ ")
        print(f"loading dataset {iDS}....")
        delete_dataset = False
        # load extracted estimates

        es_ts_path = glob.glob(os.path.join(dir, f"{iDS}_*.csv"))[0]

        es_ts = pd.read_csv(es_ts_path, parse_dates=["time"],index_col=['time'])
        if keepnan:
            es_ts = es_ts.resample("D").apply(lambda x: np.sum(x.values))
        else:
            es_ts = es_ts.resample("D").sum()
        es_ts = es_ts.reset_index()
        #es_ts["time"] = pd.DatetimeIndex(es_ts.time).normalize()

        # option focus on analysis domain: check if estimates and ground stations coincide
        if analysis_type == "analysis_domain":
            corrected_start_date = analysis_time_domain[0]
            corrected_end_date = analysis_time_domain[1]

            if analysis_time_domain[0] >= station_time_domain[0]:
                # analysis_time_domain[0] = station_time_domain[0]
                print("ground stations time series starts before start analysis time domain")
                print("... ok ...")
                # corrected_start_date = analysis_time_domain[0].copy()
            else:  # analysis_time_domain[0] < station_time_domain[0]:
                print("ground stations time series starts after start analysis time domain")
                print("... start analysis time is set to start ground station time")
                corrected_start_date = station_time_domain[0].copy()
            if analysis_time_domain[1] <= station_time_domain[1]:
                # analysis_time_domain[1] = station_time_domain[1]
                print("ground stations time series ends after end analysis time domain")
                print("... ok .. ")
                # corrected_end_date = analysis_time_domain[1].copy()
            else:  # analysis_time_domain[1] > station_time_domain[1]:
                print("ground stations time series ends before end analysis time domain")
                print("... end analysis time is set to end ground station time")
                corrected_end_date = station_time_domain[1].copy()
            # subset estimates and stations to analysis time
            try:
                es_ts_sub = es_ts[(es_ts.time >= corrected_start_date) & (es_ts.time <= corrected_end_date)]
                gs_ts_sub = gs_ts[(gs_ts.time >= corrected_start_date) & (gs_ts.time <= corrected_end_date)]

                if es_ts_sub.empty or gs_ts_sub.empty:
                    print(f"dataset {iDS} does not fall into time analysis domain")
                    print("...and will be deleted from analysis...")
                    delete_dataset = True
                    deleted_datasets.append(iDS)

            except:
                print(f"dataset {iDS} does not fall into time analysis domain")
                print("...and will be deleted from analysis...")
                delete_dataset = True
                deleted_datasets.append(iDS)

            if delete_dataset:
                pass
            else:
                es_ts_dict[iDS] = es_ts_sub
                gs_ts_dict[iDS] = gs_ts_sub
        # option focus on dataset coverage: check if estimates and ground stations coincide
        if analysis_type == "product_domain":
            print("analysis: product_domain")
            corrected_start_date = es_ts.time.values[0]
            corrected_end_date = es_ts.time.values[-1]

            if es_ts.time.values[0] >= station_time_domain[0]:
                # analysis_time_domain[0] = station_time_domain[0]
                print("ground stations time series starts before start estimate time")
                print("... ok ...")
                # corrected_start_date = analysis_time_domain[0].copy()
            else:  # analysis_time_domain[0] < station_time_domain[0]:
                print(f"ground stations time starts {station_time_domain[0]} after start estimate time {es_ts.time.values[0]}")
                print("... start estimate time series is set to start ground station time")
                corrected_start_date = station_time_domain[0].copy()
            if es_ts.time.values[-1] <= station_time_domain[1]:
                # analysis_time_domain[1] = station_time_domain[1]
                print("ground stations time series ends after end estimate time")
                print("... ok .. ")
                # corrected_end_date = analysis_time_domain[1].copy()
            else:  # analysis_time_domain[1] > station_time_domain[1]:
                print(f"ground stations time {station_time_domain[1]} ends before estimate time {es_ts.time.values[-1]}")
                print("... estimate time series end is set to end ground station time")
                corrected_end_date = station_time_domain[1].copy()
            # subset estimates and stations to analysis time
            try:
                es_ts_sub = es_ts[(es_ts.time >= corrected_start_date) & (es_ts.time <= corrected_end_date)]
                gs_ts_sub = gs_ts[(gs_ts.time >= corrected_start_date) & (gs_ts.time <= corrected_end_date)]

                if es_ts_sub.empty or gs_ts_sub.empty:
                    print(f"dataset {iDS} does not fall into time dataset domain")
                    print("...and will be deleted from analysis...")
                    delete_dataset = True
                    deleted_datasets.append(iDS)

            except:
                print(f"dataset {iDS} does not fall into time dataset domain")
                print("...and will be deleted from analysis...")
                delete_dataset = True
                deleted_datasets.append(iDS)

            if delete_dataset:
                pass
            else:
                es_ts_dict[iDS] = es_ts_sub
                gs_ts_dict[iDS] = gs_ts_sub
        print(f" ------ ")

    print(f"dataset discarded: {deleted_datasets}")

    # TODO: any pre-processing will be done in another script

    remove = "no" #input("delete dataset? yes/no")
    if remove == 'yes':
        datasets = [i for i in datasets if i not in deleted_datasets]
    else:
        pass
    return es_ts_dict,gs_ts_dict
