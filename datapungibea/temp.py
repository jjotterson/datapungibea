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
    output.append({'tableNames':list(set(entry[0])), 'structure':pd.DataFrame(list(zip( list(entry[1]), list(entry[2]) )),columns = ['SeriesCode','Indentation']).to_dict('records')}  )
  return(output)
#TODO: change this format: dictionary of 3 arrays: tableNames, SeriesCode and Indentations.  dump as json
  
data = dpb.data()


all = []
for section in range(1,8):
    v = data.NIPAVintage(type='main',Title = 'Section '+ str(section), releaseDate ='2018-12-12')
    all = getIndentations(v,all)

cleanAll = toDictionary(all)


#TODO:
# 1 check no table shows up as two different keys - else use try to keep trying to find the right format on the given 
#2 check all current tables have indentation info  (first get nipa parameter of tables with getParameterValues, check if the tables are somewhere in the list)


flat_list = []
for sublist in all:
    sublist = list(sublist[0])
    for item in sublist:
        flat_list.append(item)

flat_list = list(set(flat_list))

pv = data.getParameterValues('NIPA','TableName')
pv = list(pv['TableName'])


set(pv).issubset(flat_list)
set(pv).remove(set())