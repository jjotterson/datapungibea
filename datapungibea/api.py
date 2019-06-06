import pandas as pd
import requests
from datapungibea import generalSettings 
from datapungibea import drivers

#TODO: improve delegation (want name of methods - getDatasetlis - to be _get... or be all in a loadedDrivers class etc.  These shouldn't be 
#      easy for user access)
# only initialize a driver if it's being called

class delegator(object):
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
            
            return(getattr(delegate_object, called_method)(*args, **kwargs))
    
        return(wrapper)


class data(delegator):
    DELEGATED_METHODS = {
        'getDatasetlist'             : ['datasetlist'],
        'getGetParameterList'        : ['getParameterList'],
        'getGetParameterValues'      : ['getParameterValues'],
        'getNIPA'                    : ['NIPA'],
        'getMNE'                     : ['MNE'],
        'getFixedAssets'             : ['fixedAssets'],
        'getITA'                     : ['ITA'],
        'getIIP'                     : ['IIP'],
        'getGDPbyIndustry'           : ['GDPbyIndustry'],
        'getRegionalIncome'          : ['RegionalIncome'],
        'getRegionalProduct'         : ['RegionalProduct'],
        'getInputOutput'             : ['InputOutput'],
        'getUnderlyingGDPbyIndustry' : ['UnderlyingGDPbyIndustry'],
        'getIntlServTrade'           : ['IntlServTrade'],
        'getRegional'                : ['Regional'],
    }
    def __init__(self,connectionParameters = {}, userSettings = {}):
        '''
          the purpose of this class is to provide an environment where the shared data needed to establish a connection is loaded
          and to be a one stop shop of listing all available drivers.  
          :param connectionParameters: a dictionary with at least 'key', and 'url'
            {'key': 'your key', 'description': 'BEA data', 'url': 'https://apps.bea.gov/api/data/'} 
          :param userSettings: settings saved in the packge pointing to a json containing the connection parameters 
        '''
        self.__connectInfo = generalSettings.getGeneralSettings(connectionParameters = connectionParameters, userSettings = userSettings ) #TODO: inherit this, all drivers as well
        self._metadata = self.__connectInfo.packageMetadata
        self._help     = self.__connectInfo.datasourceOverview
        #load drivers:
        self.getDatasetlist        = drivers.getDatasetlist(self.__connectInfo.baseRequest)
        self.getGetParameterList   = drivers.getGetParameterList(baseRequest = self.__connectInfo.baseRequest)
        self.getGetParameterValues = drivers.getGetParameterValues(baseRequest = self.__connectInfo.baseRequest)
        self.getNIPA               = drivers.getNIPA(baseRequest = self.__connectInfo.baseRequest)
        self.getMNE                = drivers.getMNE(baseRequest = self.__connectInfo.baseRequest)
        self.getFixedAssets        = drivers.getFixedAssets(baseRequest = self.__connectInfo.baseRequest)
        self.getITA                = drivers.getITA(baseRequest = self.__connectInfo.baseRequest)
        #TODO: improve loading the drivers 
        




if __name__ == '__main__':
    
    d = data()
    #print(d.datasetlist(verbose=True)['code'])
    #print(d.getParameterList('FixedAssets',verbose=True))  #TODO: harmonize the names - use the same as listed in the datasetlist
    #print(d.getParameterValues('NIPA','Year',verbose=True))
    #print(d.NIPA('T0101'))
    #print(d.fixedAssets('FAAt101','X'))
    print(d.ITA('BalCurrAcct','Brazil','A','2010'))

    #print(NIPA('T10101'))