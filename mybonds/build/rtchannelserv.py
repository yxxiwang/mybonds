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
  
def getChannelNewsCopynumListByTime(parms=[]):
    print parms
    if len(parms) != 5:
        print "parms is %d,not 5!" %len(parms)
        return json.dumps(rdata)
    
    (action,schema,code,dayfrom,dayto)=parms
    rdata = []
    code = "" 
    if action == "stock":
#         print parms[2][2:]
        code = r.hget("stock:channel",parms[2][2:])
    else:
        code = parms[2]
#     print code
    if code is None or code =="":
        print "code is None!"
        return json.dumps(rdata)
     
    def check_int(s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    if not check_int(dayfrom) or  not check_int(dayto):
        print "day is not digit!"
        return json.dumps(rdata)
     
    key = "channel:"+code+":doc_tcnt"
    tmsfrom = ( dt.date.today() + dt.timedelta(int(dayfrom)) ).strftime('%Y%m%d') 
    tmsto = ( dt.date.today() + dt.timedelta(int(dayto)) ).strftime('%Y%m%d')
    tmsfrom = int(tmsfrom+"000000")
    tmsto = int(tmsto+"240000")
    print tmsfrom ,"=",tmsto,"=",key
    if schema == "schema": 
        for docid,tms in r.zrangebyscore(key, tmsfrom, tmsto, 0, -1, withscores=True):
            rdata.append(tms)
    else:
        for docid,tms in r.zrangebyscore(key, tmsfrom, tmsto, 0, -1, withscores=True):
            rdata.append(r.hget("copynum", docid))
    return json.dumps(rdata)
    
    
def getChannelNewsCountsList(parms=[]):
    print parms
    rdata = []
    if len(parms) != 5:
        print "parms is %d,not 5!" %len(parms)
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
#     print "key is %s" % key
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
        for i in xrange(int(dayfrom),int(dayto)+1):
            tdate = (dt.date.today() + dt.timedelta(i)).strftime('%Y%m%d')
#             print tdate
            rdata.append(tdate)
    else:
        for i in xrange(int(dayfrom),int(dayto)+1):
            tdate = (dt.date.today() + dt.timedelta(i)).strftime('%Y%m%d')
            cnt = r.zscore(key, tdate)
#             print tdate,cnt
            cnt = 0 if cnt is None else cnt
            rdata.append(str(cnt))
    return json.dumps(rdata)
#   return ["9527","9528"]

class functionMapping:
  def __init__(self):
    self.controllers = {
      'querySinaFrequence': querySinaFrequence,
      'getChannelNewsCountsList': getChannelNewsCountsList,
      'getChannelNewsCopynumListByTime': getChannelNewsCopynumListByTime,
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
    
    