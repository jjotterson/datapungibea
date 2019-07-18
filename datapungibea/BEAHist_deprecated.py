import pandas as pd              #
import numpy as np               # 
import requests as rq            # get json
import bs4 as bs                 # scraping websites
import urllib.request            # work/connect to url    
import re                        # regular expression
from datetime import datetime
import json
import gzip
import sys
import pickle
import zlib 
from base64 import b64encode, b64decode

#import datetime 
#from CFGBeaHist import *        # get basic config.




def urlNIPAHistQYVintage( 
        NIPAHistUrl  = 'https://apps.bea.gov/histdata/histChildLevels.cfm?HMI=7', #location of table of historical databases
        histUrl      = 'https://apps.bea.gov/histdata/',                          #missing part of the historical database https 
        replaceSpaceWith = "%20"
    ):
    '''
     Table of the url of the Quarter Year Vintage Data

     Inputs:
       NIPAUrl a string poiting to the site of NIPA historical data.  For each quater, vintage, release data,
     it gives a link to the historical NIPA data (missing the mainUrl part)
     
     replaceSpaceWith %20 is because certain pages will load open without this correction
     
     Output:
       Returns a table listing the name, vintage, time units of the historical data and their http links 
       These are not links to data, but a place that points to excel tables (the output of interest).
    '''    
    #connect to main BEA Historical table and get tables
    source = urllib.request.urlopen( NIPAHistUrl ).read()
    soup = bs.BeautifulSoup( source, 'lxml' )
    htable = soup.table
    
    #get the main table and standardize its entries ('1. Advance' vs 'Advance' in lines etc)
    dfUrlQYVintage = pd.read_html( str( htable ), header = 1)[1]  #get the table entries, could go to the html directly.
    dfUrlQYVintage.columns = ['yearQuarter','vintage','releaseDate']
    dfUrlQYVintage['vintage'] = dfUrlQYVintage['vintage'].apply( lambda x: re.sub('.\. ','',x) )  
    dfUrlQYVintage['vintage'] = dfUrlQYVintage['vintage'].apply( lambda x: re.sub('Final','Third',x) )
    dfUrlQYVintage['vintage'] = dfUrlQYVintage['vintage'].apply( lambda x: re.sub('Preliminary','Second',x) )
    dfUrlQYVintage['vintage'] = dfUrlQYVintage['vintage'].apply( lambda x: re.sub('Initial','Advance',x) )
    
    #get hrefs from the loaded table
    links = []
    for link in htable.table.find_all('tr'):
        #links.append(link)
        aux = link.a        
        if aux != None:
            links.append(aux.get('href'))
    
    dfUrlQYVintage['vintageLink'] = links
    dfUrlQYVintage['vintageLink'] = dfUrlQYVintage['vintageLink'].apply( lambda x: (histUrl+x).replace(" ", replaceSpaceWith) )  #appends the main url bc the link given misses this part
    
    return( dfUrlQYVintage )

def urlNIPAHistQYVintageMainOrUnderlSection( 
          LineOfdfUrlQYVintage,                    #a line of the table output of  urlNIPAHistQYVintage
          beaUrl = 'https://apps.bea.gov/'      
    ):
    '''
       From the url of quarter year vintage data (see urlNIPAHistQYVintage) make a table of the url of the 
        quarter year vintage type (main/underlying etc) and section
       The output urls point to excel tables.        
    '''  
       
    source = urllib.request.urlopen( LineOfdfUrlQYVintage['vintageLink'] ).read()
    soup   = bs.BeautifulSoup( source, 'lxml' )
    htable = soup.body.find_all('table')
    
    outValues = []
    for table in htable: #this will skip tables that don't have headings
      try: 
        dftab =  pd.read_html( str(table) , header = 1 )[0]
        auxlink = list( map( lambda x: x.get('href'), table.find_all('a') ))
        #links.append( [auxlink] )
        dftab['excelLink'] = list(map(lambda x: beaUrl+x ,auxlink))    #here replace " " with %20
        if not dftab.empty:
          for key in LineOfdfUrlQYVintage: 
              dftab[key] = LineOfdfUrlQYVintage[key] 
          outValues.append(dftab)
      except:
        pass
     
    if len(outValues) == 3:      #Varies a lot, some years have three tables (main, FA / Millions, underlying, other years 1 (main)                                             
      output = dict(zip( ['main','FAorMillions','underlying'], outValues ))
    elif len(outValues) == 2:
      output = dict(zip( ['main','underlying'], outValues ))
    else:
      output = dict(zip( ['main'], outValues ))
    
    return(output)


