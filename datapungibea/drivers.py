import pandas as pd
import requests
import json
from copy import deepcopy
import pyperclip
from datapungibea import generalSettings 
from datapungibea import vintage as vintageFns
from datapungibea import utils
import re
import math


# (1) Auxiliary functions ######################################################
def _getBaseRequest(baseRequest={},connectionParameters={},userSettings={}):
    '''
      Write a base request.  Could have other such functions, one for each type of base request.
    '''
    if baseRequest =={}:
       connectInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
       return(connectInfo.baseRequest)
    else:
       return(baseRequest)

def _getBaseCode(codeEntries): 
    '''
      eg: start with an array vEntries, _getBaseCode(*vEntries)
    '''
    code = '''
import requests
import json    
import pandas as pd

#(1) get user API key (not advised but can just write key and url in the file)
#    file should contain: {{"BEA":{{"key":"YOUR KEY","url": "{}" }}}}

apiKeysFile = "{}"
with open(apiKeysFile) as jsonFile:
   apiInfo = json.load(jsonFile)
   url,key = apiInfo["BEA"]["url"], apiInfo["BEA"]["key"]    
     '''.format(*codeEntries)
    return(code)

def _getCode(query,userSettings={},pandasCode=""):
    #general code to all drivers:
    try:
        url        = query['url']
        if not userSettings:  #if userSettings is empty dict 
                apiKeyPath = generalSettings.getGeneralSettings( ).userSettings['ApiKeysPath']
        else:
            apiKeyPath = userSettings['ApiKeysPath']
    except:
        url         = " incomplete connection information "
        apiKeyPath = " incomplete connection information "
    
    baseCode = _getBaseCode([url,apiKeyPath])
    
    #specific code to this driver:
    queryClean = deepcopy(query)
    queryClean['url'] = 'url'
    queryClean['params']['UserID'] = 'key'
    
    
    queryCode = '''
query = {}
retrivedData = requests.get(**query)

{} #replace json by xml if this is the request format
    '''.format(json.dumps(queryClean),pandasCode)
    
    queryCode = queryCode.replace('"url": "url"', '"url": url')
    queryCode = queryCode.replace('"UserID": "key"', '"UserID": key')
    
    return(baseCode + queryCode)

def _clipcode(self):
    try:
        pyperclip.copy(self._lastLoad['code'])
    except:
        print("Loaded session does not have a code entry.  Re-run with verbose option set to True. eg: v.drivername(...,verbose=True)")

