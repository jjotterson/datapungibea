import pandas as pd              #
import numpy as np               # 
import requests as rq            # get json
import bs4 as bs                 # scraping websites
import urllib.request            # work/connect to url    
import html5lib
import re                        # regular expression
from datetime import datetime
import json
import sys

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
    dfUrlQYVintage = pd.read_html( str( htable ), encoding='utf-8',header = 0)[1]  #get the table entries, could go to the html directly.
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
        else:
            pass
            
    
    
    #NOTE: maybe the most stable way is to work 
    #df['href'] = [np.where(tag.has_attr('href'),tag.get('href'),"no link") for tag in tb.find_all('a')]
    
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
        dftab =  pd.read_html( str(table) , header = 0 )[0]
        auxlink = list( map( lambda x: x.get('href'), table.find_all('a') ))
        #links.append( [auxlink] )
        dftab['excelLink'] = list(map(lambda x: beaUrl+x ,auxlink))    #here replace " " with %20
        if not dftab.empty:
          for key, entry in LineOfdfUrlQYVintage.items(): 
              dftab[key] = entry
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
    
    #Get the location of the datasets with same Q-Y  
    dfUrlQYVintage = urlNIPAHistQYVintage()
    
    #Load all data in the given location
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



if __name__ == '__main__':

    listTables = urlNIPAHistQYVintage( )
    print(listTables)
    urlData = urlNIPAHistQYVintageMainOrUnderlSection( listTables.iloc[0] )
    print(urlData)
    allLinks = getAllLinksToHistTables()
    print(allLinks)