def getAllLinksToHistTables(readSaved = False):
    '''
      Concatenate the tables of the excel data urls.

      If readSaved = True, will read the pre-saved data
    '''
    
    if readSaved == True:
      urlOfExcelTables = pd.read_json('I:/Jamesot/Projects/outside/beafullfetchpy/beafullfetchpy/data/NIPAUrlofExcelHistData.json',orient="records")  #TODO: fix this, need to include Manifest.in
      return( urlOfExcelTables )
     
    dfUrlQYVintage = urlNIPAHistQYVintage()
    
    urlOfExcelTables = pd.DataFrame()
    for line in range(len(dfUrlQYVintage)):
        LineOfdfUrlQYVintage = dfUrlQYVintage.to_dict('records')[line]
        out = urlNIPAHistQYVintageMainOrUnderlSection( LineOfdfUrlQYVintage )
        
        for type in out:
          out[type]['type'] = type
        
        urlOfExcelTables = pd.concat([urlOfExcelTables] + list(out.values()),sort=False)
       
    return( urlOfExcelTables )

def getNIPADataFromListofLinks( tableOfLinks , asJson = False):
    '''
      
    '''
    nipaData = tableOfLinks.to_dict(orient='records')
    count = 0 
    for row in nipaData:
        link = row['excelLink']
        if asJson == False:
            try:
                row['data'] = pd.read_excel(link.replace(" ","%20"), sheet_name=None)
            except:
                try:
                    row['data'] = pd.read_excel(link.replace(" ","%20"), sheet_name=None) 
                except:   
                    print("cannot read: " + link)
        else:
            try:
                row['data'] = pd.read_excel(link.replace(" ","%20"), sheet_name=None).to_dict(orient='records')
            except:
                try: 
                    row['data'] = pd.read_excel(link.replace(" ","%20"), sheet_name=None).to_dict(orient='records')
                except:
                    print('cannot read: ' + link)
        count = count + 1    
        if count%250 == 0:
          print( 'got item '+ str(count) )
    return( nipaData )

#def getHistTable( tableName, yearQuarter, vintage = "Third", timeUnit = "Q", cfg = cfg ):
#    sectionNum = tableName[1]
#    r = re.compile( tableName.replace('T','') + '.*' + timeUnit )  #will search for sheet names with this regex.
#    maindf  = urlNIPAHistQYVintage( cfg['NIPAHistUrl'], cfg['histUrl'] )
#    dfline  = maindf[ (maindf.yearQuarter == yearQuarter) & (maindf.vintage == vintage) ]
#    excelLinks = NIPAHistExcelLinks( dfline , cfg['beaUrl'] )['main']
#    dfExcelSelected = excelLinks[ excelLinks.Title.str.contains('Section {}'.format(sectionNum)) ]
#    
#    output = pd.DataFrame()
#    if dfExcelSelected.empty:
#       print("Table does not exist in time period!")
#       return( output )
#    
#    #for now, will only get the Section x data, not the Section x (Pre) (pre 1969) that might exist
#    #to do: when (pre) exist open and concatenate it.
#    exLink = excelLinks[ excelLinks.Title == 'Section {}'.format(sectionNum) ].excelLink.tolist()[0]
#    excelAll = pd.read_excel( exLink, None)  #get all tables
#    
#    table = excelAll[ list( filter( r.match, excelAll.keys()) )[0] ]
#    
#    #get metadata (date range for now):
#    #r2 = re.compile('.* data from .* To .*'.lower())
#    #vv = table.iloc[:,0].astype(str).str.lower().tolist()
#    #dates = list( filter( lambda x: r2.match(x), vv  ) )[0]
#    
#    #clean up the table.
#    table = table[ table.iloc[:,2].notna() ].iloc[:,2:]
#    table = table.rename(columns={ table.columns[0]: 'variable' }).set_index('variable')
#    table = table.apply(pd.to_numeric, errors='coerce')
#    table = table.dropna( how = 'all' ) 
#    
#    #put dates
#    Nobs = table.shape[1]
#    if timeUnit == 'Q':
#      ffreq = 'QS' #else will end a quarter before...
#    
#    dateRange = list( pd.date_range(end=yearQuarter.replace(', ',''), periods=Nobs,freq=ffreq ) )
#    dates = pd.PeriodIndex( dateRange, freq = timeUnit)
#    
#    table.columns = dates
#    return(table)
#

