<h1> Datapungibea  </h1>

  Datapungibea is a python package that provides a simplified way to extract data from the U.S. Bureau of Economics Analysis (BEA).  It uses an interface
  (Application Program Interface - API) provided by the BEA that follows current industrial standards of data transmission.  Extracting data via an API is superior 
  than web scrapping or manually downloading data from a website since it provides a reproducible direct access to the 
  dataset that is independent of a website's design.  
  
  Datapungibea is based on the Requests, a python library that facilitates access to APIs.  Requests is well maintained package with hundreds of contributors and a large corporate sponsorship.  Datapungibea adapts Requests to the specific features of the BEA API; it has the following features:

  - it provides a quick access to the BEA datasets, but at the same time provides the Requests code snippet used to retrieve the data (which can be placed on a user script for reproducibility);
  - it outputs the whole request output (which includes metadata), but it also provides a cleaned up version, in python pandas format, of the requested dataset;
  - it goes beyond the data provided by the BEA's API to include (see below): (1) NIPA vintage data; (2) NIPA data graphical structure; and (3) NIPA summary tables;      
  - it provides a simplified management (update and read) of the user access keys (API user keys) to avoid having a copy of the key on a user script;
  - it automatically tests: (1) the connectivity to all BEA datasets, (2) the quality of the cleaned up data, (3) the validity of the provided requests code to be placed in a user's script, (4) if some of 
  the previously downloaded data has being updated (eg, GDP data tends to be retroactively updated), and (5) if new data is available. 


  
  
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

- <h3> Optional Setting up Step - Specify a Output Folder for Code Tests</h3>

Datapungibea comes with a family of tests to check its access to the BEA API and quality of the retrieved data.  They check:

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


<h2> Sample runs </h2>

<h3>Some functionalities of datapungibea</h3>

    import datapungibea as dpb
    
    data = dpb.data()     #start the drivers

    print(data)                               #displays a list of available drivers 
    data.NIPA.__doc__                         #get a list of inputs and default options of the driver  
    data.NIPA('T10101')                       #load and clean NIPA table T10101 (default: frequency = Q, all years).  

    all = data.NIPA('T10101',verbose = True)  #This is a dictionary with all data 
    all['code']                               #(1) a code snippet of a requests query of the BEA API
    all['metadata']                           #(2) the metadata of the BEA dataset
    all['dataFrame']                          #(3) a cleanedup version of the output - pandas dataframe
    all['request']                            #(4) the output of the requests query
    
    
    ## To copy the requests code snippet to clipboard, run:
    data._clipboard()
    

<h3>Run of all BEA drivers</h3>

    import datapungibea as dpb
    
    #start the drivers:
    data = dpb.data()
    
    #METADATA Functions.                      # Use these to get: 
    data.datasetlist()                        # (1) the list of BEA datasets with APIs
    data.getParameterList('FixedAssets')      # (2) the parameters of a specific BEA API 
    data.getParameterValues('NIPA','Year')    # (3) the options of a parameter of a BEA API 
    
    
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



<h2> References </h2>

- https://apps.bea.gov/API/signup/index.cfm
- https://2.python-requests.org//en/master/