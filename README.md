[![image](https://img.shields.io/pypi/v/requests.svg)](https://pypi.org/project/datapungibea/) 

install code: pip install datapungibea 

<h1> Datapungibea  </h1>

  Datapungibea is a python package that provides a simplified way to extract data from the U.S. Bureau of Economics Analysis (BEA).  Its main purpose is to uses the 
  Application Program Interface (API) provided by the BEA and access it using Requests, a main python HTTP package. Usually, getting data via APIs are better
  than web scrapping or manual downloads from a website since they provides a reproducible direct access to data.   
  
  Datapungibea has the following features:
  - it provides a quick access to the BEA datasets, but at the same time provides the Requests code snippet used to retrieve the data (which can be placed on a user script for reproducibility).
  - it outputs the whole request output (which includes metadata), but it also provides a cleaned up version, in python pandas format, of the requested dataset.
  - it goes beyond the data provided by the BEA's API to include: 
      * NIPA vintage data; 
      * NIPA graph structure (indentations); and 
      * NIPA summary tables.      
  - it provides a simplified management (update and read) of the user access keys (user API keys) to avoid having a copy of the key on a user script.
  - it can automatically test: 
      * the connectivity to all BEA datasets, 
      * the quality of the cleaned up data, and 
      * the validity of the provided requests code to be placed in a user's script. 

<h2> Sample runs </h2>

After setting the package up (see **Setting Up** section, the main step is to get an API key from BEA, save it somewhere and let datapungibea know about its location), you can run the following:

    import datapungibea as dpb
    
    #Step 0: follow the Setting Up section below (basically, you need to get a key from BEA 
    #save it somewhere or pass it to the app in a given session)

    #Step 1: load user keys, start the connections to the databases (drivers, eg NIPA)
    data = dpb.data()                 
    
    #else, you can either let datapungibea know about the location of the key during the session only:
    #see, the Setting UP section below for the format of the json file containing the key).
    #data = dpb.data(userSettings = {"ApiKeysPath": "Path/yourFile.json", "ApiKeyLabel": "BEA", "ResultFormat": "JSON"} )

    #or pass the key direclty:
    #data = dpb.data({"key": "your key", "url": "https://apps.bea.gov/api/data/"})
    

    #Step 2: start loading data - here is some documentation on doing this:
    print(data._help)                 #overall info on datapungibea plus an example of a request
    print(data)                       #the list of datasets datapungi can query (the 'drivers'), eg 'NIPA'
    print(data._docDriver('NIPA'))    #prints the documentation of a given driver
    
    #query of an API dataset (13 drivers):
    data.NIPA('T10101')               #Query the dataset.  The output is a pandas dataframe. 
                                      #Note: for the NIPA driver, it will enrich the dataset to include 
                                      #missing indentations (NIPA's graph structure).
    data.NIPA('T10101',frequency='A',year='X',includeIndentations=False) 
    #Note: see 
    print(data._docDriver('NIPA')) 
    #for the other driver input options.
    
    #to get the full information, select the verbose option of a driver:
    full = data.NIPA('T10101',verbose=true)  
    full['dataFrame']                 #the cleaned up dataframe, as above
    full['request']                   #the output of the request run (see the python Request package)
    full['code']                      #a code snippet of a request run that reproduces the query. 

    ## To copy the requests code snippet to clipboard (Windows), run:
    data._clipcode()

    #to get a high level summary of all NIPA information, run:
    #NOTE: this is not an BEA API 
    data.NIPASummary('2010','A')

<h3>Sample run of NIPA Vintage methods </h3>
  Quick example (see section below for more):

      import datapungibea as dpb
      
      data = dpb.data()

      data.NIPAVintageTables()   #list the url of the vintage datasets
      
      #T10101 Annual and Quarterly data of the last dataseet released before or on the given date.
      data.NIPAVintage('T10101',Title='Section 1',releaseDate="2018-01-22') 
      
      #tables may change name over time; so, NIPAVintage query a substring
      # below, will return all tables that contain the string '10101'
      data.NIPAVintage(tableName='10101',Title='Section 1', releaseDate = '2008-03-20')
      
      #return all "final" tables in the Section of a given year quarter
      data.NIPAVintage(Title='Section 1',quarter='Q1',year='2009',vintage='Third')

<h3>Sample run of all BEA API drivers</h3>

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
    data.IIP(TypeOfInvestment='DebtSecAssets',Component='All',Frequency='All',Year='All') #NOTE: for IIP, either use All years of All TypeOfInvestment            
    data.IIP('All','All','All','2010')              
    data.GDPbyIndustry('211','1','A','2018')
    
    #RegionalIncome and RegionalOutput were deprecated - use Regional instead.
    data.getRegionalIncome.RegionalIncome()
    data.getRegionalProduct.RegionalProduct()
    
    data.InputOutput(TableID='56',Year='2010')
    
    data.InputOutput('All','All')                       
    data.UnderlyingGDPbyIndustry('ALL','ALL','A','ALL') #NOTE: PDF and query of getParameterValues say Frequency = Q, but actually it's A
    data.IntlServTrade('ALL','ALL','ALL','AllCountries','All')  

<h2> NIPA Vintage </h2>
  Vintage data (i.e., data as as provided in a given date without subsequent updates) are not provided
by the BEA's APIs and have to be retrived using less reliable methods.  Overall, vintage data is costly to load because they are aggregated by:

  - **Title** :  Section 1 to Section 8 (default to empty)
  - **year** :  the year of the data release (default to empty)
  - **quarter** :  the quarter of the data release (default to empty)
  - **type** :  main, underlyning, MilsOfDollars.  (Defaults to main.)
  - **vintage** :  Third, Second, Advance (default empty)

 Having specified all these parameters, there still remain to specify the NIPA table (eg T10101) 
 and if it is in annual, monthly or yearly data format.  Often, there will be more than 
100s of tables even after specifying the above parameters.  So, it is a good idea to specify 
as many of these as possible.    

Hence, unless using a powerful computer, **do not** run:

     #data.NIPAVintage()
     #data.NIPAVintage('T10101')

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

    import datapungibea as dpb

    data = dpb.data()

    print(data._docDriver('NIPAVintage'))    #list the args and default options of this method.
    out1 = data.NIPAVintage('tableName = 'T10101',frequency='Q',Title='Section 1',releaseDate='2018-01-01')
    out2 = data.NIPAVintage('tableName = '10101', frequency='Q',Title='Section 1',releaseDate='2008-01-01')
    
<h2> Setting up Datapungibea </h2>

To use the BEA API, **the first step** is to get an API key from the BEA: 

* https://apps.bea.gov/API/signup/index.cfm

It is not a best practice to save an API key on a script that is running your code.  **The second step** to set up datapungibea is to save your API key on a safe location.  In particular, you will need to save your BEA API key somewhere  on your computer on a json file containing at least the following line: 

    {  
         "BEA": {"key": "**PLACE YOUR KEY HERE**", "url": "https://apps.bea.gov/api/data/"},
         (...Other API keys...)
    }


That is all that is needed to start running datapungibea.    You can either always point to the API location on a run, such as:



     import datapungibea as dpb   

     userSettings = {"ApiKeysPath": "**C:/Path to My Folder/myApiKey.json**", "ApiKeyLabel": "BEA","ResultFormat":"JSON"}   
     drivers = dpb.data(userSettings = userSettings)  
     drivers.NIPA('T10101')



Or, you may follow **step three (optional)** and save the path to your BEA API key on the package's user settings:



    import datapungibea as dpb

    dpb.utils.setUserSettings('C:/Path/myKeys.json')



Note: in case you prefer to use the log the API directly, you can use the 'connectionParameters' entry of the dpb.data above to pass the key direclty.

<h2> Running Tests (Optional) </h2>

Datapungibea comes with a family of tests to check its access to the BEA API and the quality of the retrieved data.  They check:

1. if the connection to BEA is working,
2. if the data cleaning step worked,
3. if the code snippet is executing,
4. if the code snippet gets the same data as the datapungi query.

Other tests check if BEA data has being updated of if new data is available.  To run the tests, type:


    import datapungibea as dpb
    
    dpb.tests.runTests(outputPath = 'C:/Your Path/')


This will save an html file in the path specified called datapungibea_Tests.html

You can save your test output folder in the user settings as well (need / at the end):

    import datapungibea as dpb

    dpb.utils.setTestFolder('C:/mytestFolder/')

NOTE: the tests will only work if datapungibea is aware of the API key location (currently, you 
cannot pass it directly during a test).

<h2> References </h2>

- https://apps.bea.gov/API/signup/index.cfm
- https://2.python-requests.org//en/master/
