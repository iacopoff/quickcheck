



class RequestData:

    def __init__(self,configPath = " ",inDir = " ",outDir= " ",datasets= [],groundStations= False,
                 reference = " ",analysisType = " ",extract =" ",extractVar = [],resolution=None,threshold=None):
        self._configPath = configPath
        self._inDir = inDir
        self._outDir = outDir
        self._datasets = datasets
        self._groundStations = groundStations
        self._reference = reference
        self._analysisType = analysisType
        self._extract = extract
        self._extractVar = extractVar
        self._resolution = resolution
        self._threshold = threshold


    @property
    def extractVar(self):
        return self._extractVar

    @extractVar.setter
    def extractVar(self,value):
        self._extractVar = value

    @property
    def extract(self):
        return self._extract

    @extract.setter
    def extract(self,value):
        self._extract = value


    @property
    def configPath(self):
        return self._configPath

    @configPath.setter
    def configPath(self,value):
        self._configPath = value


    @property
    def inDir(self):
        return self._inDir

    @inDir.setter
    def inDir(self,value):
        if isinstance(value,str):
            self._inDir = value
            print("Setting value")
        else:
            raise ValueError(f"accepted type str not {type(value)}")
            print("Setting value")



    @property
    def outDir(self):
        return self._outDir

    @outDir.setter
    def outDir(self,value):
        self._outDir = value

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self,value):
        self._reference = value

    @property
    def datasets(self):
        return self._datasets

    @datasets.setter
    def datasets(self,value):
        self._datasets = value

    @property
    def groundStations(self):
        return self._groundStations

    @groundStations.setter
    def groundStations(self,value):
        self._groundStations = value

    @property
    def analysisType(self):
        return self._analysisType

    @analysisType.setter
    def analysisType(self,value):
        self._analysisType = value

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self,value):
        self._resolution = value

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self,value):
        self._threshold = value

