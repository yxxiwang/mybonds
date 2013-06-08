
timeWindow  = {
  'sinaIntervalTime':   "4",     #get sina stock frequency 5--> 5s
  'firstMeanIntervalTime':"30", 
    
  'firstMeanStartTimePoint':"083000",
  'firstMeanEndTimePoint':"150500",

}
zmqPort= {
        'systemParameterServicePort':       'tcp://*:30000',  
        'systemParameterClientPort':      'tcp://localhost:30000',  
        'stockGroupServicePort':                'tcp://*:30010',  
        'stockGroupClientPort':           'tcp://localhost:30010',  
          
        'sinaDataProcessServicePort':       'tcp://*:30200',  
        'sinaDataProcessClientPort':      'tcp://localhost:30200',  

        'firstMeanTimeWindowServicePort':       'tcp://*:30300',  
        'firstMeanTimeWindowClientPort':  'tcp://localhost:30300',  
        'firstMeanCalcServicePort':           'tcp://*:30310',  
        'firstMeanCalcClientPort':        'tcp://localhost:30310',  
          
        'RmeanCalcServicePort':       'tcp://*:5550',  
        'RmeanCalcClientPort':        'tcp://localhost:5550',  


}

stkSinaMeta={
  'todayOpeningPrice':'intf:sa:0',
  'yesterdayClosingPrice':'intf:sa:1',
  'currentPrce':'intf:sa:2',
  'todayHighPrice':'intf:sa:3',
  'todayLowPrice':'intf:sa:4',
  'askL1Price':'intf:sa:5',
  'sellL1Price':'intf:sa:6',
  'transactionVolume':'intf:sa:7',
  'transactionAmount':'intf:sa:8',
  'dataTimestamp':'intf:sa:32',


}


JSON = {

}