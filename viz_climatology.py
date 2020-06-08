
from quickcheck.utils import getCmap
import matplotlib.pyplot as plt
import numpy as np
import os



import seaborn as sbn
import pandas as pd


# -------------------------------------------------------------------------------------------------------
# define functions and classes
# -------------------------------------------------------------------------------------------------------

# make time series plot
class PlotTimeSeries:
    """  """

    def __init__(self, datacontainer,timeaggr=np.mean,cmap="prism"):


        self.datacontainer = datacontainer
        self.time = pd.date_range(datacontainer.timeDomain[0], datacontainer.timeDomain[1], freq="D")
        self.datasets = datacontainer.request.datasets
        self.start = self.time[0]
        self.end = self.time[-1]
        self.outDir = datacontainer.request.outDir

        self.colour = getCmap(len(self.datasets), name=cmap)

        self.timeaggr =timeaggr

    def plotSpatialAverage(self,figsize,title_fig = None, title_file = None,spataggr=np.mean,save_plot=False):
        self.title = title_fig

        self.plotted = None
        if self.plotted:
            for i in [self.ax1,self.ax2,self.ax3]:
                if i:
                    del i

        self.figSpatAverage = plt.figure(figsize = figsize)

        plt.suptitle(title_fig,fontsize=35)
        plt.subplots_adjust(bottom=0.15, top=0.95)

        # average

        for i,iDS in enumerate(self.datasets):
            df = self.datacontainer.predicted[iDS]  ##filter("[0-9]",axis=1).aggregate(np.mean,axis=1)
            dfAgg = df.drop(["time"], axis=1).apply(func=spataggr, axis=1).to_frame()
            dfAgg["time"] = self.datacontainer.predicted[iDS].time  # sttime
            dfAgg = dfAgg.set_index("time")
            self.plotDaily(self.figSpatAverage,dfAgg,self.colour(i),self.datasets[i])
            self.plotMonthly(self.figSpatAverage,dfAgg,self.colour(i),self.datasets[i])
            self.plotYear(self.figSpatAverage,dfAgg,self.colour(i),self.datasets[i])


        if save_plot:
            self.figSpatAverage.savefig(self.outDir + "/" + title_file + ".png",dpi=300)





    def plotSpatialAverageByGroups(self,groupby,figsize,title_fig = None, title_file = None,spataggr=np.mean,save_plot=False):
        self.title = title_fig


        self.plotted = None
        if self.plotted:
            for i in [self.ax1,self.ax2,self.ax3]:
                if i:
                    del i



        for group in np.unique(self.datacontainer.referenceSpatial[groupby].values):

            self.figSpatGroups = plt.figure(figsize=figsize)
            plt.suptitle(group,fontsize=35)
            plt.subplots_adjust(bottom=0.15, top=0.95)
            df = {}

            for i,iDS in enumerate(self.datasets):
                subs = ["time"] + self.datacontainer.referenceSpatial.loc[self.datacontainer.referenceSpatial[groupby] == group][
                    "name"].tolist()
                df[iDS] = self.datacontainer.predicted[iDS].filter(subs)
                dfAgg = df[iDS].drop(["time"], axis=1).apply(func=spataggr, axis=1).to_frame()
                dfAgg["time"] = self.datacontainer.predicted[iDS].time  # sttime
                dfAgg = dfAgg.set_index("time")
                self.plotDaily(self.figSpatGroups,dfAgg,self.colour(i),self.datasets[i])
                self.plotMonthly(self.figSpatGroups,dfAgg,self.colour(i),self.datasets[i])
                self.plotYear(self.figSpatGroups,dfAgg,self.colour(i),self.datasets[i])



            if save_plot:
                self.figSpatGroups.savefig(os.path.join(self.outDir, title_file +"_" + str(group) + ".png"),dpi=300)








    def plotDaily(self,fig,timeSeries,colour,label):



        self.ax1 = fig.add_subplot(3, 1, 1)

        self.ax1.set_xlim(self.start, self.end)
        self.ax1.plot(timeSeries, color=colour, label=label, linewidth=0.5)


        self.ax1.set_ylabel('Daily \n(mm)', multialignment='center',fontsize=25)

        self.ax1.grid(b=True, which='major', axis='y', color="k", linestyle='--',
                      linewidth=0.5)

        self.ax1.set_title(self.title)
        self.ax1.tick_params(labelsize=25)


    def plotMonthly(self,fig,timeSeries,colour,label):
        """

        """
        # PLOT MONTHLY

        # daily to monthly

        self.ts_monthly = timeSeries.resample("M",label="left").apply(self.timeaggr)

        self.ax2 = fig.add_subplot(3, 1, 2, sharex=self.ax1)

        self.ax2.plot(self.ts_monthly, color=colour, label=label, linewidth=2)

        # self.ax2.fill_between(self.dates, t, td, color='r')

        self.ax2.set_ylabel('Monthly \n(mm)', multialignment='center',fontsize=25)
        self.ax2.tick_params(labelsize=25)
        self.ax2.grid(b=True, which='major', axis='y', color="k", linestyle='--',
                      linewidth=0.5)

    def plotYear(self,fig,timeSeries,colour,label):
        """

        """
        # PLOT YEAR

        # aggregate to year

        self.ts_yearly = timeSeries.resample("A",label="left").apply(self.timeaggr)
        self.ax3 = fig.add_subplot(3, 1, 3, sharex=self.ax1)
        self.ax3.plot(self.ts_yearly, color=colour, label=label, linewidth=2)
        # self.ax3.legend(loc='upper center', bbox_to_anchor=(0.5, 1.22), ncol=5,prop={'size': 8})
        self.ax3.grid(b=True, which='major', axis='y', color="k", linestyle='--',
                      linewidth=0.6)
        # self.ax3.set_ylim(plot_range[0], plot_range[1], plot_range[2])
        self.ax3.tick_params(labelsize=25)
        # self.ax3.fill_between(self.dates, rh, self.ax3.get_ylim()[0], color='g')
        self.ax3.set_ylabel('Annual \n(mm)', multialignment='center',fontsize=25)
        self.ax3.set_xlabel("time",fontsize=25)
        self.ax3.legend(loc='lower center',
                   bbox_to_anchor=(0.5, -0.35), ncol=4, prop={'size': 20},markerscale=5,frameon=False)





