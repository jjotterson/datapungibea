class datasetlist():

    def __init__(verbose=False):
        query = self._query
        query['params'].update({'method':'GETDATASETLIST'})
        
        retrivedData = requests.get(**query)
        
        if query['params']['ResultFormat'] == 'JSON':
            df_output =  pd.DataFrame( retrivedData.json()['BEAAPI']['Results']['Dataset'] )
        else:
            df_output =  pd.DataFrame( retrivedData.xml()['BEAAPI']['Results']['Dataset'] )  #TODO: check this works
        
        if verbose == False:
            return(df_output)
        else:
            code = '''
              import requests
              import json    
              
              #(1) get user API key (not advised but can just write key and url in the file)
              #    file should contain: {{"BEA":{{"key":"YOUR KEY","address":"https://apps.bea.gov/api/data/"}}}}
              
              apiKeysFile = "{}"
              with open(apiKeysFile) as jsonFile:
                 apiInfo = json.load(jsonFile)
                 url,key = apiInfo["BEA"]["address"], apiInfo["BEA"]["key"]       
            '''.format(self._userSettings["ApiKeysPath"])
            output = dict(dataFrame = df_output, request = retrivedData, code = code)  
            return(output)  

def NIPA(
    tableName,
    payload={'method': 'GETDATA', 'DATABASENAME': 'NIPA', 'datasetname': 'NIPA', 'Year': 'X', 'Frequency': 'Q', 'ParameterName': 'TableID'},
    outputFormat="tablePretty",
    beaHttp='https://apps.bea.gov/api/data/',
    tryFrequencies=False
   ):
    '''
      User only need to specify the NIPA tableName, other parameters are defined by default.  Year (set to X) and Frequency (set to Q)
      can be redefined with payload = {Year = 1990, Frequency = 'A'}, for example.
      
      payload - will override the default
      
      outputFormat - table, tablePretty will return tables (the latter separates the metadata and pivots the table to index x time).
                     Else, returns the JSON, XML.
      
      beaHttp - the addess of the BEA API
    '''
    # TODO: put the payload ={} all data in lowercase, else may repeat the load (say frequency=A and Frquency = Q will load A and Q)
    # load user preferences defined in userSettings, use suggested parameters, override w fun entry
    payloadValues = {x: userSettings.userOptions[x] for x in ['UserID', 'ResultFormat']}
    payloadValues.update({'TABLENAME': tableName})
    payloadValues.update(payload)
    
    # TODO: try loading different frenquencies if no return
    #
    nipa = requests.get(beaHttp, params=payloadValues)
    
    # output format
    if outputFormat == "table":
        # TODO: check if xml or json
        return(pd.DataFrame(nipa.json()['BEAAPI']['Results']['Data']))
    elif outputFormat == "tablePretty":
        table = pd.DataFrame(nipa.json()['BEAAPI']['Results']['Data'])
        table['LineNumber'] = pd.to_numeric(table['LineNumber'])
        table['DataValue'] = pd.to_numeric(table['DataValue'])
        
        meta = table.drop(['DataValue', 'TimePeriod'], axis=1).drop_duplicates()
        meta = meta.set_index(['LineNumber', 'SeriesCode', 'LineDescription']).reset_index()
        
        table = table[['LineNumber', 'SeriesCode', 'LineDescription', 'DataValue', 'TimePeriod']]
        table = pd.pivot_table(table, index=['LineNumber', 'SeriesCode', 'LineDescription'], columns='TimePeriod', values='DataValue', aggfunc='first')
        
        return({'metadata': meta, 'table': table})
    else:
        return(nipa)