import pandas as pd
import requests
import json
from copy import deepcopy
import pyperclip
import math
import re
from datetime import datetime
from datapungibea import generalSettings 
from datapungibea import vintage as vintageFns
from datapungibea import utils
from datapungibea.config import CFGnipaSummary


# (1) Auxiliary functions ######################################################
def _getBaseRequest(baseRequest={},connectionParameters={},userSettings={}):
    '''
      Write a base request.  This is the information that gets used in most requests such as getting the userKey
    '''
    if baseRequest =={}:
       connectInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
       return(connectInfo.baseRequest)
    else:
       return(baseRequest)

def _getBaseCode(codeEntries): 
    '''
      The base format of a code that can be used to replicate a driver using Requests directly.
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
    '''
       Copy the string to the user's clipboard (windows only)
    '''
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
        '''
        Get the list of available datasets in the BEA API.  
        Sample run -
          datasetlist()
        
        Args:
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
        '''
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
    '''
      rest
    '''
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
        outputFormat   = "tablePretty",
        verbose        = False,
        includeIndentations = True
    ):
        '''
        Get National Income and Product Account (NIPA) data. Most parameters are set to deafault values; passing 
        tableName will return a value of quarterly data in all available years.  Sample run -
          NIPA('T10101')  
          NIPA('T10101', frequency = 'A', year='X',verbose=True,includeIndentation=False)
            
        Args:
            tableName (str): name of NIPA table, for example T10101
            frequency (str): frequency of data - Annual (A), quarterly (Q) or monthly (M); default to Q
            year (str): specific year or X for all years -  eg, '2019' or 'X'; default to X
            payload (dict): this is the base request information of a BEA NIPA query; default - {'method': 'GETDATA', 'DATABASENAME': 'NIPA', 'datasetname': 'NIPA', 'ParameterName': 'TableID'}
            outputFormat (str): tablePretty will clean up data and return pandas of variable by date; else returns table of (variable,date) by data; default to tablePretty
            verbose (bool): If false just return a pandas table; else return table, the request result and the code used; default to False
            includeIndentations (bool): API does not include indentation of the table, indicate if should include it; default to True
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code
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
        
        output         = self._cleanOutput(query,retrivedData,outputFormat,includeIndentations) #a dict of a df or df and meta (tablePretty)
        
        if verbose == False:
            self._lastLoad = output['dataFrame']
            return(self._lastLoad)
        else:
           output['code'] = _getCode(query,self._connectionInfo.userSettings,self._cleanCode)
           output['request'] = retrivedData
           self._lastLoad = output
           return(output)       
    
    def _cleanOutput(self,query,retrivedData, outputFormat,includeIndentations):
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
            df_output = self._includeIndentations(df_output,query['params']['TABLENAME'],includeIndentations)
            output = {'dataFrame':df_output,'metadata':meta}
                        
            #update the code string:
            self._cleanCode = self._cleanCode + "\ndf_output['LineNumber'] = pd.to_numeric(df_output['LineNumber'])  \n" 
            self._cleanCode = self._cleanCode + "df_output['DataValue'] = pd.to_numeric(df_output['DataValue'].apply(lambda x: x.replace(',','')))  \n"  
            self._cleanCode = self._cleanCode + "df_output = df_output[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]  \n"   
            self._cleanCode = self._cleanCode + "df_output = pd.pivot_table(df_output, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first') \n" 
            if includeIndentations:
                self._cleanCode = self._cleanCode + '\n#Including indentations:'
                self._cleanCode = self._cleanCode + '\nimport datapungibea as dpb \ndata = dpb.data() \ndf_output = data.getNIPA._includeIndentations(df_output,"'+query['params']['TABLENAME']+'")\n'
                self._cleanCode = self._cleanCode + '#can get all indentations running:    from datapungibea.config.CFGindentations import indentations as cfgIndentations \n'
        return(output)
    
    def _includeIndentations(self,df_output,tableName,includeIndentations=True): #tableName = query['params']['TABLENAME']
        if not includeIndentations:
            return(df_output)
        from datapungibea.config.CFGindentations import indentations as cfgIndentations #TODO: move this to __int__
        cfgCases = list(filter(lambda x: tableName in x['tableName'], cfgIndentations))
        if len(cfgCases) < 1:
            return(df_output)
        else:
            try:
                indentTable = cfgCases[0]
                indentTable = pd.DataFrame(list(zip(indentTable['LineNumber'],indentTable['SeriesCode'], indentTable['Indentations'])),columns=['LineNumber','SeriesCode','Indentations'])
                df_output.reset_index(inplace=True)
                df_output = df_output.merge(indentTable,on=['LineNumber','SeriesCode'],how='left') #merge will indentationTable, keep left cases that don't match with right
                df_output['Indentations'].fillna(0,inplace=True)
                df_output['LineDescription'] = df_output.apply(lambda x: '-'*x['Indentations'] + x['LineDescription'] , axis = 1)
                df_output.drop('Indentations',axis=1,inplace=True)
                df_output.set_index(['LineNumber', 'SeriesCode', 'LineDescription'],inplace=True)
            except:
                print('could not include indentations on table '+ tableName + ' returning table without indentation info')
        return(df_output)


     
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
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def getParameterList(self,
        datasetname,
        payload        = {'method': 'GetParameterList'},
        verbose        = False
    ):
        '''
        Get the list of parameter needed to get data from dataset.  
        Sample run -
          getParameterList('NIPA')
        
        Args:
            datasetname (str): the name of the dataset eg, NIPA
            payload (dict): the request payload that is basic to this driver; default to {'method': 'GetParameterList'}
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Get the list of values of a parameter of a database.  
        Sample run -
          getParameterValues('NIPA','tableName')
        
        Args:
            datasetname (str): the name of the dataset eg, NIPA
            parameterName (str): the name of the parameter you want to know the values of; eg 'tableName'
            payload (dict): the request payload that is basic to this driver; default to {'method': 'getParameterValues'}
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        outputFormat   = "tablePretty",
        verbose        = False
    ):
        '''
        Query the MNE database  
        Args:
            Frequency (str):				
	        TableID (str):				
            DirectionOfInvestment (str):  	
            OwnershipLevel (str):				
            NonbankAffiliatesOnly (str):		 
            Classification (str):				 
            Country (str):					
            Industry (str):					
            Year (str):						
            State (str):						
            SeriesID (str):					
            GetFootnotes (str):				
            Investment (str):						
            ParentInvestment (str):				
            payload (dict): default to {'method': 'GETDATA',  'datasetname': 'MNE', 'ParameterName': 'TableID'},
            outputFormat (str): default to "tablePretty",
            verbose (bool): default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the fixed assets database (API query)  
        Sample run -
          fixedAssets('T10101','2010')
        
        Args:
            tableName (str): the name of the NIPA table, eg 'T10101'
            Year (str): the year; eg 'X' for all years or '2018'
            payload (dict): the request payload that is basic to this driver; default to {'method': 'GETDATA',  'datasetname': 'FixedAssets'}
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the ITA database (API query)  
        Sample run -
          
        
        Args:
            Indicator (str): the name of the NIPA table, eg 'T10101'
            AreaOrCountry (str): the year; eg 'X' for all years or '2018'
            Frequency (str): eg Q
            Year (str): eg 2019
            payload (dict): the request payload that is basic to this driver; default to {'method': 'GETDATA',  'datasetname': 'FixedAssets'}
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the IIP database (API query)  
        Sample run -
         
        
        Args:
            TypeOfInvestment (str): eg
            Component (str): eg
            Frequency (str): eg Q
            Year (str): eg 'X' for all or '2019'
            payload (dict): request default {'method': 'GETDATA',  'datasetname': 'IIP'},
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the GDPbyIndustry database (API query)  
        Sample run -
         
        
        Args:
            Industry (str): eg
            TableID (str): eg
            Frequency (str): eg Q
            Year (str): eg 'X' for all or '2019'
            payload (dict): request default {'method': 'GETDATA',  'datasetname': 'GDPbyIndustry'},
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the InputOutput database (API query)  
        Sample run -
         
        
        Args:
            TableID (str): eg
            Year (str): eg 'X' for all or '2019'
            payload (dict): request default {'method': 'GETDATA',  'datasetname': 'InputOutput'},
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the UnderlyingGDPbyIndustry database (API query)  
        Sample run -
         
        
        Args:
            Industry (str): eg
            TableID (str): eg
            Frequency (str): eg Q
            Year (str): eg 'X' for all or '2019'
            payload (dict): request default {'method': 'GETDATA',  'datasetname': 'IIP'},
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the IntlServTrade database (API query)  
        Sample run -
         
        
        Args:
            TypeOfService (str): eg
            TradeDirection (str): eg
            Affiliation (str): eg 
            AreaOrCountry (str): eg
            Year (str): eg 'X' for all or '2019'
            payload (dict): request default {'method': 'GETDATA',  'datasetname': 'IntlServTrade'},
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Query the IntlServTrade database (API query)  
        Sample run -
         
        
        Args:
            GeoFips (str): eg
            LineCode (str): eg
            TableName (str): eg 
            Year (str): eg 'X' for all or '2019'
            payload (dict): request default {'method': 'GETDATA',  'datasetname': 'Regional'},
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code              
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
        Get a list of NIPA Vintage tables (non-API)  
        Sample run -
         NIPAVintageTables()
        
        Args:
            verbose (bool): if returns that data in a pandas dataframe format or all available information; default to False
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code (empty code for now)             
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


