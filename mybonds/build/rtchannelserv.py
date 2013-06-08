#!/usr/bin/python

import os,string,sys,time,re
import redis,json
import zmq
import RTCfg
import datetime as dt
import datetime
# import fcntl

r = redis.StrictRedis()

def querySinaFrequence():
  return RTCfg.timeWindow['sinaIntervalTime']
  
def getChannelNewsCountsList(parms=[]):
    print parms
    rdata = {}
    if len(parms) != 3:
        return "{}"
    
    action = parms[0]
    if action == "stock":
        print parms[1][2:]
        code = r.hget("stock:channel",parms[1][2:])
    else:
        code = parms[1]
        
    if code is None or code =="":
        return "{}"
    
    key = "channel:"+code+":cnt"
    days = parms[2]
    
    if not days.isdigit():
        return "{}"
  
    for i in xrange(int(days)):
        tdate = (dt.date.today() - dt.timedelta(i)).strftime('%Y%m%d')
        cnt = r.zscore(key, tdate)
        cnt = 0 if cnt is None else cnt
        rdata[tdate]= cnt
        
    return json.dumps(rdata)
#   return ["9527","9528"]

class functionMapping:
  def __init__(self):
    self.controllers = {
      'querySinaFrequence': querySinaFrequence,
      'getChannelNewsCountsList': getChannelNewsCountsList,
      #'/logout/':logout,
    }

if __name__ == '__main__':

  context = zmq.Context()
  funcMapping = functionMapping()
  
  socket = context.socket(zmq.REP) 
  socket.bind(RTCfg.zmqPort['systemParameterServicePort'])

  while True:
    #  Wait for next request from client
    message = socket.recv()
    message = message.rstrip()
    ary = re.split('\s+',message)

    #  Send reply back to client
    retFunc = funcMapping.controllers.get(ary[0])
    if retFunc:
      socket.send(retFunc(ary[1:]))
    else:
      socket.send("no this function")
    time.sleep(5)
    
    