# (2) Drivers ###################################################################
class getDatasetlist():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest    = _getBaseRequest(baseRequest,connectionParameters,userSettings)  #TODO: could just pass the output of _connectionInfo here.
        self._lastLoad       = {}  #data stored here to assist functions such as clipcode
    
    def datasetlist(self,params = {},verbose=False):
        query = deepcopy(self._baseRequest)
        query['params'].update({'method':'GETDATASETLIST'})
        
        retrivedData = requests.get(**query)
        
        df_output = self._cleanOutput(query,retrivedData)
        
        if verbose == False:
            self._lastLoad = df_output
            return(df_output)
        else:
            code = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
            output = dict(dataFrame = df_output, request = retrivedData, code = code)  
            self._lastLoad = output
            return(output)  
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame( retrivedData.json()['BEAAPI']['Results']['Dataset'] )"
            df_output =  pd.DataFrame( retrivedData.json()['BEAAPI']['Results']['Dataset'] )
        else:
            self._cleanCode = "pd.DataFrame( retrivedData.json()['BEAAPI']['Results']['Dataset'] )"
            df_output =  pd.DataFrame( retrivedData.xml()['BEAAPI']['Results']['Dataset'] )  #TODO: check this works
    
        return(df_output)
        
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"List of Datasets",
            "method"     :"datasetlist",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getNIPA():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings ) 
        self._baseRequest    = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad       = {}  #data stored here to asist other function as clipboard
    
    def NIPA(self,
        tableName,
        frequency      = 'Q',
        year           = 'X',
        payload        = {'method': 'GETDATA', 'DATABASENAME': 'NIPA', 'datasetname': 'NIPA', 'ParameterName': 'TableID'},
        tryFrequencies = False,  #TODO: remove
        outputFormat   = "tablePretty",
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'TABLENAME': tableName})
        query['params'].update({'FREQUENCY':frequency})
        query['params'].update({'YEAR':year})
        query['params'].update(payload)
        
        # TODO: try loading different frenquencies if no return
        #
        retrivedData = requests.get(**query)
        
        output         = self._cleanOutput(query,retrivedData,outputFormat) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(self._lastLoad)
        else:
           output['code'] = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData, outputFormat):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
        
        if outputFormat == "tablePretty":
            df_output['LineNumber'] = pd.to_numeric(df_output['LineNumber'])
            df_output['DataValue'] = pd.to_numeric(df_output['DataValue'].apply(lambda x: x.replace(',','')))
            
            meta = df_output.drop(['DataValue', 'TimePeriod'], axis=1).drop_duplicates()
            meta = meta.set_index(['LineNumber', 'SeriesCode', 'LineDescription']).reset_index()
            
            df_output = df_output[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]
            df_output = pd.pivot_table(df_output, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first')
            
            output = {'dataFrame':df_output,'metadata':meta}
                        
            #update the code string:
            self._cleanCode = self._cleanCode + "\ndf_output['LineNumber'] = pd.to_numeric(df_output['LineNumber'])  \n" 
            self._cleanCode = self._cleanCode + "df_output['DataValue'] = pd.to_numeric(df_output['DataValue'].apply(lambda x: x.replace(',','')))  \n"  
            self._cleanCode = self._cleanCode + "df_output = df_output[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]  \n"   
            self._cleanCode = self._cleanCode + "df_output = pd.pivot_table(df_output, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first') \n" 
            
        return(output)
     
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"List of Datasets",
            "method"     :"datasetlist",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getGetParameterList():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def getParameterList(self,
        datasetname,
        payload        = {'method': 'GetParameterList'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'datasetname':datasetname})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Parameter'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Parameter'])
        else:
            self._cleanCode = "pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Parameter'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Parameter'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getGetParameterValues():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def getParameterValues(self,
        datasetName,
        parameterName,         
        payload        = {'method': 'getParameterValues'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'datasetname':datasetName})
        query['params'].update({'parameterName':parameterName})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['ParamValue'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['ParamValue'])
        else:
            self._cleanCode = "pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['ParamValue'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['ParamValue'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
    
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getMNE():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def MNE(self,
	    Frequency,				
	    TableID,				
        DirectionOfInvestment,  	
        OwnershipLevel,				
        NonbankAffiliatesOnly,		 
        Classification,				 
        Country,					
        Industry,					
        Year,						
        State,						
        SeriesID,					
        GetFootnotes,				
        Investment,						
        ParentInvestment,				
        payload        = {'method': 'GETDATA',  'datasetname': 'MNE', 'ParameterName': 'TableID'},
        tryFrequencies = False,  #TODO: remove
        outputFormat   = "tablePretty",
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({ "Frequency"			   :  Frequency			     })
        query['params'].update({ "TableID"			       :  TableID			     })
        query['params'].update({ "DirectionOfInvestment"   :  DirectionOfInvestment  })
        query['params'].update({ "OwnershipLevel"		   :  OwnershipLevel		 })
        query['params'].update({ "NonbankAffiliatesOnly"   :  NonbankAffiliatesOnly  })
        query['params'].update({ "Classification"		   :  Classification		 })        
        query['params'].update({ "Country"			       :  Country			     })
        query['params'].update({ "Industry"			       :  Industry			     })
        query['params'].update({ "Year"				       :  Year				     })
        query['params'].update({ "State"				   :  State				     })
        query['params'].update({ "SeriesID"			       :  SeriesID			     })
        query['params'].update({ "GetFootnotes"		       :  GetFootnotes		     })
        query['params'].update({ "Investment"			   :  Investment			 })
        query['params'].update({ "ParentInvestment"        :  ParentInvestment	     })
        query['params'].update(payload)
        
        # TODO: try loading different frenquencies if no return
        #
        retrivedData = requests.get(**query)
        
        output         = self._cleanOutput(query,retrivedData,outputFormat) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(self._lastLoad)
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData, outputFormat):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
        
        if outputFormat == "tablePretty":
            df_output['LineNumber'] = pd.to_numeric(df_output['LineNumber'])
            df_output['DataValue'] = pd.to_numeric(df_output['DataValue'].apply(lambda x: x.replace(',','')))
            
            meta = df_output.drop(['DataValue', 'TimePeriod'], axis=1).drop_duplicates()
            meta = meta.set_index(['LineNumber', 'SeriesCode', 'LineDescription']).reset_index()
            
            df_output = df_output[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]
            df_output = pd.pivot_table(df_output, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first')
            
            output = {'dataFrame':df_output,'metadata':meta}
            
            #update the code string:
            self._cleanCode = self._cleanCode + "\ndf_output['LineNumber'] = pd.to_numeric(df_output['LineNumber'])  \n" 
            self._cleanCode = self._cleanCode + "df_output['DataValue'] = pd.to_numeric(df_output['DataValue'].apply(lambda x: x.replace(',','')))  \n"  
            self._cleanCode = self._cleanCode + "df_output = df_output[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]  \n"   
            self._cleanCode = self._cleanCode + "df_output = pd.pivot_table(df_output, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first') \n" 
            
        return(output)
     
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"List of Datasets",
            "method"     :"datasetlist",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]

