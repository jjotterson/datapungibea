import subprocess
import os
#from ..utils import getResourcePath


def runTests(outputPath='',testsPath='',verbose = True):
    if not testsPath:
       testsPath =  os.path.dirname(os.path.abspath(__file__)).replace("\\","/")
       print('**************************** \nWill run tests in: ' + testsPath)
    if not outputPath:
        outputPath = "U:/"
    subprocess.Popen('pytest ' + testsPath + ' --html='+outputPath+'datapungibea_Tests.html --self-contained-html')
    if verbose:
        print('Tests will be saved in '+outputPath+'datapungibea_Tests.html \n****************************')

if __name__ == '__main__':
    from sys import argv    
    import subprocess
    import os

    runTests()
    #print(os.path.dirname(os.path.realpath(__file__)))
    #query = subprocess.Popen('pytest --html=datapungibea_Tests.html')
    #print(query)