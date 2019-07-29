'''
  Script that generates indentation information of NIPA tables.
'''
import datapungibea as dpb 
import pandas as pd
from datetime import datetime
from datapungibea import drivers


def whereIn(arr,entry):
  '''
    a helper, given an array and an entry, return where it's located or -1 if not. 
  '''
  try:
    output = arr.index(entry)
  except:
    output = -1
  return(output)


def getIndentations(queryResults,all=[]):
    '''
      From a query of NIPAVintage, get all indentations, and only include information if it was not previously available (hence, unsing tuples to be able to compare)
      If the result of a query and a previous indentation data (all) is passed, will include info to the output only if finds new information.
    '''
    if all == []:
        allrest = []
    else:
      allrest = [tup[1:] for tup in all] #drop table names of all
    
    for entry in queryResults:
      b = tuple([ tuple(entry['SeriesCode']), tuple(entry['Indentations'])   ] )
      test = whereIn(allrest,b)
      if test < 0:
        a = tuple([ tuple([entry['tableName'].iloc[0]]), tuple(entry['SeriesCode']), tuple(entry['Indentations']) ] )
        all.append(a)
        allrest.append(b)
      else:
        a = tuple([ tuple(set(all[test][0] + tuple([entry['tableName'].iloc[0]]))), tuple(entry['SeriesCode']), tuple(entry['Indentations']) ] )
        all[test] = a
    
    return(all)

def getIndentationsInVintage(releaseDate = datetime.now() ):
    '''
      Fix a releaseDate, read all tables of that vintage and get its indentation tables.
    '''
    nvDriver = drivers.getNIPAVintage()
    all = []
    for section in range(1,10):
        v = nvDriver.NIPAVintage(type='main',Title = 'Section '+ str(section), releaseDate = releaseDate)
        all = getIndentations(v,all)
    return(all)

def checkHaveAllTables(all):
    '''
      After collecting all indentation tables of a vintage, check that have all tables in current NIPA on that list.
    '''
    tableNamesWithIndention = []
    discard = [tableNamesWithIndention.extend(x[0]) for x in all]
    tableNamesWithIndention = set(tableNamesWithIndention)
    
    #get name of current nipa tables
    driver = drivers.getGetParameterValues()
    pv = driver.getParameterValues('NIPA','TableName')
    pv = list(pv['TableName'])  
    
    #check if got the indentation of all tables 
    gotAllTables = set(pv).issubset(tableNamesWithIndention)
    
    return(gotAllTables)

def toDictionary(indentArrayTuples,divideBy=2,firstZero=True):
  '''
    Given something in the format of the output of getIndentations, put in array of dictionaries with tuple entries.
    This is something do to at the end; it's hard to compare dictionaries.  
    -divideBy = 2, indentations seem to be in multiples of 2, write as multiples of 1.  TODO: check no fractions.
    -firstZero = first line of table should have zero indentation (apparently it's written as a title - centralized)
  '''
  def modifyIndent(x):
      x = list(x)
      if divideBy > 1:
        canDiv = max( [e%divideBy for e in x])
        if canDiv == 0:
          x = [int(e/2) for e in x]
      if firstZero == True:
        x[0] = 0
      return(tuple(x))
   
  output = [ {'tableName':x[0], 'SeriesCode':x[1],'Indentations':modifyIndent(x[2])} for x in indentArrayTuples]
  #for entry in indentArrayTuples:
  #  output.append({'tableNames':list(set(entry[0])), 'structure':pd.DataFrame(list(zip( list(entry[1]), list(entry[2]) )),columns = ['SeriesCode','Indentation']).to_dict('records')}  )
  return(output)

if __name__ == '__main__':
    '''
      Get indentation information of NIPA tables using last available Vintage information.
    '''
    
    all = getIndentationsInVintage(releaseDate = '2018-12-12')
    print('Got indentation tables for all current tables: ', checkHaveAllTables(all))
    dict_out = toDictionary(all)
    print(dict_out)