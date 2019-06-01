import pandas as pd
import requests
from datapungibea import utils as cfgf
from . import generalSettings 
from . import drivers

try:
    from datapungibea import config as userSettings
except:
    print(
        "Run userPreferences to save API Key and prefered format (XML vs JSON) to memory \n" +
        "  else Run in session or add to script \n    userOptions = {'UserID': 'enter key here', 'ResultFormat': 'JSON' } \n" + 
        "  else include API key and prefered format in each function call")  
        #TODO: do this as class - so that can add this to object atribute, not define on brackground userOptions = {} but bff.userOptions ==

def basePayload(payload):
    payload = {x: userSettings.userOptions[x]
               for x in ['UserID', 'ResultFormat']}
    payload.update(settings)


class data():
    def __init__(self,connectionParameters = {}, userSettings = {}):
        '''
          the purpose of this class is to provide an environment where the shared data needed to establish a connection is loaded
          and to be a one stop shop of listing all available drivers.  
          :param connectionParameters: a dictionary with at least 'key', and 'url'
            {'key': 'your key', 'description': 'BEA data', 'url': 'https://apps.bea.gov/api/data/'} 
          :param userSettings: settings saved in the packge pointing to a json containing the connection parameters 
        '''
        self.__connectInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings ) #TODO: inherit this, all drivers as well
          
  


class Delegator(object):
    def __getattr__(self, called_method):
        def __raise_standard_exception():
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, called_method))

    def wrapper(*args, **kwargs):
        delegation_config = getattr(self, 'DELEGATED_METHODS', None)
        if not isinstance(delegation_config, dict):
            __raise_standard_exception()
 
        for delegate_object_str, delegated_methods in delegation_config.items():
            if called_method in delegated_methods:
                break
        else:
            __raise_standard_error()

        delegate_object = getattr(self, delegate_object_str, None)

        return getattr(delegate_object, called_method)(*args, **kwargs)

    return wrapper



if __name__ == '__main__':
    
    d = data()
    print(d)
    #print(NIPA('T10101'))