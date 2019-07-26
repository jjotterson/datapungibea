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
            'TableName' : 'T11000',
            'TableEntries' :  
            [
                { 'symbol': "A261RC", 'level':0},	
                { 'symbol': "A4002C", 'level':1},	
                { 'symbol': "A4102C", 'level':2},	
                { 'symbol': "W270RC", 'level':3},	
                { 'symbol': "B4189C", 'level':3},	
                { 'symbol': "A038RC", 'level':2},	
                { 'symbol': "W056RC", 'level':1},	
                { 'symbol': "A107RC", 'level':1},	
                { 'symbol': "W271RC", 'level':1},	
                { 'symbol': "W260RC", 'level':2},	
                { 'symbol': "W272RC", 'level':2},	
                { 'symbol': "B029RC", 'level':2},	
                { 'symbol': "A041RC", 'level':2},	
                { 'symbol': "A048RC", 'level':2},	
                { 'symbol': "A445RC", 'level':2},	
                { 'symbol': "A054RC", 'level':3},	
                { 'symbol': "W273RC", 'level':3},	
                { 'symbol': "A449RC", 'level':4},	
                { 'symbol': "W274RC", 'level':4},	
                { 'symbol': "A108RC", 'level':3},	
                { 'symbol': "A262RC", 'level':1},	
                { 'symbol': "A024RC", 'level':2},	
                { 'symbol': "A264RC", 'level':2},	
                { 'symbol': "A030RC", 'level':0}
            ]
        },
        'uses' : {
            'TableName' : 'T10105',
            'TableEntries' : [ 
                {'symbol':"A191RC",'level': 0},	
                {'symbol':"DPCERC",'level': 1},	
                {'symbol':"DGDSRC",'level': 2},	
                {'symbol':"DDURRC",'level': 3},	
                {'symbol':"DNDGRC",'level': 3},	
                {'symbol':"DSERRC",'level': 2},	
                {'symbol':"A006RC",'level': 1},	
                {'symbol':"A007RC",'level': 2},	
                {'symbol':"A008RC",'level': 3},	 
                {'symbol':"B009RC",'level': 4},	
                {'symbol':"Y033RC",'level': 4},	
                {'symbol':"Y001RC",'level': 4},	
                {'symbol':"A011RC",'level': 3},	
                {'symbol':"A014RC",'level': 2},	
                {'symbol':"A019RC",'level': 1},	
                {'symbol':"B020RC",'level': 2},	
                {'symbol':"A253RC",'level': 3},	
                {'symbol':"A646RC",'level': 3},	
                {'symbol':"B021RC",'level': 2},	
                {'symbol':"A255RC",'level': 3},	
                {'symbol':"B656RC",'level': 3},	
                {'symbol':"A822RC",'level': 1},	
                {'symbol':"A823RC",'level': 2},	
                {'symbol':"A824RC",'level': 3},	
                {'symbol':"A825RC",'level': 3},	
                {'symbol':"A829RC",'level': 2}
            ]
        }
    }, 
    'Account 2' : {
        'meta' :{
            'heading': "Table 2: Private Enterprise Income Account",
            'caption': "Source: BEA NIPA Table 1.16"          
        },
        'source' : {
            'TableName' : "T11600",
            'TableEntries' : [
               {'symbol':"W259RC",'level':0},
               {'symbol':"W260RC",'level':1},
               {'symbol':"W261RC",'level':1},
               {'symbol':"W262RC",'level':2},
               {'symbol':"B3375C",'level':2},
               {'symbol':"B3475C",'level':2}, 
            ]
        },
        'uses' : {
            'TableName' : "T11600",
            'TableEntries' : [
                {'symbol':"W263RC",'level': 0 },
                {'symbol':"W264RC",'level': 1 },
                {'symbol':"W265RC",'level': 2 },
                {'symbol':"B3376C",'level': 2 },
                {'symbol':"B3476C",'level': 2 },
                {'symbol':"B029RC",'level': 1 },
                {'symbol':"B931RC",'level': 2 },
                {'symbol':"W061RC",'level': 2 },
                {'symbol':"W237RC",'level': 2 },
                {'symbol':"A041RC",'level': 1 },
                {'symbol':"A048RC",'level': 1 },
                {'symbol':"A051RC",'level': 1 },
                {'symbol':"A054RC",'level': 2 },
                {'symbol':"W025RC",'level': 3 },
                {'symbol':"B930RC",'level': 3 },
                {'symbol':"A551RC",'level': 2 },
                {'symbol':"B056RC",'level': 3 },
                {'symbol':"A127RC",'level': 3 }
            ]
        }
    },
    'Account 3' : {
        'meta' :{
            'heading': "Table 3: Personal Income and Outlays Account",
            'caption': "Source: BEA NIPA Table 2.01"          
        },
        'source' :{
            'TableName' : "T20100",
            'TableEntries' : [
                {'symbol':"A065RC",'level': 0 },
                {'symbol':"A033RC",'level': 1 },
                {'symbol':"A034RC",'level': 2 },
                {'symbol':"A132RC",'level': 3 },
                {'symbol':"B202RC",'level': 3 },
                {'symbol':"A038RC",'level': 2 },
                {'symbol':"B040RC",'level': 3 },
                {'symbol':"B039RC",'level': 3 },
                {'symbol':"A041RC",'level': 1 },
                {'symbol':"B042RC",'level': 2 },
                {'symbol':"A045RC",'level': 2 },
                {'symbol':"A048RC",'level': 1 },
                {'symbol':"W210RC",'level': 1 },
                {'symbol':"A064RC",'level': 2 },
                {'symbol':"B703RC",'level': 2 },
                {'symbol':"A577RC",'level': 1 },
                {'symbol':"A063RC",'level': 2 },
                {'symbol':"W823RC",'level': 3 },
                {'symbol':"W824RC",'level': 3 },
                {'symbol':"A045RC",'level': 3 },
                {'symbol':"W825RC",'level': 3 },
                {'symbol':"W826RC",'level': 3 },
                {'symbol':"W827RC",'level': 3 },
                {'symbol':"B931RC",'level': 2 }
             ]
        },
        'uses' : {
            'TableName' : "T20100",
            'TableEntries' : [ 
                {'symbol':"W055RC",'level': 1 },
                {'symbol':"A068RC",'level': 1 },
                {'symbol':"DPCERC",'level': 2 },
                {'symbol':"B069RC",'level': 2 },
                {'symbol':"W211RC",'level': 2 },
                {'symbol':"W062RC",'level': 3 },
                {'symbol':"B070RC",'level': 3 },
                {'symbol':"A071RC",'level': 1 }
            ]
        }
    },
    'Account 4' : {
        'meta' :{
            'heading': "Table 4: Government Receipts and Expenditure Account",
            'caption': "Source: BEA NIPA Table 3.01"          
        },
        'source' :{
            'TableName' : "T30100",
            'TableEntries' : [
                {'symbol':"W021RC",'level': 0 },
                {'symbol':"W054RC",'level': 1 },
                {'symbol':"W055RC",'level': 2 },
                {'symbol':"W056RC",'level': 2 },
                {'symbol':"W025RC",'level': 2 },
                {'symbol':"W008RC",'level': 2 },
                {'symbol':"W782RC",'level': 1 },
                {'symbol':"W058RC",'level': 1 },
                {'symbol':"W059RC",'level': 2 },
                {'symbol':"Y703RC",'level': 3 },
                {'symbol':"Y704RC",'level': 3 },
                {'symbol':"W065RC",'level': 2 },
                {'symbol':"W060RC",'level': 1 },
                {'symbol':"W061RC",'level': 2 },
                {'symbol':"W061RC",'level': 2 },
                {'symbol':"A108RC",'level': 1 }
            ]
        },
        'uses' : {
            'TableName' : "T30100",
            'TableEntries' : [ 
                {'symbol':"W022RC",'level': 0 },
                {'symbol':"A955RC",'level': 1 },
                {'symbol':"A084RC",'level': 1 },
                {'symbol':"W063RC",'level': 2 },
                {'symbol':"A063RC",'level': 3 },
                {'symbol':"W016RC",'level': 3 },
                {'symbol':"W017RC",'level': 2 },
                {'symbol':"A180RC",'level': 1 },
                {'symbol':"A204RC",'level': 2 },
                {'symbol':"Y712RC",'level': 2 },
                {'symbol':"A107RC",'level': 1 },
                {'symbol':"A922RC",'level': 1 }  
            ]
        }
    },   
    'Account 5' : {
        'meta' :{
            'heading': "Table 5: Foreign Transaction Current Account",
            'caption': "Source: BEA NIPA Table 4.01"          
        },
        'source' :{
            'TableName' : "T40100",
            'TableEntries' : [  
                {'symbol':"W163RC",'level': 0 },
                {'symbol':"B021RC",'level': 1 },
                {'symbol':"A255RC",'level': 2 },
                {'symbol':"A333RC",'level': 3 },
                {'symbol':"A340RC",'level': 3 },
                {'symbol':"B656RC",'level': 2 },
                {'symbol':"A655RC",'level': 1 },
                {'symbol':"B4189C",'level': 2 },
                {'symbol':"W161RC",'level': 2 },
                {'symbol':"B1869C",'level': 3 },
                {'symbol':"B3376C",'level': 3 },
                {'symbol':"B3476C",'level': 3 },
                {'symbol':"A123RC",'level': 1 },
                {'symbol':"B070RC",'level': 2 },
                {'symbol':"B088RC",'level': 2 },
                {'symbol':"W164RC",'level': 2 },
                {'symbol':"A124RC",'level': 0 }
             ]
        },
        'uses' : {
            'TableName' : "T40100",
            'TableEntries' : [
                {'symbol':"A120RC1",'level': 0 },
                {'symbol':"B020RC", 'level': 1 },
                {'symbol':"A253RC", 'level': 2 },
                {'symbol':"A332RC", 'level': 3 },
                {'symbol':"A339RC", 'level': 3 },
                {'symbol':"A646RC", 'level': 3 },
                {'symbol':"B645RC", 'level': 1 },
                {'symbol':"B4188C", 'level': 2 },
                {'symbol':"W160RC", 'level': 2 },
                {'symbol':"A2067C", 'level': 3 },
                {'symbol':"B3375C", 'level': 3 },
                {'symbol':"B3475C", 'level': 3 }
             ]
        }
    },
    'Account 6' : {
        'meta' :{
            'heading':  "Table 6: Domestic Capital Account",
            'caption': "Source: BEA NIPA Tables 5.01"          
        },
        'source' :{
            'TableName' : "T50100",
            'TableEntries' : [
                {'symbol': "A929RC", 'level': 0 },
                {'symbol': "W201RC", 'level': 1 },
                {'symbol': "W202RC", 'level': 2 },
                {'symbol': "A127RC", 'level': 3 },
                {'symbol': "B057RC", 'level': 4 },
                {'symbol': "B058RC", 'level': 4 },
                {'symbol': "A059RC", 'level': 4 },
                {'symbol': "W986RC", 'level': 3 },
                {'symbol': "A071RC", 'level': 4 },
                {'symbol': "A922RC", 'level': 2 },
                {'symbol': "A923RC", 'level': 3 },
                {'symbol': "A924RC", 'level': 3 },
                {'symbol': "A262RC", 'level': 1 },
                {'symbol': "A024RC", 'level': 2 },
                {'symbol': "W276RC", 'level': 3 },
                {'symbol': "W279RC", 'level': 3 },
                {'symbol': "A264RC", 'level': 2 },
                {'symbol': "A918RC", 'level': 3 },
                {'symbol': "A919RC", 'level': 3 },
             ]
        },
        'uses' : {
            'TableName' : "T50100",
            'TableEntries' : [
                {'symbol':"A928RC", 'level':  0 },
                {'symbol':"W170RC", 'level':  1 },
                {'symbol':"A006RC", 'level':  2 },
                {'symbol':"W987RC", 'level':  3 },
                {'symbol':"W988RC", 'level':  3 },
                {'symbol':"A782RC", 'level':  2 },
                {'symbol':"A787RC", 'level':  3 },
                {'symbol':"A799RC", 'level':  3 },
                {'symbol':"W167RC", 'level':  1 },
                {'symbol':"W999RC", 'level':  2 },
                {'symbol':"W989RC", 'level':  3 },
                {'symbol':"W990RC", 'level':  3 },
                {'symbol':"W991RC", 'level':  2 },
                {'symbol':"W992RC", 'level':  3 },
                {'symbol':"W993RC", 'level':  3 },
                {'symbol':"W162RC", 'level':  1 },
                {'symbol':"W994RC", 'level':  2 },
                {'symbol':"W995RC", 'level':  3 },
                {'symbol':"W996RC", 'level':  3 },
                {'symbol':"AD01RC", 'level':  2 },
                {'symbol':"AD02RC", 'level':  3 },
                {'symbol':"AD03RC", 'level':  3 },
                {'symbol':"A030RC", 'level':  0 },
             ]
        }
    }
}