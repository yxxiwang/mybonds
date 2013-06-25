#!/usr/bin/python

import os,string,sys,time,re
import redis,json
import zmq
# import RTCfg
import CfgGrp
import datetime as dt
import datetime
# import fcntl

r = redis.StrictRedis()
ccnt_data={}
ccopynum_data={}

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def querySinaFrequence(parms=[]):
    return ""
#   return RTCfg.timeWindow['sinaIntervalTime']

def getNewsCnts(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    
    if schema =="schema" :
        return ccnt_data["date"]
    else:
        rtstr = ccnt_data[code] if ccnt_data.has_key(code) else "has no key:"+code
        return rtstr 
    
def getNewsCntsFromDate(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    
    if schema =="schema" :
        return ccnt_data["date"]
    else:
        rtstr = ccnt_data[code] if ccnt_data.has_key(code) else "has no key:"+code
        return rtstr 
    
def getNewsCoypNums(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    
    if schema =="schema" :
        return ccopynum_data["date"]
    else: 
        rtstr = ccopynum_data[code] if ccopynum_data.has_key(code) else "has no key:"+code
        return rtstr 

def getNewsCoypNumsFromDate(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    
    if schema =="schema" :
        return ccopynum_data["date"]
    else: 
        rtstr = ccopynum_data[code] if ccopynum_data.has_key(code) else "has no key:"+code
        return rtstr 

def initData(parms=[]):
    context = zmq.Context()   
    socket = context.socket(zmq.REQ)  
    socket.connect ('tcp://121.199.37.23:30000')
    print "============getNewsCnts================"
    
    socket.send ("getNewsCnts stock schema sh300088 -60 -1 240000")   
    message = socket.recv()
    print "dates is:",message
    ccnt_data["date"]= message
    ccopynum_data["date"]= message
#     for i in xrange(1,5):
    stockliststr = CfgGrp.AGroup["1"]
    for stockcode in stockliststr.split(","):
        print "proc: ",stockcode
        
        socket.send ("getNewsCnts stock data "+stockcode+"  -60 -1 240000")  
        message = socket.recv() 
        ccnt_data[stockcode]=message
        
        socket.send ("getNewsCoypNums stock data "+stockcode+"  -60 -1 240000")  
        message = socket.recv() 
        ccopynum_data[stockcode]=message 
    
    
class functionMapping:
  def __init__(self):
    self.controllers = {
      'querySinaFrequence': querySinaFrequence,
      'getNewsCnts': getNewsCnts,
      'getNewsCoypNums': getNewsCoypNums,
      'getNewsCntsFromDate': getNewsCntsFromDate,
      'getNewsCoypNumsFromDate': getNewsCoypNumsFromDate,
      #'/logout/':logout,
    }

if __name__ == '__main__':

  context = zmq.Context()
  funcMapping = functionMapping()
  
  socket = context.socket(zmq.REP) 
  socket.bind("tcp://*:39527")
  initData()
  print "====getNewsCnts is okay====="
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
    
    