class getNIPAVintage():
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
        
    def NIPAVintage(self,tableName='',frequency='',type = 'main', Title = '',year='',quarter='',vintage = '',releaseDate='',reload=False,verbose=False,beaAPIFormat=False):
        '''
        Get a list of NIPA Vintage tables (non-API)  
        Sample run - 
           
  
        Args:
            tableName (str): the name of a NIPA table of interest; will return all tables otherwise. Default to '', all tables.
            frequency (str): A,Q or M.  Returns all frequencies otherwise.  Default to '', all frequencies   
            type (str):  main, underlyning, MilsOfDollars.  Defaults to main.
            Title (str): Section 0, Section 1, etc.  
            vintage (str): Third, Second, Advance
            year (str): string or numeric
            quarter (str): Q1,...,Q4
            releaseDate (str): will pick the first release date prior or equal to this. string or datetime eg datetime.now(), '2019-04-05', '04-05-2019', 'Apr-05-2019'  
            reload (bool): reloads getting the datatable by QY ReleaseDate
            verbose (bool): False just returns a table with all data.  Else, returns cleaned data, code, and returned query
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code   
        '''
        self._getUrlsOfData( type, Title,year,quarter,vintage,releaseDate,reload)  #get the url of excel sheets with data given type, Title etc
        self.array_output = vintageFns.getNIPADataFromListofLinks(self._urlsOfExcelTables)   
        self.clean_array = self._cleanExcelQuery(self.array_output,tableName,frequency,beaAPIFormat)
        
        output = dict()
        output['dataFrame'] = [ x['Results']['Data'] for x in self.clean_array ]
        
        if not verbose:
            self._lastLoad =  output['dataFrame']
            return(output['dataFrame'])
        else:
            output['code']  = 'none'  #TODO: fix code
            output['request'] = self.clean_array
            self._lastLoad = output
            return(output)
            
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
    
    def _cleanExcelQuery(self,arrayData,tableName='',frequency='',beaAPIFormat=False):
        '''
           Given an array of dictionaries (array entry contains all data by year, quarter type Title)
        '''
        clean_array = []
        for entry in arrayData:
            baseInfo = {key:val for key, val in entry.items() if not key == 'data'} #data that is not sheet
            #restrict to cases containing tableName and frequency
            if tableName == '' and frequency == '':
                subset = entry['data']
            else:
                subset = {key:val for key, val in entry['data'].items() if tableName.lower() in key.lower() and frequency.lower() in key.lower() }
            subset  = vintageFns.formatBeaRaw( subset )
            for sheetName, sheet in subset.items():
                sName = sheetName.split('_')
                table = sName[0]
                try:
                    frequency = sName[1]  #covers the case sheetName = 'Contents'
                except:
                    frequency = ''                 
                #add basic info to the pandas table:
                sheet['Data'].insert(0,'tableName',table)
                sheet['Data'].insert(1,'yearQuarterVintage','-'.join([entry['year'] , entry['quarter'],entry['vintage']]))
                sheet['Data'].insert(2,'releaseDate',entry['releaseDate'].strftime("%Y-%m-%d"))
                clean_array.append(  {**baseInfo, **{'sheetName':sheetName,'tableID':table,'frequency':frequency}, **{'Results':sheet}}   )
        
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


