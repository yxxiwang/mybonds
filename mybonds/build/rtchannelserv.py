#!/usr/bin/python

import os,string,sys,time,re
import redis,json
import zmq
import RTCfg
import datetime as dt
import datetime
# import fcntl

r = redis.StrictRedis()

def querySinaFrequence(parms=[]):
  return RTCfg.timeWindow['sinaIntervalTime']
  
def getChannelNewsCountsList(parms=[]):
    print parms
    rdata = []
    if len(parms) != 5:
        print "parms is %d,not 4!" %len(parms)
        return json.dumps(rdata)
    code = ""
    action = parms[0]
    if action == "stock":
#         print parms[2][2:]
        code = r.hget("stock:channel",parms[2][2:])
    else:
        code = parms[2]
#     print code
    if code is None or code =="":
        print "code is None!"
        return json.dumps(rdata)
    
    key = "channel:"+code+":cnt"
    dayfrom = parms[3]
    dayto = parms[4]
    def check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    if not check_int(dayfrom) or  not check_int(dayto):
        print "day is not digit!"
        return json.dumps(rdata)
    
    schema = parms[1]
    if schema == "schema":
        for i in xrange(int(dayfrom),int(dayto)):
            tdate = (dt.date.today() + dt.timedelta(i)).strftime('%Y%m%d')
#             print tdate
            rdata.append(tdate)
    else:
        for i in xrange(int(dayfrom),int(dayto)):
            tdate = (dt.date.today() - dt.timedelta(i)).strftime('%Y%m%d')
            print tdate
            cnt = r.zscore(key, tdate)
            cnt = 0 if cnt is None else cnt
            rdata.append(str(cnt))
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
#     time.sleep(5)
    
    