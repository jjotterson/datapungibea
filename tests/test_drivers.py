import datapungibea as dpbea 

dataBea = dpbea.data()


def executeCode(stringIn):
    '''
      auxiliary function for tests: get the requests code and try to execute it.
    '''
    try:
        exec(stringIn)
        return(True)
    except:
        return(False)

def test_datasetlist():
    driver = dataBea.datasetlist(verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.

def test_getParameterList():
    driver = dataBea.getParameterList('FixedAssets',verbose=True)  
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.

def test_getParameterValues():
    driver = dataBea.getParameterValues('NIPA','Year',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.

def test_NIPA():
    driver = dataBea.NIPA('T10101','Q','2010',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.

def test_fixedAssets():
    driver = dataBea.fixedAssets('FAAt101','X',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.   

def test_ITA():
    driver = dataBea.ITA('BalCurrAcct','Brazil','A','2010',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_IIP():
    driver = dataBea.IIP(TypeOfInvestment='DebtSecAssets',Component='All',Frequency='All',Year='2010',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_GDPbyIndustry():
    driver = dataBea.GDPbyIndustry('211','1','A','2018',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_InputOutput():
    driver = dataBea.InputOutput(TableID='56',Year='2010',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_UnderlyingGDPbyIndustry():
    driver = dataBea.UnderlyingGDPbyIndustry('ALL','ALL','A','ALL',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_IntlServTrade():
    driver = dataBea.IntlServTrade('ALL','ALL','ALL','AllCountries','All',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_IntlServTrade():
    driver = dataBea.IntlServTrade('ALL','ALL','ALL','AllCountries','All',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       

def test_Regional():
    driver = dataBea.Regional('00000','1','SAGDP5N', 'All',verbose=True)
    assert driver['request'].status_code == 200  #test if connection was stablished
    assert not driver['dataFrame'].empty         #cleaned up output is not empty
    assert executeCode(driver['code'])           #try to execute the code.       