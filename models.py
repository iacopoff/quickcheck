

class DataContainer:
    """

    """
    def __init__(self,sourcesPath=" ",predicted= " ",reference=" ",referenceSpatial= " ",referenceTimeSeries= " ",
                 timeDomain=" "):
        self.sourcesPath = sourcesPath
        self.predicted = predicted
        self.reference = reference
        self.referenceSpatial = referenceSpatial
        self.referenceTimeSeries = referenceTimeSeries
        self.timeDomain = timeDomain





    def describe(self):
        print("--- describe internal objects ---")
        print(f'predicted: \n')
        self.out = {}
        for pred in self.predicted:
            self.out[pred] = str(self.predicted[pred].describe())
            print('{} : \n {} \n'.format(pred,self.out[pred]))

        print(f'reference: \n')
        self.outRef = {}
        for ref in self.reference:
            self.outRef[ref] = str(self.reference[ref].describe())
            print('{} : \n {} \n'.format(ref,self.outRef[ref]))

    def info(self):
        print('--- info internal objects ---')
        print(f'predicted: \n')
        self.infoPred = {}
        for pred in self.predicted:
            self.infoPred[pred] = str(self.predicted[pred].info())
            print('{} : \n {} \n'.format(pred,self.infoPred[pred]))

        print(f'reference: \n')
        self.infoRef= {}
        for ref in self.reference:
            self.infoRef[ref] = str(self.reference[ref].info())
            print('{} : \n {} \n'.format(ref,self.infoRef[ref]))



    def __getitem__(self,param_id):
        pass

    def __setitem__(self,):
        pass


