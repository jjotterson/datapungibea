import subprocess
import os

def runTests(outputPath):
    subprocess.Popen('pytest --html='+outputPath+'datapungibea_Tests.html')

if __name__ == '__main__':
    from sys import argv    
    import subprocess
    import os

    runTests('')
    #print(os.path.dirname(os.path.realpath(__file__)))
    #query = subprocess.Popen('pytest --html=datapungibea_Tests.html')
    #print(query)