class getFixedAssets():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def fixedAssets(self,
        TableName,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'FixedAssets'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'TableName':TableName})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]

class getITA():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def ITA(self,
        Indicator,
        AreaOrCountry,
        Frequency,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'ITA'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'Indicator':Indicator})
        query['params'].update({'AreaOrCountry':AreaOrCountry})
        query['params'].update({'Frequency':Frequency})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            try: #one line datasets will need to be transformed in an array
                self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
                df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
            except:
                try:
                    self._cleanCode = "df_output =  pd.DataFrame([retrivedData.json()['BEAAPI']['Results']['Data']])"
                    df_output =  pd.DataFrame([retrivedData.json()['BEAAPI']['Results']['Data']])
                except:
                    self._cleanCode = "df_output = pd.DataFrame([])"
                    df_output = pd.DataFrame([])
        else:
            try: #one line datasets will need to be transformed in an array
               self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])" 
               df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
            except:
                try:
                    self._cleanCode = "df_output =  pd.DataFrame([retrivedData.json()['BEAAPI']['Results']['Data']])"
                    df_output =  pd.DataFrame([retrivedData.json()['BEAAPI']['Results']['Data']])
                except:
                    self._cleanCode = "df_output = pd.DataFrame([])"
                    df_output = pd.DataFrame([])
                  
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getIIP():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def IIP(self,
        TypeOfInvestment,
        Component,
        Frequency,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'IIP'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'TypeOfInvestment':TypeOfInvestment})
        query['params'].update({'Component':Component})
        query['params'].update({'Frequency':Frequency})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Data'])  #NOTE: Not workings, works if use "Dimensions" instead of data, but not sure if this is the right thing.
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getGDPbyIndustry():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def GDPbyIndustry(self,
        Industry,
        TableID,
        Frequency,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'GDPbyIndustry'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'Industry':Industry})
        query['params'].update({'TableID':TableID})
        query['params'].update({'Frequency':Frequency})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else: 
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]

class getRegionalIncome():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def RegionalIncome(self):
        print("RegionalIncome and RegionalProduct were deprecated - use Regional instead - check https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf appendix I and J")
        output = {'dataFrame':pd.DataFrame(['Dataset deprecated - use Regional'])}       
        return(output)

class getRegionalProduct():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def RegionalProduct(self):
        print("RegionalIncome and RegionalProduct were deprecated - use Regional instead - check https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf appendix I and J")
        output = {'dataFrame':pd.DataFrame(['Dataset deprecated - use Regional'])}       
        return(output)


