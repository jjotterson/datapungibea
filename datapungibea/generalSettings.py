'''
  .generalSettings
  ~~~~~~~~~~~~~~~~~
  Loads general information: metadata of the datasource, metadata of the package's 
  database drives (methods connecting to the databases of the datasource), 
  and the datasource url and user api key.
'''

from . import utils

class getGeneralSettings(): #NOTE: write as a mixin?
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
          NOTE: Datasets RegionalIncome and RegionalProduct were deprecated, use Regional instead. 
          
          https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf
          https://www.bea.gov/tools/   or  https://apps.bea.gov/API/signup/index.cfm
         
          Basically, there are three types of meta (the first three tabs): 
            (1) GETDATASETLIST      top level, get the name of all tables.  
            (2) GetParameterList    given a table, what parameters it needs to download (eg. NIPA)
            (3) GetParameterValues  given a parameter of a table, which values you can choose. (eg. TableID)
           
            Use them to get: name of datasets, their paramaters, and the values of the parameters.  These 
            can be used in the searches of individual datasets (in the other tabs)  

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
        "databases":        [  #TODO: pass this to the driver, load the individual drivers metdata in the api.
            {
             "displayName":"List of Datasets",
             "method"     :"datasetlist",   #NOTE run with getattr(data,'datasetlist')()
             "params"     :{},
            },
            {
             "displayName":"Parameter List",
             "method"     :"getParameterList",   
             "params"     :{'datasetname':'NIPA'}, #Parameters and default options.
            },
            {
             "displayName":"Parameter Values",
             "method"     :"getParameterValues",   
             "params"     :{'datasetName':'NIPA','parameterName':'TableID'}, #Parameters and default options.
            },
            {
             "displayName":"NIPA",
             "method"     :"NIPA",   
             "params"     :{'tableName':'T10101','year':'X','frequency':'Q'}, #Parameters and default options.
            },
            {
             "displayName":"MNE",
             "method"     :"MNE",  
             "params"     :{
                 "Frequency"					        :"Q",
	               "TableID"					        	:"T10101",
                 "DirectionOfInvestment"  		:"inward" ,
                 "OwnershipLevel"				      :"0" ,
                 "NonbankAffiliatesOnly"		  :"0" ,
                 "Classification"				      :"Country" ,
                 "Country"						        :"all" ,
                 "Industry"					          :"all" ,
                 "Year"						            :"all" ,
                 "State"						          :"all" ,
                 "SeriesID"					          :"0" ,
                 "GetFootnotes"				        :"no" ,	
                 "Investment"					        :"all" ,	
                 "ParentInvestment"		        :"all" ,	 
              }, #Parameters and default options.
            },            
            {
             "displayName":"Fixed Assets",
             "method"     :"fixedAssets",  
             "params"     :{'TableName':'NIPA','Year':'Year'}, #Parameters and default options.
            },              
            {
             "displayName":"ITA",
             "method"     :"ITA",   
             "params"     :{"Indicator":"","AreaOrCountry":"","Frequency":"","Year":""}, #Parameters and default options.
            },              
            {
             "displayName":"IIP",
             "method"     :"IIP",   
             "params"     :{"TypeOfInvestment":"","Component":"","Frequency":"","Year":""}, #Parameters and default options.
            },              
            {
             "displayName":"GDP by Industry",
             "method"     :"GDPbyIndustry",   
             "params"     :{"Industry":"","TableID":"","Frequency":"","Year":""}, #Parameters and default options.
            },              
            #{  #RegionalIncome and RegionalProduct were deprecated - use Regional Instead.
            # "displayName":"RegionalIncome",
            # "method"     :"RegionalIncome",   
            # "params"     :{"GeoFips":"","LineCode":"","TableName":"","Year":""}, #Parameters and default options.
            #},              
            #{
            # "displayName":"RegionalProduct",
            # "method"     :"RegionalProduct",  
            # "params"     :{"GeoFips":"","Component":"","IndustryId":"","Year":""}, #Parameters and default options.
            #},              
            {
             "displayName":"InputOutput",
             "method"     :"InputOutput",   
             "params"     :{"TableID":"","Year":""}, #Parameters and default options.
            },                          
            {
             "displayName":"Under. GDP by Industry",
             "method"     :"UnderlyingGDPbyIndustry",  
             "params"     :{"Industry":"Industry", "TableID":"","Frequency":"", "Year":""}, #Parameters and default options.
            },                          
            {
             "displayName":"Intl Serv Trade",
             "method"     :"IntlServTrade",   
             "params"     :{"TypeOfService":"","TradeDirection":"","Affiliation":"","AreaOrCountry":"", "Year":""}, #Parameters and default options.
            },                          
            {
             "displayName":"Regional",
             "method"     :"Regional",   
             "params"     :{"GeoFips"   :"","LineCode"  :"","TableName" :"", "Year":""}, #Parameters and default options.
            },                          
            {
             "displayName":"NIPA Vintage Tbl",
             "method"     :"NIPAVintageTables",   
             "params"     :{}, #Parameters and default options.
            },                          
          ],
     }  
    
    return(output)