def getAndSaveData(range,filename,excelTables, quiet = True):
    tableRange = excelTables.iloc[range]
    
    fullnipaData = getNIPADataFromListofLinks(tableRange)
    
    serialized = pickle.dumps(fullnipaData)
        
    with open(filename,'wb') as file_object:
        file_object.write(serialized)
     
    if quiet == False:
        print( "finished loading!")
        print(range)

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
        list(rawIn),
        [re.sub(" |-", "_", entry).replace('Qtr', 'Q').replace('Month', 'M').replace('Ann', 'A').strip() for entry in list(rawIn)]
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



if __name__ == '__main__':
    #cfg = {
    #   'beaUrl'   : 'https://apps.bea.gov/',
    #   'histUrl'  : 'https://apps.bea.gov/histdata/',
    #   'NIPAHistUrl'  : 'https://apps.bea.gov/histdata/histChildLevels.cfm?HMI=7',
    #}
    #dfUrlQYVintage = urlNIPAHistQYVintage()
    #LineOfdfUrlQYVintage = dfUrlQYVintage.to_dict('records')[line]
    #out = urlNIPAHistQYVintageMainOrUnderlSection( LineOfdfUrlQYVintage )
    #
    #excelTables = getAllLinksToHistTables()
    #excelTables = excelTables[['index', 'yearQuarter', 'vintage', 'Title', 'Details', 'type', 'releaseDate', 'vintageLink', 'excelLink']]
    #excelTables.to_json('data/NIPAUrlofExcelHistData.json',orient="records")  #todo: fix this file pointer.
    excelTables = getAllLinksToHistTables(readSaved=True)

    #downloads all NIPA hist excels from web in batch mode
    #for i in range(int(sys.argv[1]),int(sys.argv[1])+1000):
    #    rr = range( i, i+1 )
    #    filename = 'beafullfetchpy/beaData/beaHist' + str(i)
    #    getAndSaveData(rr, filename, excelTables)
    #    i = i + 1
    #    if i % 100 == 1:
    #        print( i )


    #get downloaded data, format and save
hfail = []
for k in range(260,4424):
    try:
        filename = 'beafullfetchpy/beaData/beaHist' +str(k)
        with open(filename,'rb') as file_object:
            raw_data = file_object.read()
        
        beaHistRaw = pickle.loads(raw_data)
        outFilename = 'beafullfetchpy/beaDataClean/' +  re.sub("[\w]*/","",filename) + "_"  #TODO: replace BeaHistn by vintage date
        raw = beaHistRaw[0]['data']
        tab = formatBeaRaw(raw, outputFormat='gzip', save='tablewise', saveAs=outFilename)
    except:
        hfail.append(k)

    print(tab.keys())
    print(tab[list(tab.keys())[0]]['Data'].head())
    print(tab[list(tab.keys())[1]]['Data'].head())



    
#case 510, 511