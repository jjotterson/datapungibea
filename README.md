<!--
TODO: add explanation of the request part of the vintage.
-->

[![image](https://img.shields.io/pypi/v/datapungibea.svg)](https://pypi.org/project/datapungibea/) 
[![build Status](https://travis-ci.com/jjotterson/datapungibea.svg?branch=master)](https://travis-ci.com/jjotterson/datapungibea)
[![downloads](https://img.shields.io/pypi/dm/datapungibea.svg)](https://pypi.org/project/datapungibea/)

[![image](https://img.shields.io/pypi/pyversions/datapungibea.svg)](https://pypi.org/project/datapungibea/)

install code: pip install datapungibea 

<h1> Datapungibea  </h1>

  Datapungibea is a python package that provides a simplified way to extract data from the U.S. Bureau of Economics Analysis (BEA).  Its main purpose is to connect to BEA's Application Program Interface (API); overall it:
  - provides a quick access to the BEA datasets **and** the python's Requests code snippet used to retrieve the data (which can be placed on a script to automate a run that is indenpendent from datapungibea).
  - returns the whole request output (with detailed metadata) **and** a cleaned up pandas table of it (with some meta).
  - goes beyond the data provided by the BEA's API to include: 
      * NIPA Vintage data
      * NIPA graph structure (indentations); and 
      * NIPA summary tables.      
  - can read a saved API key (in json/yaml files or environment variables (default)) to avoid having a copy of it on a script.
  - can automatically test: 
      * the connectivity to all BEA datasets, 
      * the quality of the cleaned up data, and 
      * if the provided requests code snippet returns the correct result. 

## Sections
  -  [Short sample runs](#Sample-runs)
  -  [Short sample runs of NIPA drivers](#Sample-runs-of-NIPA-drivers)
  -  [Short sample runs of all drivers](#Sample-run-of-all-BEA-API-drivers)
  -  [Description of a full return](#Full-request-result) 
  -  [NIPA Vintage, long description](#NIPA-Vintage)
  -  [Setting up datapungibea](#Setting-up-Datapungibea)
  -  [Testing the package](#Running-Tests) 

## Sample runs

First, [set the package up](#Setting-up-Datapungibea) (get an API key from BEA, save it somewhere and let datapungibea know its location).  After setting datapungibea up, you can run the following:

```python
'''
  Short datapungibea sample run
'''

import datapungibea as dpb

data = dpb.data() #or data = dpb.data("API Key"), see setting up section   

#Basic package description
print(data._help)                 #overall info and basic example
print(data)                       #the list of available databases
print(data._docDriver('NIPA'))    #documentation of a specific databases

#Query a database, return only pandas table:
data.NIPA('T10101')                         #default freq = Q, year = All
data.NIPA('T10101').meta                    #meta lists units, rev date, etc
data.NIPA('T10101',frequency='A',year='X')  
data.NIPA('T71800',frequency='A')           #if a query does not work, try other frequencies


#Query a database, return all information:
full = data.NIPA('T10101',verbose=true)  
full['dataFrame']           #pandas table, as above
full['request']             #full request run, see section below
full['code']                #code snippet of a request that reproduces the query. 

data._clipcode() #copy ccode to clipboard (Windows only).
```

### Sample runs of NIPA drivers

Datapungibea provides information on the NIPA data going beyond the API.  It can provide; (1) table indentations (the graph structure of the database), (2) summary of NIPA datasets, and (3) fetch vintage data.  

#### (1) NIPA indentations

A query of the NIPA API will not include the graph structure (ie. if a given line is a subcomponent of a previous line).  Datapungibea can 
enrich the dataset to include this information (the default option is to always enrich the dataset)
```python
import datapungibea as dpb

data = dpb.data()

data.NIPA('T10101',includeIndentations=False)
data.NIPA('T10101')
```


API data  | Enriched data 
--------- | ------------- 
![](https://github.com/jjotterson/datapungibea/blob/master/docs/beaQuery.png) | ![](https://github.com/jjotterson/datapungibea/blob/master/docs/enrichIndentQuery.png)    

 
#### (2) NIPA Summary tables
There are hundreds of NIPA tables.  To get an overall picture of the data, datapungibea provides a NIPASummary table for a given date; it sums up the data in the source of income and expenditures of six sectors (Domestic Income and Product Account, Private Enterprises, Personal Incomes, Government, Foreign Transactions, and Domestic Capital Account). For an example of such table, check [NIPA Summary Tables](http://www.econbrief.com/app_eb/boards/boardMacroSNATable).

```python 
import datapungibea as dpb

data = dpb.data()
data.NIPASummary('2010','A') 
```
#### (3) NIPA Vintage data
Finaly, for the NIPA database, datapungibea can also fetch vintage data (this is a quick run sample, see Section [NIPA Vintage](#NIPA-Vintage) for more):

```python

import datapungibea as dpb

data = dpb.data()

data.NIPAVintageTables()   #list the url of the vintage datasets

#T10101 Annual and Quarterly data of the first dataseet released before or on the given date.
data.NIPAVintage('T10101',Title='Section 1',releaseDate='2018-01-22') 

#tables may change name over time; so, NIPAVintage query a substring
# below, will return all tables that contain the string '10101'
data.NIPAVintage(tableName='10101',Title='Section 1', releaseDate = '2008-03-20')

#return all "final" tables in the Section of a given year quarter
data.NIPAVintage(Title='Section 1',quarter='Q1',year='2009',vintage='Third')
```

### Sample run of all BEA API drivers

Notice that all panda tables include a "meta" section listing units, short table description, revision date etc.  For more detailed metadata, use the verbose = True option (see, [Description of a full return](#Full-request-result)).  

```python
import datapungibea as dpb

data = dpb.data()

v = data.NIPA('T10101')
v.meta
```

Also, "meta" is not a pandas official attribute; slight changes to the dataframe (say, merging, or multiplying it by a number) will remove meta.


```python

import datapungibea as dpb

#start the drivers:
data = dpb.data()

#METADATA drivers                         # Use these to get: 
data.datasetlist()                        # (1) the list of BEA datasets with APIs
data.getParameterList('FixedAssets')      # (2) the parameters of a specific BEA API 
data.getParameterValues('NIPA','Year')    # (3) the options of a parameter of a BEA API 
    
#specific driver queries:
data.NIPA('T10101')
data.fixedAssets('FAAt101','X')
data.ITA('BalCurrAcct','Brazil','A','2010')
#NOTE: for IIPeither use All years of All TypeOfInvestment            
data.IIP(TypeOfInvestment='DebtSecAssets',Component='All',Frequency='All',Year='All') 
data.IIP('All','All','All','2010')              
data.GDPbyIndustry('211','1','A','2018')

#RegionalIncome and RegionalOutput were deprecated - use Regional instead.
data.getRegionalIncome.RegionalIncome()
data.getRegionalProduct.RegionalProduct()

data.InputOutput(TableID='56',Year='2010')
data.InputOutput('All','All')                       

#NOTE: Next driver's PDF and query of getParameterValues say Frequency = Q, but actually it's A
data.UnderlyingGDPbyIndustry('ALL','ALL','A','ALL') 
data.IntlServTrade('ALL','ALL','ALL','AllCountries','All')  
```

## Full request result 

When the verbose option is selected, eg:

```python
tab = data.NIPA('T10101',verbose = True)
```

A query returns a dictionary with three entries: dataFrame, request and code.  
  - dataFrame is a cleaned up version of the request result in pandas dataframe format
  - request is the full output of a request query (see the request python package)
  - code is a request code snippet to get the data that can be placed in a script 
  - (and "metadata" in some cases - listing detailed metadata)

The most intricate entry is the request one.  It is an object containing the status of the query:

```python
print(tab['request'])  #200 indicates that the query was successfull 
```

and the output:

```python
tab['request'].json()['BEAAPI']
```

a dictionary.  Its entry

```python
 tab['request'].json()['BEAAPI']['Results']
```

is again a dictionary this time with the following entries:
  
  - Statistic: the name of the table (eg, NIPA)
  - UTCProductionTime: the time when you downloaded the data
  - Dimensions: the dimensions (unit of measurement) of each entry of the dataset
  - Data: the dataset 
  - Notes: A quick description of the dataset with the date it was last revised.  


## NIPA Vintage 
  Vintage data (i.e., data as as provided in a given date without subsequent updates) are not provided
by the BEA's APIs and have to be retrived using less reliable methods.  Overall, vintage data is costly to load because they are aggregated by:

  - **Title** :  Section 1 to Section 8 (default to empty)
  - **year** :  the year of the data release (default to empty)
  - **quarter** :  the quarter of the data release (default to empty)
  - **type** :  main, underlyning, MilsOfDollars.  (Defaults to main.)
  - **vintage** :  Third, Second, Advance (default empty)

 Hence, any query will always first download all the data at this level.  Often, there will be more than 100s of tables even after specifying the above parameters.  So, it is a good idea to specify as many of them as possible. For example, there still remains to specify the NIPA table (eg T10101) and its frequency (annual, monthly or yearly data). 

Hence, unless using a powerful computer, **do not** run:
```python
     #data.NIPAVintage()
     #data.NIPAVintage('T10101')
```
since it will try to load all main data (around 6GB of data).  

Remark: Instead of specifying the year, quarter and 
vintage (Advance, Second, quarter) of the data, the query can also be made using 

  - **releaseDate**:  a string such as "2010-01-22", or a datetime object as datetime.now()

The driver will look for the first available data (that is, year, quarter, vintage) on or prior to the given date (hence, this is the latest dataset available to a person at the given time).

After retrieving the datasets, the method can query the tables and only keep the cases of interest.
The user can specify:
  
  - **tableName**: eg T10101 (it searches for substrings, can use 10101 since table names change over time, as in the example - T10101 in 2018 but 10101 in 2008)
  - **frequency**: A, Q or M 

The example below loads data at very aggregate level and then keeps the cases with tableName and frequency
```python
import datapungibea as dpb

data = dpb.data()

print(data._docDriver('NIPAVintage'))    #list the args and default options of this method.
out1 = data.NIPAVintage(tableName = 'T10101',frequency='Q',Title='Section 1',releaseDate='2018-01-01')
out2 = data.NIPAVintage(tableName = '10101', frequency='Q',Title='Section 1',releaseDate='2008-01-01')
```    
## Setting up Datapungibea 

To use the BEA API, **the first step** is to get an API key from the BEA: 

* https://apps.bea.gov/API/signup/index.cfm

There are three main options to pass the key to datapungibea:

#### (Option 1) Pass the key directly:
```python
import datapungibea as dpb

data = dpb.data("BEA API KEY")

data.NIPA('T10101')
```

#### (Option 2) Save tke key in either a json or yaml file and let datapungibea know its location:

 sample json file : 
```python
    {  
         "BEA": {"key": "**PLACE YOUR KEY HERE**", "url": "https://apps.bea.gov/api/data/"},
         (...Other API keys...)
    }
```
sample yaml file:

```yaml
BEA: 
    key: PLACE BEA API KEY HERE
    description: BEA data
    url: https://apps.bea.gov/api/data/
api2:
    key:
    description:
    url:
```

Now can either always point to the API location on a run, such as:

```python
import datapungibea as dpb   
    
userSettings = {
   'ApiKeysPath':'**C:/MyFolder/myApiKey.yaml**', #or .json
   'ApiKeyLabel':'BEA',
   'ResultFormat':'JSON'
}   

data = dpb.data(userSettings = userSettings)  
data.NIPA('T10101')
```

Or, save the path to your BEA API key on the package's user settings (only need to run the utils once, datapungibea will remember it in future runs):


```python
import datapungibea as dpb

dpb.utils.setUserSettings('C:/Path/myKeys.yaml') #or .json

data = dpb.data()
data.NIPA('T10101')
```

#### (Option 3) Save the key in an environment variable

Finally, you can also save the key as an environment variable (eg, windows shell and in anaconda/conda virtual environment).   

For example, on a command prompt (cmd, powershell etc, or in a virtual environment)

```
> set BEA=APIKey 
```

Then start python and run:

```python
import datapungibea as dpb

data = dpb.data()
data.NIPA('T10101')
```

Notice: searching for an environrment variable named 'BEA' is the deafault option.  If changed to some other option and want to return to the default, run:

```python
import datapungibea as dpb

dpb.utils.setUserSettings('env')  
```

If you want to save the url of the BEA API in the environment, call it BEA_url. Datapungibea will use the provided http address instead of the default 

> https://apps.bea.gov/api/data/

### Changing the API key name
  By default, datapungibea searches for an API key called 'BEA' (in either json/yaml file or in the environment).  In some cases, it's preferable to call it something else (in conda, use BEA_Secret to encript it).  To change the name of the key, run

  ```python
  import datapungibea as dpb
  
  dpb.utils.setKeyName('BEA_Secret')  #or anyother prefered key name
  ```
  When using environment variables, if saving the API url in the environment as well, call it KeyLabel_url (for example, 'BEA_Secret_url'). Else, datapungibea will use the default one.
  
## Running Tests

Datapungibea comes with a family of tests to check its access to the BEA API and the quality of the retrieved data.  They check if:

1. the connection to BEA is working,
2. the data cleaning step worked,
3. the code snippet is executing (**NOTE: currently only working when keys are stored in a json file**),
4. the code snippet produces the same data as the datapungi query.

Other tests check if BEA data has being updated of if new data is available.  Most of these tests are run every night on python 3.5, 3.6 and 3.7 (see the code build tag on the top of the document).  However, 
these test runs are not currently checking the code snippet quality to check if its output is the same as the driver's. To run the tests, including the one 
that checks code snippet quality, type:

```python
import datapungibea as dpb

dpb.tests.runTests(outputPath = 'C:/Your Path/')
```

This will save an html file in the path specified called datapungibea_Tests.html

You can save your test output folder in the user settings as well (need / at the end):

```python
import datapungibea as dpb

dpb.utils.setTestFolder('C:/mytestFolder/')
```


## References 

- https://apps.bea.gov/API/signup/index.cfm
- https://2.python-requests.org//en/master/
