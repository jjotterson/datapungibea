import pandas as pd
import requests
import json
from datapungibea import generalSettings 

def _getBaseRequest(baseRequest={},connectionParameters={},userSettings={}):
    '''
      Write a base request.  Could have other such functions, one for each type of base request.
    '''
    if baseRequest =={}:
       connectInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
       return(connectInfo.baseRequest)
    else:
       return(baseRequest)

def _getBaseCode(codeEntries = []):
    code = '''
              import requests
              import json    
              
              #(1) get user API key (not advised but can just write key and url in the file)
              #    file should contain: {{"BEA":{{"key":"YOUR KEY","address":"https://apps.bea.gov/api/data/"}}}}
              
              apiKeysFile = "{}"
              with open(apiKeysFile) as jsonFile:
                 apiInfo = json.load(jsonFile)
                 url,key = apiInfo["BEA"]["url"], apiInfo["BEA"]["key"]    

            '''.format(codeEntries)
    return(code)

class getDatasetlist():
    def __init__(self,baseRequest={},connectionParameters={},userSettings={}):
        self._connectionInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings )
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings)
        self._lastLoad    = {}  #data stored here to asist other function as clipboard

    def datasetlist(self,verbose=False):
        query = self._baseRequest
        query['params'].update({'method':'GETDATASETLIST'})
        
        retrivedData = requests.get(**query)
        
        df_output = self._cleanOutput(query,retrivedData)
        
        if verbose == False:
            self._lastLoad = df_output
            return(df_output)
        else:
            code = self._getCode(query)
            output = dict(dataFrame = df_output, request = retrivedData, code = code)  
            self._lastLoad = output
            return(output)  
    
    def _cleanOutput(self,query,retrivedData):
        if query['params']['ResultFormat'] == 'JSON':
            df_output =  pd.DataFrame( retrivedData.json()['BEAAPI']['Results']['Dataset'] )
        else:
            df_output =  pd.DataFrame( retrivedData.xml()['BEAAPI']['Results']['Dataset'] )  #TODO: check this works
    
        return(df_output)

    def _getCode(self,query):
        #general code to all drivers:
        try:
            apiKeyPath = self._connectionInfo.userSettings["ApiKeysPath"]
        except:
            apiKeyPath = " unavailable "

        baseCode = _getBaseCode([apiKeyPath])
        
        #specific code to this driver:
        queryClean = query
        queryClean['url'] = 'url'
        queryClean['params']['UserID'] = 'key'
        
        
        queryCode = '''
              query = {}
              retrivedData = requests.get(**query)'''.format(json.dumps(queryClean))
        
        queryCode = queryCode.replace('"url": "url"', '"url": url')
        queryCode = queryCode.replace('"UserID": "key"', '"UserID": key')
        
        return(baseCode + queryCode)

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
        self._baseRequest = _getBaseRequest(baseRequest,connectionParameters,userSettings) 
        self._lastLoad    = {}  #data stored here to asist other function as clipboard
    
    def NIPA(self,
        tableName,
        frequency = 'Q',
        payload={'method': 'GETDATA', 'DATABASENAME': 'NIPA', 'datasetname': 'NIPA', 'Year': 'X', 'ParameterName': 'TableID'},
        outputFormat="tablePretty",
        tryFrequencies=False
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
        query = self._baseRequest
        query['params'].update({'TABLENAME': tableName})
        query['params'].update({'FREQUENCY':frequency})
        query['params'].update(payload)
        
        # TODO: try loading different frenquencies if no return
        #
        nipa = requests.get(**query)
        
        # output format
        if outputFormat == "table":
            # TODO: check if xml or json
            self._lastLoad = pd.DataFrame(nipa.json()['BEAAPI']['Results']['Data'])
            return(self._lastLoad )
        elif outputFormat == "tablePretty":
            table = pd.DataFrame(nipa.json()['BEAAPI']['Results']['Data'])
            table['LineNumber'] = pd.to_numeric(table['LineNumber'])
            table['DataValue'] = pd.to_numeric(table['DataValue'])
            
            meta = table.drop(['DataValue', 'TimePeriod'], axis=1).drop_duplicates()
            meta = meta.set_index(['LineNumber', 'SeriesCode', 'LineDescription']).reset_index()
            
            table = table[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]
            table = pd.pivot_table(table, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first')
            self._lastLoad = {'metadata': meta, 'table': table}
            return(self._lastLoad)
        else:
            self._lastLoad = nipa
            return(self._lastLoad)


if __name__ == '__main__':
    #from datapungibea.drivers import getNIPA
    #v = getNIPA()
    #v.NIPA('T10101')
    from datapungibea.drivers import getDatasetlist
    v = getDatasetlist()
    v.datasetlist(verbose=True)