class getNIPASummary(): 
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        '''
          driver of list of NIPA Account Summary tables  
        '''
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}                  #data stored here to asist other function as clipboard
        self.cfgSummary = CFGnipaSummary.tabparams
        self.queryNIPA  = getNIPA(baseRequest,connectionParameters,userSettings)
        self.queryNIPAVintage = getNIPAVintage()
                
    def NIPASummary(self,year,frequency,verbose=False): 
        '''
        Overall view of NIPA data (non-API)  
        Sample run - 
            NIPASummary(2018,'Q')
  
        Args:
            frequency (str): A,Q or M.  Returns all frequencies otherwise.  Default to '', all frequencies   
            year (str): string or numeric
            verbose (bool): False just returns a table with all data.  Else, returns cleaned data, code, and returned query
        Returns:
            output: either a pandas dataframe or a dictionary (verbose=True) with dataFrame, request, and code               
        ''' 
        output = dict()
        output['request']   = self._getAccountTable(year,frequency)
        output['dataFrame'] = self._cleanRequest(output['request'])  #will put Account # - source/use as column title to shorten the request output
                
        if verbose == False:
            return(output['dataFrame'])
        else:
            return(output)
        
    def _cleanRequest(self,requestResult):
        df_array = []
        for key,entry in requestResult.items():
            useTable       = entry['uses'].copy()
            sourceTable    = entry['source'].copy()
            useCol         = list(useTable.columns)
            sourceCol      = list(sourceTable.columns)
            useCol[0]      = key + ' uses'
            sourceCol[0]   = key + ' sources'
            useTable.columns = useCol
            sourceTable.columns = sourceCol
            df_array.append(useTable)
            df_array.append(sourceTable)
        return(df_array)
        
    def _getAccountTable(self,year,frequency):
        array_output = deepcopy(self.cfgSummary)  #use the structure of cfgSummary to output
        for acct in self.cfgSummary:
            query = self.cfgSummary[acct]['source'] #TODO: query->queryUses querySources - one try - do source and uses at same time.
            if acct == 'Account 2':
                frequency = 'A'  #Account 2 only have annual data
            query.update({'frequency':frequency,'year':year})
            try:
                array_output[acct]['source'] = self._getAccountUseOrSource(**query)
            except:
                print( 'Could not find information of ' + acct +' on current NIPA.  Trying to query historical annual data.' )
                array_output[acct]['source'] = self._getAccountUseOrSourceVintage(**query)
            query = self.cfgSummary[acct]['uses']
            query.update({'frequency':frequency,'year':year})
            try:
                array_output[acct]['uses'] = self._getAccountUseOrSource(**query)
            except:
                print( 'Could not find information of ' + acct +' on current NIPA.  Trying to query historical annual data.' )
                array_output[acct]['source'] = self._getAccountUseOrSourceVintage(**query)          
        return(array_output)
    
    def _getAccountUseOrSource(self,tableName,year,frequency,tableEntries):
        readTable = self.queryNIPA.NIPA(tableName = tableName, frequency = frequency, year = year )
        readTable.reset_index(inplace=True)
        restrict = pd.DataFrame(tableEntries)
        output = pd.merge(restrict,readTable,on=['SeriesCode','SeriesCode'])
        output['LineDescription'] = output.apply(lambda x: x['indentation']*'-' + x['LineDescription'],axis=1)
        output.drop(['indentation','LineNumber'],axis=1,inplace=True)
        output.set_index(['LineDescription','SeriesCode'],inplace=True) #NOTE: this is just for sorting column order
        output.reset_index(inplace=True)
        return(output)

    def _getAccountUseOrSourceVintage(self,tableName,year,frequency,tableEntries,Title ='Section 1',releaseDate=datetime.now()):
        '''
          Try to get vintage data (try annual). Default is to check the last available vintage datset from current date.
        '''
        readTable = self.queryNIPAVintage.NIPAVintage(tableName = tableName, frequency = frequency, Title = Title, releaseDate = releaseDate )
        readTable = readTable[0]
        year = str(min(year,int(readTable.columns[-1]))) #either use: the queried year or the last available year in dateset.  The smallest of these. 
        cols = [ 'Line', 'LineDescription', 'SeriesCode',year ] 
        readTable = readTable[cols]
        #readTable.reset_index(inplace=True)
        restrict = pd.DataFrame(tableEntries)
        output = pd.merge(restrict,readTable,on=['SeriesCode','SeriesCode'])
        output['LineDescription'] = output.apply(lambda x: x['indentation']*'-' + x['LineDescription'],axis=1)
        output.drop(['indentation','Line'],axis=1,inplace=True)
        output.set_index(['LineDescription','SeriesCode'],inplace=True) #NOTE: this is just for sorting column order
        output.reset_index(inplace=True)
        return(output)
    

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
    
    #from datapungibea.drivers import  *
    #v = getNIPAVintage()  
    ##print(v._queryUrlsOfQYRelease(releaseDate='2019-04-01'))
    ##print(v._getUrlsOfData(releaseDate='2019-04-01'))
    #cases = v.NIPAVintage(tableName='T10101',frequency='Q',releaseDate = '2018-03-20')
    #print(cases)
    


    #v = getNIPASummary()
    #print(v.NIPASummary(2018,'Q'))

    #table indentations
    v = getNIPA()
    #print(v.NIPA('T11000',includeIndentations=False))
    print(v.NIPA('T11000'))
