<h1> General Guidelines for datapungi Packages </h1>

packageName\
--config\
----pkgConfig    specific parameters used for the methods in the package (eg, url of used by the methods)
----userConfig   user information such as path to api keys, and key label, preferred output format (eg json vs xml), 
                 user should have an interface function that allows to change this. 
api            - main file with a "data" method 
utils          - project internal tools such as resource locator, users' tools to change their preferences.  
databases      - functions that get data from databases of the datasource
databasesUtils - utility function for handling the databases of the datasource
metadata       - information on the datasource and its databases available 