class PlotHist():
    """  """

    def __init__(self,datacontainer,fig_size,aggr=np.sum):

        self.data = datacontainer.predicted.copy()
        self.gs_flag = datacontainer.request.groundStations
        self.outDir = datacontainer.request.outDir
        self.refSpatial = datacontainer.referenceSpatial

        if self.gs_flag:
            gsname = "reference"
            self.gs = datacontainer.reference[list(self.data)[0]]
            datacontainer.request.datasets.append(gsname)
            self.label = datacontainer.request.datasets
            self.data[gsname] = self.gs
        else:
            self.label = datacontainer.request.datasets

        self.fig_size = fig_size

        self.pltstations = None
        self.pltaverage  = None
        self.aggr = aggr

    def _calc_stations(self):

        df = []
        for iDS in self.label:
            d1 = self.data[iDS]

            #self.st_number = d1.shape[1]
            d1["month"] = d1.apply(lambda x: x.time.to_pydatetime().month, axis=1)
            d1 = d1.groupby("month").aggregate(self.aggr).reset_index("month")
            d1 = pd.melt(d1, id_vars=["month"], var_name="station")
            df.append(d1)

        d2 = pd.concat(df ,keys=self.label)
        self.df = d2.reset_index()

        #self.df.columns.name = ["source","count","month","station","rainfall"]

        return


    def plotSpatialAverageByGroups(self,groupby,title_fig = None, title_file = None,save_plot=False):


        self.groupby = groupby
        self.groubynames= np.unique(self.refSpatial[groupby].values)

        #d1= {}
        for group in self.groubynames:
            d2 = {}
            for iDS in self.label:

                subs = ["time"] + self.refSpatial.loc[self.refSpatial[self.groupby] ==group]["name"].tolist()
                d2[iDS] = self.data[iDS].filter(subs)
                d2[iDS]["month"] = d2[iDS].apply(lambda x: x.time.to_pydatetime().month, axis=1)

            d2 = pd.concat(d2, keys=self.label)
            d2.index.names = ["source", "idx"]
            d2 = d2.reset_index()
            del d2["idx"]
            d2 = d2.groupby(["month", "source"]).aggregate(self.aggr).reset_index("month")
            d2 = d2.reset_index()
            d3 = pd.melt(d2, id_vars=["month","source"], var_name=self.groupby)


            fig = plt.figure(figsize=self.fig_size)
            ax = fig.add_subplot(1, 1, 1)
            self.pltgroupby = sbn.barplot(data=d3 , x="month", y="value", hue="source", capsize=.2,ax =ax)
            plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0.,prop={'size': 20},markerscale=2,frameon=False)

            plt.suptitle(title_fig + "-" + str(group),fontsize=35)
            ax.tick_params(labelsize=20)

            if save_plot:

                self.figpltgroupby = self.pltgroupby.get_figure()
                self.figpltgroupby.savefig(os.path.join(self.outDir, title_file +"_" + str(group) + ".png"))



        return


    def plotEach(self,col_wrap):

        self._calc_stations()
        self.pltstations = sbn.catplot(data=self.df, x="month", y="value", hue="level_0", capsize=.2, kind="bar", col="station",
                                       col_wrap=col_wrap)
        self.figpltstations = self.pltstations.fig

    def plotSpatialAverage(self,title_fig = None, title_file = None,save_plot=False):
        self._calc_stations()
        fig = plt.figure(figsize=self.fig_size)
        ax = fig.add_subplot(1,1,1)
        self.pltaverage = sbn.barplot(data=self.df, x="month", y="value", hue="level_0", capsize=.2, ax = ax)
        plt.legend(bbox_to_anchor=(1.02, 1), loc=2, borderaxespad=0., prop={'size': 20}, markerscale=2, frameon=False)
        plt.suptitle(title_fig, fontsize=30)
        ax.tick_params(labelsize=20)


        if save_plot:
            self.figpltaverage = self.pltaverage.get_figure()
            self.figpltaverage.savefig(os.path.join(self.outDir, title_file + ".png"))




