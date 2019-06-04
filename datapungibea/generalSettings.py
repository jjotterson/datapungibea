'''
  .generalSettings
  ~~~~~~~~~~~~~~~~~
  Loads general information: metadata of the datasource, metadata of the package's 
  database drives (methods connecting to the databases of the datasource), 
  and the datasource url and user api key.
'''

from . import utils

class getGeneralSettings(): #TODO: write as a mixin
    def __init__(self,connectionParameters={},userSettings={}):
        ''' 
         sessionParameters  - API key and the url (most used) of the datasource
           entry should look like:
           {'key': 'your key', 'description': 'BEA data', 'address': 'https://apps.bea.gov/api/data/'}
         userSettings - containg things like the path to api keys, preferred output format (json vs xml)
         datasourceOverview - a quick description of the datasource and its license
         packageMetadata - basic info on the package - to be used in a GUI or catalog of 
            methods that read data.  Also, "databases" will get automaticall updated with
            info on the methods that get specific dataset from the datasource.  A typical 
            entry should look like:
            {
                 "displayName":"List of Datasets",
                 "method"     :"datasetlist",   #NOTE run with getattr(data,'datasetlist')()
                 "params"     :{},              #No parameters in this case.
            }
        '''
        
        #Load, for example, API Key and the (most used) path to the datasource
        self.userSettings         = utils.getUserSettings(userSettings=userSettings)
        self.connectionParameters = utils.getConnectionParameters(connectionParameters,userSettings)
        self.baseRequest          = getBaseRequest(self.connectionParameters,self.userSettings)
        self.datasourceOverview   = getDatasourceOverview()
        self.packageMetadata      = getPackageMetadata()
               
            
def getBaseRequest(connectionParameters={},userSettings={}):
    '''
      translate the connection parameters, a flat dictionary, to the format used by 
      requests (or other connector), also, translate names to ones used by the datasource.        
    '''   
    if userSettings == {}:
        userSettings = dict(ResultFormat = 'JSON')
        print("result format was set to JSON since none could be found or was passed as a 'ResultFormat' in userSettings")
    
    output = { #this is, for example, the base of a requests' request - the drivers add to this.
       'url' : connectionParameters['url'],
       'params' :{
         'UserID' : connectionParameters['key'],
         'ResultFormat': userSettings["ResultFormat"]
       }
    }
    
    return(output)

def getDatasourceOverview():
    output = '''
         Userguides:
          https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf
          https://www.bea.gov/tools/   or  https://apps.bea.gov/API/signup/index.cfm
         
          Basically, there are three types of meta: 
            (1) GETDATASETLIST      top level, get the name of all tables.  
            (2) GetParameterList    given a table, what parameters it needs to download (eg. NIPA)
            (3) GetParameterValues  given a parameter of a table, which values you can choose. (eg. TableID)
         
         Sample python code (getting the list of datasets):
         
            import requests 
            payload = {
                'UserID':  ENTER YOUR BEA API Key Here, 
                'method': 'GETDATASETLIST',
                'ResultFormat': "JSON"
            }
            beaDatasets = requests.get( 'https://apps.bea.gov/api/data/', params = payload )
        
         Licenses (always check with the data provider):
            Data used is sourced from the Bureau of Economic Analysis 
            As stated on the Bureau of Economic Analysis website: 
            - Unless stated otherwise, information published on this site is in the public 
               domain and may be used or reproduced without specific permission. 
            - As a U.S. government agency, BEA does not endorse or recommend any 
              commercial products or services.                                            
            - Any reference or link to the BEA Web site must not contain information 
              that suggests an endorsement or recommendation by BEA.                  
            For more information, see: 
             https://www.bea.gov/help/guidelines-for-citing-bea  
        '''   
    
    return(output)

def getPackageMetadata():
    output = {
        "name":             "datapungibea",
        "loadPackageAs" :   "dpbea",
        "apiClass":         "data",
        "displayName":      "BEA",
        "description":      "Acess data from Bureau of Economic Analysis (BEA)",
        "databases":        [
            {
             "displayName":"List of Datasets",
             "method"     :"datasetlist",   #NOTE run with getattr(data,'datasetlist')()
             "params"     :{},
            },
            {
             "displayName":"NIPA",
             "method"     :"NIPA",   #NOTE run with getattr(data,'datasetlist')()
             "params"     :{'Year':'X','Frequency':'Q'}, #Parameters and default options.
            },
            ],
     }  
    
    return(output)



'''


                {
                 "displayName":"NIPA",
                 "method"     :"NIPA",   #NOTE run with getattr(data,'datasetlist')()
                 "params"     :{'Year':'X','Frequency':'Q'}, #Parameters and default options.
                },
             ],
        }
'''