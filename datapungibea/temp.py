import datapungibea as dpb 


def whereIn(arr,entry):
  try:
    output = arr.index(entry)
  except:
    output = -1
  return(output)


def getIndentations(queryResults,all=[]):
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

def toDictionary(indentArrayTuples):
  output = [] 
  for entry in indentArrayTuples:
    output.append({'tableNames' : entry[0],'structure' : pd.DataFrame(list(zip( list(entry[1]), list(entry[2]) )),columns = ['SeriesCode','Indentation']).to_dict('records')}
  return(output)

  
data = dpb.data()

v = data.NIPAVintage(type='main',Title = 'Section 1', releaseDate ='2018-12-12')