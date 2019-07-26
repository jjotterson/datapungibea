def formatBeaRaw( rawIn, outputFormat = 'dict', save = 'no', saveAs = '' ):
    '''
      Raw is the pandas reading of the BEA excel table (has all sheets).
      output formats (note, all compressed outputs are of json format):  #TODO: separate format (dict/json vs pandas) from compression
        - (dict) dictionary in a format close to json
        - (dictPandas) dictionary where tables are in Pandas format
        - (json)
        - (zlib64) zlib compression of json followed by b64econde  
                   to decompress use json.loads(zlib.decompress(b64decode( variable  )))  
        - (gzip)   gzip compression of json
        - (pickle) pickle compression of json
      save: 
        - 'no'    - will not save the output
        - 'block' - will save all tables in the raw together
        - 'tablewise' - saves each table separatedly, will append table names to the saveAs string
    '''
    #fix table names:
newRawKeys = dict(zip(
    [re.sub(" |-", "_", entry).replace('Qtr', 'Q').replace('Month', 'M').replace('Ann', 'A').strip() for entry in list(rawIn)],
    list(rawIn)
))
    raw = { newRawKeys[entry] : rawIn[entry]   for entry in newRawKeys  }
    Results = {}
    for x in raw:
        
        if x == 'Contents':
            continue 
        
        Results[x] = {}
        table = raw[x].copy()
        #fix the case when the quarter or month is listed on a separated line
        if table.iloc[7,:].isna()[0] == True and table.iloc[7,:].isna()[1] == True:
            freq = x[-1]  #Q, A, or M
            table.iloc[6, 3:] = [ (str(x[0]) + freq + str(x[1])).replace('.0','') for x in zip(table.iloc[6, 3:], table.iloc[7, 3:])]
            table.drop(table.index[7],inplace = True)
        #Results -- Data, Statistic (NIPA Table), UTCProductionTime (now), Notes, and Dimensions ##########################
        #
        Results[x]['Notes'] = {
            'NoteRef': re.sub('-.$|Qrt$|Annual|A$|M$','',x).strip(" "),     #TODO remove -A, Qtr, -Q etc -M
            'NoteText': " - ".join( [table.columns[0]] + [ str(entry) for entry in list(table.iloc[:5,0])] )   #TODO: replace nan with ''
        }
        #main data and footnote comments
        dataTab = table.iloc[7:]  #TODO: check when quarters are indicated in the next line
        #column names
        colNames = list(table.iloc[6])
        colNames[1] = 'LineDescription'
        colNames[2] = 'SeriesCode'
        colNames = list(map(lambda x: str(int(x)) if not isinstance(x,str) else x , colNames)  ) #all columns as strings.
        dataTab.columns = colNames
        dataTab.reset_index(drop=True,inplace=True)
        
        #store footnotes on the notes part of the results
        footnotes = list( dataTab.loc[dataTab['LineDescription'].isnull() & dataTab['Line'].notnull()].iloc[:, 0] )
        Results[x]['Notes']['Footnotes'] = dict(zip(range(1,1+len(footnotes)),footnotes))
        dataTab = dataTab.loc[dataTab['LineDescription'].notnull()]
        
        #include graph structure:
        indents = dataTab.LineDescription.map(lambda x: len(x) - len(x.lstrip(' '))) 
        dataTab.insert(3, 'Indentations', indents)
        
        #save table structure
        Results[x]['Notes']['TableStructure'] = dataTab.reset_index().iloc[:,:5].fillna('').to_dict('list')
        
        #clean up table
        #remove subsection headings (these have no data)
        dataTab = dataTab.loc[dataTab['SeriesCode'].notna()]
        
        dataTab.LineDescription = dataTab.LineDescription.map(lambda x: re.sub('\\\\.\\\\', '', x) )
        dataTab.LineDescription = dataTab.LineDescription.map(lambda x: re.sub('[\w]*:','',x))  #removes Less:, Equals:...
        dataTab.LineDescription = dataTab.LineDescription.map(lambda x : x.lstrip(" "))  #do this last to avoid the case when space is created
        
        #reshape data and save
        outData = pd.melt(dataTab, id_vars=['Line', 'LineDescription', 'SeriesCode', 'Indentations'],var_name= 'TimePeriod',value_name = 'DataValue' )
        outData.DataValue = pd.to_numeric(outData.DataValue, errors = 'coerce').map(lambda x: str(x))  #values are as strings, here removed non numbers as .....
        if outputFormat == 'dictPandas':  #TODO: just reshape the above data (so, assure numeric) data if not returning pandas
            outData = dataTab
        outData.rename(index=str, columns={'Line': 'LineNumber'},inplace=True)
        outData.insert(0, 'TableName', re.sub('_.$|Qrt$|Annual|A$|M$','',x).strip(" ") )
        #outData.insert(len(outData.keys()),'UNIT_MULT',0)    #TODO check T10101, always 0, as in many other cases.  Bit costly to save these UNIT_Mult, CL data.
        #outData.insert(len(outData.keys()), 'CL_UNIT', table.iloc[0,0])  # TODO check, T10101: CL_UNIT Percent change, annual rate
        #outData.insert(len(outData.keys()), 'CL_UNIT', 0)  # check   TODO: this is missing example of T10101: METRIC_NAME Fisher Quantity Index
        
        if outputFormat == "dictPandas":
            Results[x]['Data'] = outData
        else:
            Results[x]['Data'] = outData.to_dict("list")  #maybe too big outData.to_dict(orient='records')
        
        Results[x]['UTCProductionTime'] = str(datetime.now()).replace(" ","T")
        Results[x]['Statistic'] = "NIPA Table"
        Results[x]['Dimensions'] = [
            {'Ordinal': '1', 'Name': 'TableName', 'DataType': 'string', 'IsValue': '0'},
            {'Ordinal': '2', 'Name': 'SeriesCode', 'DataType': 'string', 'IsValue': '0'},
            {'Ordinal': '3', 'Name': 'LineNumber', 'DataType': 'numeric', 'IsValue': '0'},
            {'Ordinal': '4', 'Name': 'LineDescription', 'DataType': 'string', 'IsValue': '0'},
            {'Ordinal': '5', 'Name': 'Indentations', 'DataType': 'numeric', 'IsValue': '0'},
            {'Ordinal': '6', 'Name': 'TimePeriod', 'DataType': 'string', 'IsValue': '0'},
            #{'Ordinal': '7', 'Name': 'CL_UNIT', 'DataType': 'string', 'IsValue': '0'},
            {'Ordinal': '8', 'Name': 'UNIT_MULT', 'DataType': 'numeric', 'IsValue': '0'},
            {'Ordinal': '9', 'Name': 'METRIC_NAME', 'DataType': 'string', 'IsValue': '0'},
            {'Ordinal': '10', 'Name': 'DataValue', 'DataType': 'numeric', 'IsValue': '1'}
            ]
        
    #Put in final format (and save or return)  #TODO: refactor this part, also,include the option of saving the tables separateldy
    if outputFormat == 'dict':
        output = Results
        if save == 'block':
            #with open( saveAs, 'w') as outfile:
            #    outfile.write(output)
            print("Not Saved! Choose pickle to save.")
            pass
        elif save == "tablewise":
            #for entry in output:
            #    with open( saveAs + entry.replace("-","_"), 'w') as outfile:
            #        outfile.write(output)
            print("Not Saved! Choose pickle to save.")
            pass    
        else:
            return(output)
    
    if outputFormat == 'dictPandas':
        output = Results
        if save == 'block':
            #with open( saveAs, 'w') as outfile:
            #    outfile.write(output)
            print("Not Saved! Choose pickle to save.")
            pass
        elif save == "tablewise":
            #for entry in output:
            #    with open( saveAs + entry.replace("-","_"), 'w') as outfile:
            #        outfile.write(output)
            print("Not Saved! Choose pickle to save.")
            pass    
        else:
            return(output)
     
    if outputFormat == 'zlib64':
        output = Results        
        if save == 'block':
            outputF = json.dumps(output) 
            outputF = zlib.compress(outputF.encode('utf-8'))
            outputF = b64encode(outputF)
            outputF = outputF.decode('ascii')
            with open( saveAs, 'w') as outfile:
                outfile.write(outputF)
            pass
        elif save == "tablewise":
            for entry in output:
                outputF = json.dumps(output[entry]) 
                outputF = zlib.compress(outputF.encode('utf-8'))
                outputF = b64encode(outputF)
                outputF = outputF.decode('ascii')
                with open( saveAs + entry.replace("-","_"), 'w') as outfile:
                    outfile.write(outputF)
            pass    
        else:
            outputF = json.dumps(output) 
            outputF = zlib.compress(outputF.encode('utf-8'))
            outputF = b64encode(outputF)
            outputF = outputF.decode('ascii')
            return(outputF)
    
    if outputFormat == 'gzip':
        output = Results
        if save == 'block':
            outputF = json.dumps(output) 
            outputF = bytes(outputF,'utf-8')
            with gzip.open( saveAs+'.txt.gz', 'wb') as outfile:
                outfile.write(outputF)
            pass
        elif save == "tablewise":
            for entry in output:
                outputF = json.dumps(output[entry]) 
                outputF = bytes(outputF,'utf-8')
                with gzip.open( saveAs + entry.replace("-","_")+".txt.gz", 'wb') as outfile:
                    outfile.write(outputF)
            pass    
        else:
            outputF = json.dumps(output) 
            outputF = bytes(outputF,'utf-8')
            return(gzip.compress(outputF))
      
    if outputFormat == 'json':
        output = Results
        if save == 'block':
            outputF = json.dumps(output) 
            with open( saveAs+'.json', 'w') as outfile:
                outfile.write(outputF)
            pass
        elif save == "tablewise":
            for entry in output:
                outputF = json.dumps(output[entry]) 
                with open( saveAs + entry.replace("-","_")+".json", 'w') as outfile:
                    outfile.write(outputF)
            pass    
        else:
            outputF = json.dumps(output) 
            return(outputF) 
     
    if outputFormat == 'pickle':
        output = Results
        if save == 'block':
            outputF = output 
            with open( saveAs+'.pickle', 'wb') as outfile:
               pickle.dump(outputF,outfile,protocol=pickle.HIGHEST_PROTOCOL)
            pass
        elif save == "tablewise":
            for entry in output:
                outputF = output[entry]
                with open( saveAs + entry.replace("-","_")+".pickle", 'wb') as outfile:
                    pickle.dump(outputF,outfile,protocol=pickle.HIGHEST_PROTOCOL)
            pass    
        else:
            outputF = pickle.dumps(output,protocol=pickle.HIGHEST_PROTOCOL)
            return(outputF)      