class getInputOutput():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def InputOutput(self,
        TableID,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'InputOutput'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'TableID':TableID})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getUnderlyingGDPbyIndustry():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def UnderlyingGDPbyIndustry(self,
        Industry,
        TableID,
        Frequency,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'UnderlyingGDPbyIndustry'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({'Industry':Industry})
        query['params'].update({'TableID':TableID})
        query['params'].update({'Frequency':Frequency})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getIntlServTrade():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def IntlServTrade(self,
        TypeOfService,
        TradeDirection,
        Affiliation,
        AreaOrCountry,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'IntlServTrade'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({"TypeOfService" : TypeOfService})
        query['params'].update({"TradeDirection": TradeDirection})
        query['params'].update({"Affiliation"   : Affiliation})
        query['params'].update({"AreaOrCountry" : AreaOrCountry})
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getRegional():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          the baseRequest contains user Key, url of datasource, and prefered output format (JSON vs XML)
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def Regional(self,
        GeoFips,
        LineCode,
        TableName,
        Year,
        payload        = {'method': 'GETDATA',  'datasetname': 'Regional'},
        verbose        = False
    ):
        '''
            User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
            can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
            
            payload - will override the default
            
            outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                           Else, returns the JSON, XML.
        '''
        # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
        # load user preferences defined in userSettings, use suggested parameters, override w fun entry
        query = deepcopy(self._baseRequest)
        query['params'].update({"GeoFips"   : GeoFips   })
        query['params'].update({"LineCode"  : LineCode  })
        query['params'].update({"TableName" : TableName })
        query['params'].update({'Year':Year})
        query['params'].update(payload)
        
        retrivedData = requests.get(**query) 
        output       = self._cleanOutput(query,retrivedData) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['code']    = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])
        else:
            self._cleanCode = "df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])"
            df_output =  pd.DataFrame(retrivedData.json()['BEAAPI']['Results']['Data'])  #TODO: check this works
         
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"Parameter of Dataset",
            "method"     :"GetParameterList",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getNIPAVintageTables():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          driver of list of NIPA vintage tables
        '''
        #TODO: need to put a default url location
        #self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        #self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def NIPAVintageTables(self,verbose=False):
        '''
            Returns the list of NIPA vintage tables containing: 
             - the year/Quarter of the release, 
             - their revision (vintage): third, second, or advance
             - the release date
             - the link to the data
            The output is a pandas table.  There are no inputs, besides the url of the homepage with the data given by default.
        '''
        # TODO: 
        listTables   = vintageFns.urlNIPAHistQYVintage( )  
        output       = self._cleanOutput(listTables) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(output['dataFrame'])
        else:
           output['request'] = listTables
           output['code']    = self._getCode() #TODO: write code as method in class
           self._lastLoad    = output
           return(output)       
    
    def _cleanOutput(self,listTables):
        #TODO: break year/quarter in first column into year and quarter columns
        df_output =  listTables
        df_output['year']    = df_output['yearQuarter'].apply(lambda x: x.split(',')[0].strip())
        df_output['quarter'] = df_output['yearQuarter'].apply(lambda x: x.split(',')[1].strip())
        df_output.drop('yearQuarter',axis=1,inplace=True)
        df_output['releaseDate'] = pd.to_datetime(df_output['releaseDate'],errors='ignore')
        output = {'dataFrame':df_output}
                    
        return(output)
      
    def clipcode(self):
        _clipcode(self)
    
    def _getCode(self):
        code = "to be written"
        return(code)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"NIPAVintageTables",
            "method"     :"getNIPAVintageTables",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


class getNIPAVintageTablesLocations():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          driver of list of NIPA vintage tables
        '''
        #TODO: need to put a default url location
        #self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        #self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}                  #data stored here to asist other function as clipboard
        self._urlsOfQYRelease      = pd.DataFrame()  #a table of the url of data with same QY release.  Will load via _getUrlsOfQYRelease if empty
        self._urlsOfQueryQYRelease = pd.DataFrame()  #table of urls of data with same QY release restricted to query of interest.  Load via _queryUrlsOfQYRelease
        self._urlsOfExcelTables    = pd.DataFrame()  #location of Excel tables of interest: type, Title, QY and ReleaseDate.  Load with _getUrlsOfData
        
    def NIPAVintageTablesLocations(self,type = 'main', Title = '',year='',quarter='',vintage = '',releaseDate='',reload=False,verbose=False):
        '''
          Returns the location of the datasets given conditions.
          - type:  main, underlyning, MilsOfDollars
          - Title: Section 0, Section 1, ...
          - vintage: Third, Second, Advance
          - year: 2019, string or numeric
          - quarter: Q1,...,Q4
          - releaseDate: eg '2019-04-05', '04-05-2019', 'Apr-05-2019'  will pick the first release date prior or equal to this.
          - reload: reloads getting the datatable by QY ReleaseDate
          - verbose: False just returns a table with all data.  Else, returns cleaned data, code, and returned query
        '''
        self._getUrlsOfData( type, Title,year,quarter,vintage,releaseDate,reload)  #get the url of excel sheets with data given type, Title etc
        
        self.array_output = vintageFns.getNIPADataFromListofLinks(self._urlsOfExcelTables)   
        
        self.clean_array = self._cleanExcelQuery(self.array_output)
        return(self.clean_array)  
    
    def _getUrlsOfQYRelease(self,reload=False):
        if reload: 
            self._urlsOfQYRelease = getNIPAVintageTables().NIPAVintageTables()
        elif self._urlsOfQYRelease.empty:
            self._urlsOfQYRelease = getNIPAVintageTables().NIPAVintageTables()
    
    def _queryUrlsOfQYRelease(self,year='',quarter='',vintage = '',releaseDate='',reload=False):        
        self._getUrlsOfQYRelease(reload)
        df_output = self._urlsOfQYRelease.copy()
        
        if not year == '':
            year = str(year)
            df_output = df_output.loc[df_output['year']==year]
        
        if not quarter == '':
            quarter = quarter.upper()
            df_output = df_output.loc[df_output['quarter']==quarter]
        
        if not vintage =='':
            vintage = vintage.capitalize()
            df_output = df_output.loc[df_output['vintage']==vintage]
        
        if not releaseDate == '':
            firstDate = df_output.loc[ df_output['releaseDate'] <= releaseDate]['releaseDate'].max()
            df_output = df_output.loc[df_output['releaseDate'] == firstDate]
        
        self._urlsOfQueryQYRelease = df_output
    
    def _getURLsInQYRelease(self,tableLine):
        self._urlsInQYRelease = vintageFns.urlNIPAHistQYVintageMainOrUnderlSection( tableLine )
        df_output = pd.DataFrame()
        for key,table in self._urlsInQYRelease.items():
            table.insert(0,'type',key)
            df_output = pd.concat([df_output, table  ])
        return(df_output)
    
    def _getUrlsOfData(self,type = 'main', Title = '',year='',quarter='',vintage = '',releaseDate='',reload=False):
        df_output = pd.DataFrame()
        
        #get data the url inside the group with same QY and Release date, 
        # restrict by the given conditions
        self._queryUrlsOfQYRelease(year,quarter,vintage,releaseDate,reload)
        
        #Get the URLs inside each entry above, these are pointers to Excel files
        for line in self._urlsOfQueryQYRelease.iterrows():
            df_output = pd.concat([df_output, self._getURLsInQYRelease( line[1] )  ])    
        
        if not type == '':
            type = type.lower()
            df_output = df_output.loc[df_output['type']==type]
        
        if not Title == '':
            Title = Title.capitalize()
            df_output = df_output.loc[df_output['Title']==Title]
              
        self._urlsOfExcelTables = df_output
    
    def _cleanOutput(self,listTables):
        #TODO: break year/quarter in first column into year and quarter columns
        df_output =  listTables
        df_output['year']    = df_output['yearQuarter'].apply(lambda x: x.split(',')[0].strip())
        df_output['quarter'] = df_output['yearQuarter'].apply(lambda x: x.split(',')[1].strip())
        df_output.drop('yearQuarter',axis=1,inplace=True)
        df_output['releaseDate'] = pd.to_datetime(df_output['releaseDate'],errors='ignore')
        output = {'dataFrame':df_output}
                    
        return(output)
    
    def _cleanExcelQuery(self,arrayData):
        '''
           Given an array of dictionaries (array entry contains all data by year, quarter type Title)
        '''
        clean_array = []
        for entry in arrayData:
            for sheetName, sheet in entry['data'].items():
                sName = re.sub('Qtr','Q',sheetName)
                sName = re.sub('Quarter','Q',sName)
                sName = re.sub('Ann','A',    sName)
                sName = re.sub('Annual','A',  sName)
                sName = re.sub('A',' A',     sName)
                sName = re.sub('Q',' Q',     sName)
                sName = re.sub('_',' ',      sName)
                sName = re.sub('-',' ',      sName)
                sName = re.sub(' +', ' ',    sName).strip()
                sName = sName.split(' ')
                table = sName[0]
                try:
                    frequency = sName[1]  #covers the case sheetName = 'Contents'
                except:
                    frequency = ''
                
                #clean up the sheet:
                #(1) delete empty rows and columns (check delete empty cols as well)
                sheet.dropna(how='all',inplace=True)
                sheet.dropna(how='all',axis=1,inplace=True)
                sheet.reset_index(drop=True)
                
                #(2) find where data starts; separate data (sheet) from meta
                meta = []
                if not table == 'Contents':
                    try:
                      rowWithTitles = sheet.index[sheet.iloc[:,0] == 'Line'].min()
                    except:
                      rowWithTitles = 5
                      print('the following sheet might have problems:' + sheetName)
                    
                    #(3) get col titles and metadata
                    colTitles = list(sheet.iloc[rowWithTitles])
                    if math.isnan(colTitles[1]):  #TODO: improve this
                        colTitles[1] = 'Variable'
                    if math.isnan(colTitles[2]):
                        colTitles[2] = 'Code'           
                    
                    meta = [sheet.keys()[0]]
                    meta = meta+ list(sheet.iloc[0:rowWithTitles,0] ) 
                    
                    #(4) make table:
                    sheet = sheet.iloc[rowWithTitles+1:].reset_index(drop=True)   
                    sheet.columns = colTitles               
                    
                    clean_array.append(  {**entry, **{'sheetName':sheetName,'table':table,'frequency':frequency,'meta':meta}, **{'data':sheet}}   )
        
        return(clean_array)

    def clipcode(self):
        _clipcode(self)
    
    def _getCode(self):
        code = "to be written"
        return(code)
    
    def _driverMetadata(self):
        self.metadata =     [{
            "displayName":"NIPAVintageTables",
            "method"     :"getNIPAVintageTables",   #Name of driver main function - run with getattr(data,'datasetlist')()
            "params"     :{},
        }]


