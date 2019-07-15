<h1> Datapungibea  </h1>

  Datapungibea is a python package that provides a simplified way to extract data from the U.S. Bureau of Economics Analysis (BEA).  It uses an interface
  (API) provided by the BEA that follows current industrial standards of data transmission.  Extracting data via an API is superior 
  than web scrapping or manually downloading data from BEA's website since APIs provide a reproducible direct access to the 
  data that does not depend on a website's design.  
  
  Datapungibea is based on the Requests, a python library that provides access to any API.  Requests is well maintained package with hundreds of contributors and a large corporate sponsorship.  Datapungibea adapts Requests to the specific features of the BEA API; it has the following features:

  - it provides a quick access to the BEA datasets, but at the same time provides the Requests code snippet used to retrieve the data (which can be placed on a user script for reproducibility);
  - it outputs the whole request output (which includes metadata), but it also provides a cleaned up version, in python pandas format, of the requested dataset;
  - it goes beyond the data provided by the BEA's API to include (see below): (1) NIPA vintage data; (2) NIPA data graphical structure; and (3) NIPA summary tables;      
  - it provides a simplified management (update and read) of the user access keys (API user keys) to avoid having a copy of the key on a user script;
  - it automatically tests: (1) the connectivity to all BEA datasets, (2) the quality of the cleaned up data, (3) the validity of the provided requests code to be placed in a user's script, (4) if some of 
  the previously downloaded data has being updated (eg, GDP data tends to be retroactively updated), and (5) if new data is available. 


  
  
<h2> Setting up Datapungibea </h2>

To use the BEA API, **the first step** is to get an API key: 

- https://apps.bea.gov/API/signup/index.cfm

It is not a best practice to save an API key on a script running the code accessing the datasets.  **The second step** to set up datapungibea is to save your API key on a safe file.  In particular, you will need to save your BEA API key on a json file somewhere in your computer.  By default, the json file should contain at least the following: 

{"BEA": {"key": "**PLACE YOUR KEY HERE**", "url": "https://apps.bea.gov/api/data/"}}

That is all that is needed to start running datapungibea.    You can either always point to the API location on a run, such as:


import datapungibea as dpb
drivers = dpb.data(userSettings = {"ApiKeysPath": "**C:/Path to My Folder/myApiKey.json**", "ApiKeyLabel": "BEA","ResultFormat":"JSON"})
drivers.NIPA('T10101')


Or, you may follow **step three (optional)** and save the path to your BEA API key on the package's user settings:


import datapungibea as dpb
dpb.utils.setUserSettings('C:/Path/myKeys.json')


<h3>Optional Step - Test Output Folder</h3>

datapungibea comes with a family of tests to check its access to the BEA API and quality of the retrieved data.  Running

import datapungibea as dpb


Sample run:
  - 

  - pip install package, setup your config, and type to get table T10101:
    
    import beafullfetchpy as bff

    bff.NIPA('T10101')



- https://apps.bea.gov/API/signup/index.cfm
- https://2.python-requests.org//en/master/