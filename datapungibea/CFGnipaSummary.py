'''
  Configuration needed to write a NIPA summary table 
'''
tabparams = {
    'Account 1' : {
        'meta' :{
            'heading': "Table 1: Domestic Income and Product Account",
            'caption':    "Source: BEA NIPA Tables 1.10 and Table 1.1.5"      
        },
        'source' : {
            'tableName' : 'T11000',
            'tableEntries' :  
            [
                { 'SeriesCode': "A261RC", 'indentation':0},	
                { 'SeriesCode': "A4002C", 'indentation':1},	
                { 'SeriesCode': "A4102C", 'indentation':2},	
                { 'SeriesCode': "W270RC", 'indentation':3},	
                { 'SeriesCode': "B4189C", 'indentation':3},	
                { 'SeriesCode': "A038RC", 'indentation':2},	
                { 'SeriesCode': "W056RC", 'indentation':1},	
                { 'SeriesCode': "A107RC", 'indentation':1},	
                { 'SeriesCode': "W271RC", 'indentation':1},	
                { 'SeriesCode': "W260RC", 'indentation':2},	
                { 'SeriesCode': "W272RC", 'indentation':2},	
                { 'SeriesCode': "B029RC", 'indentation':2},	
                { 'SeriesCode': "A041RC", 'indentation':2},	
                { 'SeriesCode': "A048RC", 'indentation':2},	
                { 'SeriesCode': "A445RC", 'indentation':2},	
                { 'SeriesCode': "A054RC", 'indentation':3},	
                { 'SeriesCode': "W273RC", 'indentation':3},	
                { 'SeriesCode': "A449RC", 'indentation':4},	
                { 'SeriesCode': "W274RC", 'indentation':4},	
                { 'SeriesCode': "A108RC", 'indentation':3},	
                { 'SeriesCode': "A262RC", 'indentation':1},	
                { 'SeriesCode': "A024RC", 'indentation':2},	
                { 'SeriesCode': "A264RC", 'indentation':2},	
                { 'SeriesCode': "A030RC", 'indentation':0}
            ]
        },
        'uses' : {
            'tableName' : 'T10105',
            'tableEntries' : [ 
                {'SeriesCode':"A191RC",'indentation': 0},	
                {'SeriesCode':"DPCERC",'indentation': 1},	
                {'SeriesCode':"DGDSRC",'indentation': 2},	
                {'SeriesCode':"DDURRC",'indentation': 3},	
                {'SeriesCode':"DNDGRC",'indentation': 3},	
                {'SeriesCode':"DSERRC",'indentation': 2},	
                {'SeriesCode':"A006RC",'indentation': 1},	
                {'SeriesCode':"A007RC",'indentation': 2},	
                {'SeriesCode':"A008RC",'indentation': 3},	 
                {'SeriesCode':"B009RC",'indentation': 4},	
                {'SeriesCode':"Y033RC",'indentation': 4},	
                {'SeriesCode':"Y001RC",'indentation': 4},	
                {'SeriesCode':"A011RC",'indentation': 3},	
                {'SeriesCode':"A014RC",'indentation': 2},	
                {'SeriesCode':"A019RC",'indentation': 1},	
                {'SeriesCode':"B020RC",'indentation': 2},	
                {'SeriesCode':"A253RC",'indentation': 3},	
                {'SeriesCode':"A646RC",'indentation': 3},	
                {'SeriesCode':"B021RC",'indentation': 2},	
                {'SeriesCode':"A255RC",'indentation': 3},	
                {'SeriesCode':"B656RC",'indentation': 3},	
                {'SeriesCode':"A822RC",'indentation': 1},	
                {'SeriesCode':"A823RC",'indentation': 2},	
                {'SeriesCode':"A824RC",'indentation': 3},	
                {'SeriesCode':"A825RC",'indentation': 3},	
                {'SeriesCode':"A829RC",'indentation': 2}
            ]
        }
    }, 
    'Account 2' : {
        'meta' :{
            'heading': "Table 2: Private Enterprise Income Account",
            'caption': "Source: BEA NIPA Table 1.16"          
        },
        'source' : {
            'tableName' : "T11600",
            'tableEntries' : [
               {'SeriesCode':"W259RC",'indentation':0},
               {'SeriesCode':"W260RC",'indentation':1},
               {'SeriesCode':"W261RC",'indentation':1},
               {'SeriesCode':"W262RC",'indentation':2},
               {'SeriesCode':"B3375C",'indentation':2},
               {'SeriesCode':"B3475C",'indentation':2}, 
            ]
        },
        'uses' : {
            'tableName' : "T11600",
            'tableEntries' : [
                {'SeriesCode':"W263RC",'indentation': 0 },
                {'SeriesCode':"W264RC",'indentation': 1 },
                {'SeriesCode':"W265RC",'indentation': 2 },
                {'SeriesCode':"B3376C",'indentation': 2 },
                {'SeriesCode':"B3476C",'indentation': 2 },
                {'SeriesCode':"B029RC",'indentation': 1 },
                {'SeriesCode':"B931RC",'indentation': 2 },
                {'SeriesCode':"W061RC",'indentation': 2 },
                {'SeriesCode':"W237RC",'indentation': 2 },
                {'SeriesCode':"A041RC",'indentation': 1 },
                {'SeriesCode':"A048RC",'indentation': 1 },
                {'SeriesCode':"A051RC",'indentation': 1 },
                {'SeriesCode':"A054RC",'indentation': 2 },
                {'SeriesCode':"W025RC",'indentation': 3 },
                {'SeriesCode':"B930RC",'indentation': 3 },
                {'SeriesCode':"A551RC",'indentation': 2 },
                {'SeriesCode':"B056RC",'indentation': 3 },
                {'SeriesCode':"A127RC",'indentation': 3 }
            ]
        }
    },
    'Account 3' : {
        'meta' :{
            'heading': "Table 3: Personal Income and Outlays Account",
            'caption': "Source: BEA NIPA Table 2.01"          
        },
        'source' :{
            'tableName' : "T20100",
            'tableEntries' : [
                {'SeriesCode':"A065RC",'indentation': 0 },
                {'SeriesCode':"A033RC",'indentation': 1 },
                {'SeriesCode':"A034RC",'indentation': 2 },
                {'SeriesCode':"A132RC",'indentation': 3 },
                {'SeriesCode':"B202RC",'indentation': 3 },
                {'SeriesCode':"A038RC",'indentation': 2 },
                {'SeriesCode':"B040RC",'indentation': 3 },
                {'SeriesCode':"B039RC",'indentation': 3 },
                {'SeriesCode':"A041RC",'indentation': 1 },
                {'SeriesCode':"B042RC",'indentation': 2 },
                {'SeriesCode':"A045RC",'indentation': 2 },
                {'SeriesCode':"A048RC",'indentation': 1 },
                {'SeriesCode':"W210RC",'indentation': 1 },
                {'SeriesCode':"A064RC",'indentation': 2 },
                {'SeriesCode':"B703RC",'indentation': 2 },
                {'SeriesCode':"A577RC",'indentation': 1 },
                {'SeriesCode':"A063RC",'indentation': 2 },
                {'SeriesCode':"W823RC",'indentation': 3 },
                {'SeriesCode':"W824RC",'indentation': 3 },
                {'SeriesCode':"A045RC",'indentation': 3 },
                {'SeriesCode':"W825RC",'indentation': 3 },
                {'SeriesCode':"W826RC",'indentation': 3 },
                {'SeriesCode':"W827RC",'indentation': 3 },
                {'SeriesCode':"B931RC",'indentation': 2 }
             ]
        },
        'uses' : {
            'tableName' : "T20100",
            'tableEntries' : [ 
                {'SeriesCode':"W055RC",'indentation': 1 },
                {'SeriesCode':"A068RC",'indentation': 1 },
                {'SeriesCode':"DPCERC",'indentation': 2 },
                {'SeriesCode':"B069RC",'indentation': 2 },
                {'SeriesCode':"W211RC",'indentation': 2 },
                {'SeriesCode':"W062RC",'indentation': 3 },
                {'SeriesCode':"B070RC",'indentation': 3 },
                {'SeriesCode':"A071RC",'indentation': 1 }
            ]
        }
    },
    'Account 4' : {
        'meta' :{
            'heading': "Table 4: Government Receipts and Expenditure Account",
            'caption': "Source: BEA NIPA Table 3.01"          
        },
        'source' :{
            'tableName' : "T30100",
            'tableEntries' : [
                {'SeriesCode':"W021RC",'indentation': 0 },
                {'SeriesCode':"W054RC",'indentation': 1 },
                {'SeriesCode':"W055RC",'indentation': 2 },
                {'SeriesCode':"W056RC",'indentation': 2 },
                {'SeriesCode':"W025RC",'indentation': 2 },
                {'SeriesCode':"W008RC",'indentation': 2 },
                {'SeriesCode':"W782RC",'indentation': 1 },
                {'SeriesCode':"W058RC",'indentation': 1 },
                {'SeriesCode':"W059RC",'indentation': 2 },
                {'SeriesCode':"Y703RC",'indentation': 3 },
                {'SeriesCode':"Y704RC",'indentation': 3 },
                {'SeriesCode':"W065RC",'indentation': 2 },
                {'SeriesCode':"W060RC",'indentation': 1 },
                {'SeriesCode':"W061RC",'indentation': 2 },
                {'SeriesCode':"W061RC",'indentation': 2 },
                {'SeriesCode':"A108RC",'indentation': 1 }
            ]
        },
        'uses' : {
            'tableName' : "T30100",
            'tableEntries' : [ 
                {'SeriesCode':"W022RC",'indentation': 0 },
                {'SeriesCode':"A955RC",'indentation': 1 },
                {'SeriesCode':"A084RC",'indentation': 1 },
                {'SeriesCode':"W063RC",'indentation': 2 },
                {'SeriesCode':"A063RC",'indentation': 3 },
                {'SeriesCode':"W016RC",'indentation': 3 },
                {'SeriesCode':"W017RC",'indentation': 2 },
                {'SeriesCode':"A180RC",'indentation': 1 },
                {'SeriesCode':"A204RC",'indentation': 2 },
                {'SeriesCode':"Y712RC",'indentation': 2 },
                {'SeriesCode':"A107RC",'indentation': 1 },
                {'SeriesCode':"A922RC",'indentation': 1 }  
            ]
        }
    },   
    'Account 5' : {
        'meta' :{
            'heading': "Table 5: Foreign Transaction Current Account",
            'caption': "Source: BEA NIPA Table 4.01"          
        },
        'source' :{
            'tableName' : "T40100",
            'tableEntries' : [  
                {'SeriesCode':"W163RC",'indentation': 0 },
                {'SeriesCode':"B021RC",'indentation': 1 },
                {'SeriesCode':"A255RC",'indentation': 2 },
                {'SeriesCode':"A333RC",'indentation': 3 },
                {'SeriesCode':"A340RC",'indentation': 3 },
                {'SeriesCode':"B656RC",'indentation': 2 },
                {'SeriesCode':"A655RC",'indentation': 1 },
                {'SeriesCode':"B4189C",'indentation': 2 },
                {'SeriesCode':"W161RC",'indentation': 2 },
                {'SeriesCode':"B1869C",'indentation': 3 },
                {'SeriesCode':"B3376C",'indentation': 3 },
                {'SeriesCode':"B3476C",'indentation': 3 },
                {'SeriesCode':"A123RC",'indentation': 1 },
                {'SeriesCode':"B070RC",'indentation': 2 },
                {'SeriesCode':"B088RC",'indentation': 2 },
                {'SeriesCode':"W164RC",'indentation': 2 },
                {'SeriesCode':"A124RC",'indentation': 0 }
             ]
        },
        'uses' : {
            'tableName' : "T40100",
            'tableEntries' : [
                {'SeriesCode':"A120RC1",'indentation': 0 },
                {'SeriesCode':"B020RC", 'indentation': 1 },
                {'SeriesCode':"A253RC", 'indentation': 2 },
                {'SeriesCode':"A332RC", 'indentation': 3 },
                {'SeriesCode':"A339RC", 'indentation': 3 },
                {'SeriesCode':"A646RC", 'indentation': 3 },
                {'SeriesCode':"B645RC", 'indentation': 1 },
                {'SeriesCode':"B4188C", 'indentation': 2 },
                {'SeriesCode':"W160RC", 'indentation': 2 },
                {'SeriesCode':"A2067C", 'indentation': 3 },
                {'SeriesCode':"B3375C", 'indentation': 3 },
                {'SeriesCode':"B3475C", 'indentation': 3 }
             ]
        }
    },
    'Account 6' : {
        'meta' :{
            'heading':  "Table 6: Domestic Capital Account",
            'caption': "Source: BEA NIPA Tables 5.01"          
        },
        'source' :{
            'tableName' : "T50100",
            'tableEntries' : [
                {'SeriesCode': "A929RC", 'indentation': 0 },
                {'SeriesCode': "W201RC", 'indentation': 1 },
                {'SeriesCode': "W202RC", 'indentation': 2 },
                {'SeriesCode': "A127RC", 'indentation': 3 },
                {'SeriesCode': "B057RC", 'indentation': 4 },
                {'SeriesCode': "B058RC", 'indentation': 4 },
                {'SeriesCode': "A059RC", 'indentation': 4 },
                {'SeriesCode': "W986RC", 'indentation': 3 },
                {'SeriesCode': "A071RC", 'indentation': 4 },
                {'SeriesCode': "A922RC", 'indentation': 2 },
                {'SeriesCode': "A923RC", 'indentation': 3 },
                {'SeriesCode': "A924RC", 'indentation': 3 },
                {'SeriesCode': "A262RC", 'indentation': 1 },
                {'SeriesCode': "A024RC", 'indentation': 2 },
                {'SeriesCode': "W276RC", 'indentation': 3 },
                {'SeriesCode': "W279RC", 'indentation': 3 },
                {'SeriesCode': "A264RC", 'indentation': 2 },
                {'SeriesCode': "A918RC", 'indentation': 3 },
                {'SeriesCode': "A919RC", 'indentation': 3 },
             ]
        },
        'uses' : {
            'tableName' : "T50100",
            'tableEntries' : [
                {'SeriesCode':"A928RC", 'indentation':  0 },
                {'SeriesCode':"W170RC", 'indentation':  1 },
                {'SeriesCode':"A006RC", 'indentation':  2 },
                {'SeriesCode':"W987RC", 'indentation':  3 },
                {'SeriesCode':"W988RC", 'indentation':  3 },
                {'SeriesCode':"A782RC", 'indentation':  2 },
                {'SeriesCode':"A787RC", 'indentation':  3 },
                {'SeriesCode':"A799RC", 'indentation':  3 },
                {'SeriesCode':"W167RC", 'indentation':  1 },
                {'SeriesCode':"W999RC", 'indentation':  2 },
                {'SeriesCode':"W989RC", 'indentation':  3 },
                {'SeriesCode':"W990RC", 'indentation':  3 },
                {'SeriesCode':"W991RC", 'indentation':  2 },
                {'SeriesCode':"W992RC", 'indentation':  3 },
                {'SeriesCode':"W993RC", 'indentation':  3 },
                {'SeriesCode':"W162RC", 'indentation':  1 },
                {'SeriesCode':"W994RC", 'indentation':  2 },
                {'SeriesCode':"W995RC", 'indentation':  3 },
                {'SeriesCode':"W996RC", 'indentation':  3 },
                {'SeriesCode':"AD01RC", 'indentation':  2 },
                {'SeriesCode':"AD02RC", 'indentation':  3 },
                {'SeriesCode':"AD03RC", 'indentation':  3 },
                {'SeriesCode':"A030RC", 'indentation':  0 },
             ]
        }
    }
}