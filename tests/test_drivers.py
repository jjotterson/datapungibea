import datapungibea as dpbea 
import time
import pandas as pd

dataBea = dpbea.data()


def executeCode(stringIn):
    '''
      auxiliary function for tests: get the requests code as a string and try to execute it.
    '''
    try:
        exec(stringIn+'\n')      #exec('print("hi")') #
        return(dict( codeRun = True, codeOutput = locals()['df_output']   ))   #try to output the dataframe called df_output
    except:
        try:
            exec(stringIn)  #if no dataframe called output, try to see it at least can exec the code
            return(dict(codeRun = True, codeOutput = pd.DataFrame([])))
        except:
            return(dict(codeRun = False, codeOutput = pd.DataFrame([])))

def test_datasetlist():
    '''
      test the datasetlist BEA dataset
    '''
    driver   = dataBea.datasetlist(verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200               #test if connection was stablished
    assert not driver['dataFrame'].empty                      #cleaned up output is not empty
    assert execCode['codeRun']                                #try to execute the code.
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_getParameterList():
    driver = dataBea.getParameterList('FixedAssets',verbose=True)  
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']                   #try to execute the code.
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_getParameterValues():
    driver = dataBea.getParameterValues('NIPA','Year',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']                   #try to execute the code.
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_NIPA():
    driver = dataBea.NIPA('T10101','Q','2010',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']                   #try to execute the code.
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_fixedAssets():
    driver = dataBea.fixedAssets('FAAt101','X',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']           #try to execute the code.   
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_ITA():
    driver = dataBea.ITA('BalCurrAcct','Brazil','A','2010',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']            #try to execute the code.   
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the      

def test_IIP():
    driver = dataBea.IIP(TypeOfInvestment='DebtSecAssets',Component='All',Frequency='All',Year='2010',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']        #try to execute the code.       
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the      

def test_GDPbyIndustry():
    driver = dataBea.GDPbyIndustry('211','1','A','2018',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']          #try to execute the code.   
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the          

def test_InputOutput():
    driver = dataBea.InputOutput(TableID='56',Year='2010',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']            #try to execute the code.       
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_UnderlyingGDPbyIndustry():
    driver = dataBea.UnderlyingGDPbyIndustry('ALL','ALL','A','ALL',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']           #try to execute the code.       
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_IntlServTrade():
    driver = dataBea.IntlServTrade('ALL','ALL','ALL','AllCountries','All',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']          #try to execute the code.       
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the  

def test_IntlServTrade():
    driver = dataBea.IntlServTrade('ALL','ALL','ALL','AllCountries','All',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']         #try to execute the code.       

def test_Regional():
    driver = dataBea.Regional('00000','1','SAGDP5N', 'All',verbose=True)
    execCode = executeCode(driver['code']) 
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert execCode['codeRun']           #try to execute the code.       
    assert execCode['codeOutput'].equals(driver['dataFrame']) #test if the output of the code equals the output of the      


if __name__ == '__main__':
    #test_IIP()
    #test_datasetlist()
    #test_getParameterList()
    #test_getParameterValues()
    test_NIPA()
    #test_fixedAssets()