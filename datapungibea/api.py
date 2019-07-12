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
        'getRegionalIncome'          : ['RegionalIncome'],  #deprecated, use Regional instead
        'getRegionalProduct'         : ['RegionalProduct'], #deprecated, use Regional instead
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
        self.getDatasetlist                = drivers.getDatasetlist(self.__connectInfo.baseRequest)
        self.getGetParameterList           = drivers.getGetParameterList(baseRequest = self.__connectInfo.baseRequest)
        self.getGetParameterValues         = drivers.getGetParameterValues(baseRequest = self.__connectInfo.baseRequest)
        self.getNIPA                       = drivers.getNIPA(baseRequest = self.__connectInfo.baseRequest)
        self.getMNE                        = drivers.getMNE(baseRequest = self.__connectInfo.baseRequest)
        self.getFixedAssets                = drivers.getFixedAssets(baseRequest = self.__connectInfo.baseRequest)
        self.getITA                        = drivers.getITA(baseRequest = self.__connectInfo.baseRequest)
        self.getIIP                        = drivers.getIIP(baseRequest = self.__connectInfo.baseRequest)
        self.getGDPbyIndustry              = drivers.getGDPbyIndustry(baseRequest = self.__connectInfo.baseRequest)
        self.getRegionalIncome             = drivers.getRegionalIncome(baseRequest = self.__connectInfo.baseRequest)
        self.getRegionalProduct            = drivers.getRegionalProduct(baseRequest = self.__connectInfo.baseRequest)
        self.getInputOutput                = drivers.getInputOutput(baseRequest = self.__connectInfo.baseRequest)
        self.getUnderlyingGDPbyIndustry    = drivers.getUnderlyingGDPbyIndustry(baseRequest = self.__connectInfo.baseRequest)
        self.getIntlServTrade              = drivers.getIntlServTrade(baseRequest = self.__connectInfo.baseRequest)
        self.getRegional                   = drivers.getRegional(baseRequest = self.__connectInfo.baseRequest)
        #TODO: improve loading the drivers 
        




if __name__ == '__main__':
    #TODO TODO: Need to test MNE
    #TODO: harmonize the names - use the same as listed in the datasetlist, include the function entry names in the example below
    #TODO: transform this into tests
    
    d = data()

    #METADATA Functions:
    #print(d.datasetlist(verbose=True)['code'])
    #print(d.getParameterList('FixedAssets',verbose=True))   
    #print(d.getParameterValues('NIPA','Year',verbose=True))

    print(d.NIPA('T10101',verbose=True)['code'])

    #print(d.fixedAssets('FAAt101','X'))

    #print(d.ITA('BalCurrAcct','Brazil','A','2010'))

    #print(d.IIP(TypeOfInvestment='DebtSecAssets',Component='All',Frequency='All',Year='All'))    #NOTE: for IIP, either use All years of All TypeOfInvestment            
    #print(d.IIP('All','All','All','2010'))              

    #print(d.GDPbyIndustry('211','1','A','2018'))

    #RegionalIncome and RegionalOutput were deprecated - use Regional instead.
    #d.getRegionalIncome.RegionalIncome()
    #d.getRegionalProduct.RegionalProduct()

    #print(d.InputOutput(TableID='56',Year='2010'))                       
    #print(d.InputOutput('All','All'))                       
    #print(d.UnderlyingGDPbyIndustry('ALL','ALL','A','ALL')) #NOTE: PDF and query of getParameterValues say Frequency = Q, but actually it's A TODO: email BEA
    #print(d.IntlServTrade('ALL','ALL','ALL','AllCountries','All')) 
    
    #print(d.Regional('00000','1','SAGDP5N', '2015,2016')) 

    #print('Regional data test')
    #print(d.Regional('00000','1','SAGDP5N', 'All')) 