if __name__ == '__main__':
    #from datapungibea.drivers import getNIPA
    #v = getNIPA()
    #v.NIPA('T10101')
      
    #from datapungibea.drivers import getNIPA #getDatasetlist
    #v = getNIPA() #getDatasetlist()
    #print(v.NIPA('T10101',verbose=True))
    ##print(v._lastLoad['code'])
    
    #from datapungibea.drivers import getGetParameterList #getDatasetlist
    #v = getGetParameterList()
    #print(v.getParameterList('NIPA',verbose = True)['code'])
    #
    #from datapungibea.drivers import getGetParameterValues #getDatasetlist
    #v = getGetParameterValues()
    #print(v.getParameterValues('NIPA','TableID')) 
    
    #from datapungibea.drivers import getNIPAVintageTables
    #v = getNIPAVintageTables()
    #print(v.NIPAVintageTables())
    #listTables = vintageFns.urlNIPAHistQYVintage( )
    #print(listTables)    
    
    from datapungibea.drivers import  *
    v = getNIPAVintageTablesLocations()  
    #print(v._queryUrlsOfQYRelease(releaseDate='2019-04-01'))
    #print(v._getUrlsOfData(releaseDate='2019-04-01'))
    cases = v.NIPAVintageTablesLocations(type = 'main',Title= 'Section 1',releaseDate = '2018-03-20')
    print(cases)
    #tab = vintageFns.getNIPADataFromListofLinks(cases)
    #array_output = cases
    #array = []
    #for entry in array_output:
    #    for sheetName, sheet in entry['data'].items():
    #        sName = re.sub('Qtr','Q',sheetName)
    #        sName = re.sub('Quarter','Q',sName)
    #        sName = re.sub('Ann','A',    sName)
    #        sName = re.sub('Annual','A',  sName)
    #        sName = re.sub('A',' A',     sName)
    #        sName = re.sub('Q',' Q',     sName)
    #        sName = re.sub('_',' ',      sName)
    #        sName = re.sub('-',' ',      sName)
    #        sName = re.sub(' +', ' ',    sName).strip()
    #        sName = sName.split(' ')
    #        table = sName[0]
    #        try:
    #            frequency = sName[1]
    #        except:
    #            frequency = ''
    #        
    #        array.append(  {**entry, **{'sheetName':sheetName,'table':table,'frequency':frequency}, **{'data':sheet}}   )
    #
