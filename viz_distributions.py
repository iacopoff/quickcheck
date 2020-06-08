import os
import gdal

import numpy as np

from matplotlib import gridspec
from matplotlib import cm

import matplotlib

import matplotlib.pyplot as plt







class compareDistribution:

    def __init__(self, datacontainer=None,timeaggr=None,removenan=True):

        """

        :param datacontainer:
        :param timeaggr:
        :param removenan:   True, NaNs are removed from the predicted and reference datasets so that to compare points
                            only where there is data in both. This has sense only when the time series is not resampled.
                            Otherwise the NaNs are handled by the policy of the timeaggr function.
        """

        self.datacontainer = datacontainer
        self.predicted = datacontainer.predicted
        self.reference = datacontainer.reference
        self.timeaggr = timeaggr
        self.label = datacontainer.request.datasets
        self.thres = datacontainer.request.threshold
        self.resolution = datacontainer.request.resolution
        self.outDir = datacontainer.request.outDir
        self.removenan = removenan

    def _calc(self):

        if self.datacontainer.request.resolution == 'monthly':
            self.predCalc = {}
            self.refCalc = {}
            for iDS in self.label:

                pred = self.predicted[iDS].set_index("time")
                ref = self.reference[iDS].set_index("time")

                pred = pred.resample("M").aggregate(self.timeaggr)
                ref = ref.resample("M").aggregate(self.timeaggr)


                flatPred = np.ndarray.flatten(pred.reset_index(drop=True).values)
                flatRef = np.ndarray.flatten(ref.reset_index(drop=True).values)

                if self.removenan:
                    notnan = np.argwhere((np.isnan(flatPred) == False) & (np.isnan(flatRef) == False))
                    # subset not nan values
                    flatRef = flatRef[notnan[:, 0]]
                    flatPred = flatPred[notnan[:, 0]]


                self.refCalc[iDS] = flatRef
                self.predCalc[iDS] = flatPred


                #
                # self.refCalc[iDS] = np.ndarray.flatten(pred.reset_index(drop=True).values)
                # self.predCalc[iDS] = np.ndarray.flatten(ref.reset_index(drop=True).values)

        elif self.datacontainer.request.resolution == 'annual':

            self.predCalc = {}
            self.refCalc = {}
            for iDS in self.label:

                pred = self.predicted[iDS].set_index("time")
                ref = self.reference[iDS].set_index("time")

                pred = pred.resample("A").aggregate(self.timeaggr)
                ref = ref.resample("A").aggregate(self.timeaggr)

                flatPred = np.ndarray.flatten(pred.reset_index(drop=True).values)
                flatRef = np.ndarray.flatten(ref.reset_index(drop=True).values)

                if self.removenan:
                    notnan = np.argwhere((np.isnan(flatPred) == False) & (np.isnan(flatRef) == False))
                    # subset not nan values
                    flatRef = flatRef[notnan[:, 0]]
                    flatPred = flatPred[notnan[:, 0]]


                self.refCalc[iDS] = flatRef
                self.predCalc[iDS] = flatPred



        elif self.datacontainer.request.resolution == 'daily':
            self.predCalc = {}
            self.refCalc = {}
            for iDS in self.label:

                pred = self.predicted[iDS].set_index("time")
                ref = self.reference[iDS].set_index("time")

                flatPred = np.ndarray.flatten(pred.reset_index(drop=True).values)
                flatRef = np.ndarray.flatten(ref.reset_index(drop=True).values)



                # mask not nan values
                if self.removenan:
                    notnan = np.argwhere((np.isnan(flatPred) == False) & (np.isnan(flatRef) == False))
                    # subset not nan values
                    flatRef = flatRef[notnan[:, 0]]
                    flatPred = flatPred[notnan[:, 0]]


                self.refCalc[iDS] = flatRef
                self.predCalc[iDS] = flatPred






    def applyObjectiveFunction(self,func,**kwargs):


        self._calc()

        out = {}
        for iDS in self.label:

            pred = self.predCalc[iDS]
            ref  = self.refCalc[iDS]

            tref = ref[ref > self.thres]
            tpred = pred[pred > self.thres]

            res = func(tpred,tref,**kwargs)

            out[iDS] = res

        return out



    def plotDistribution(self,figsize, title_file = None, logy =True,
                         normalise=False,save_plot=False):
        # TODO: add metrics on the plot


        self._calc()

        for iDS in self.label:

            pred = self.predCalc[iDS]
            ref  = self.refCalc[iDS]

            tref = ref[ref > self.thres]
            tpred = pred[pred > self.thres]


            if normalise:
                tref = (tref- np.nanmin(tref)) / (np.nanmax(tref) - np.nanmin(tref))
                tpred = (tpred  - np.nanmin(tpred )) / (np.nanmax(tpred ) - np.nanmin(tpred))
            else:
                pass

            if self.resolution == "monthly":
                ind = range(0, np.nanmax([ref , pred ]).astype("int") + 10, 10)
            else:
                ind = range(0, np.nanmax([ref, pred]).astype("int") + 10, 2)

            href, binRef = np.histogram(tref, ind)
            hpred, binPred = np.histogram(tpred , ind)


            nameRef = self.datacontainer.request.reference

            fig = plt.figure(figsize=figsize)
            gs = gridspec.GridSpec(2, 2)
            ax1 = plt.subplot(gs[0])
            ax1.hist(tref, binRef, alpha=0.5, label=nameRef , color="green")
            ax1.hist(tpred , binPred , alpha=0.5, label=iDS, color="red")
            ax1.legend( loc='lower center',
                        bbox_to_anchor=(0.3, 1),
                        prop={'size': 12}, markerscale=1, frameon=False)
            ax1.tick_params(labelsize=12)
            #ax1.legend(loc='upper right')

            if logy:
                add_to_title = "logy"
                plt.yscale('log', nonposy='clip')
                plt.ylabel("counts (log-scale)",fontsize=16)
            else:
                plt.ylabel("counts",fontsize=16)
            #plt.title("rainfall event distribution")

            ax2 = plt.subplot(gs[2])
            if self.resolution == "monthly":
                ax2.bar(binPred[:-1], hpred * np.round(binPred[:-1], 3), width=10, alpha=0.5, color="red", label=iDS)
                ax2.bar(binRef[:-1], href * np.round(binRef[:-1], 3), width=10, alpha=0.5, color="green", label=nameRef)
            else:
                ax2.bar(binPred[:-1],hpred * np.round(binPred[:-1], 3), width=2, alpha=0.5, color="red", label=iDS)
                ax2.bar(binRef[:-1],href * np.round(binRef[:-1], 3), width=2, alpha=0.5, color="green", label=nameRef)


            ax2.tick_params(labelsize=12)
            plt.xlabel("event bins (mm)",fontsize=16)


            if logy:
                plt.yscale('log', nonposy='clip')
                plt.ylabel("volume per event (mm) (log-scale)")
            else:
                plt.ylabel("volume per event (mm)")


            # second plot
            ax3 = plt.subplot(gs[1])
            h = ax3.hist2d(ref, pred, bins=200, cmap=matplotlib.cm.gist_rainbow, norm=matplotlib.colors.LogNorm())
            plt.colorbar(h[3], ax=ax3)
            # ax3.scatter(obs,sim,marker=".",alpha=0.4,color="blue",s=3.2)
            ax3.set_xlabel(f"{nameRef} mm",fontsize=16)
            ax3.set_ylabel(f"{iDS} mm",fontsize=16)
            ax3.plot(ref, 1 * ref, 'black', label='perfect fit', linewidth=0.8, linestyle="--")
            ax3.legend(loc='upper right')
            ax3.tick_params(labelsize=12)
            plt.xlim(0, np.nanmax([ref, pred]))
            plt.ylim(0, np.nanmax([ref, pred]))
            plt.title("datasets correlation")

            ax4 = plt.subplot(gs[3])
            ax4.scatter(ref, pred - ref, marker=".", alpha=0.4, color="blue", s=3.2, label="residuals")
            ax4.axhline(y=0, linewidth=0.8, linestyle="--", color="black")
            ax4.set_xlabel(f"{nameRef} (mm)",fontsize=16)
            ax4.set_ylabel(f"residuals (mm)",fontsize=16)
            ax4.legend(loc='upper right')
            ax4.tick_params(labelsize=12)

            thres = self.thres
            plt.suptitle(f"{iDS} - {nameRef} \n threshold: {thres} mm",
                         fontsize=17,x=0.58,y=1)
            #plt.tight_layout()
            fig.subplots_adjust(top=0.93, bottom = 0.1,wspace=0.2 , hspace=0.2,left = 0.1)


            if save_plot:
                res = self.resolution
                if logy:
                    fig.savefig(self.outDir + f"/{iDS}_{title_file}_{add_to_title}_{res}.png", bbox_inches='tight')
                else:
                    fig.savefig(self.outDir + f"/{iDS}_{title_file}_{res}.png", bbox_inches='tight')
    #
