#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os,string,sys,time,re
import redis,json
import zmq
import RTCfg
import datetime as dt
import datetime
# import fcntl
import warnings

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

r = redis.StrictRedis()

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def querySinaFrequence(parms=[]):
  return RTCfg.timeWindow['sinaIntervalTime']
  
def getNewsCoypNums(parms=[]):
    print parms
    rdata = []
    if len(parms) < 6:
        print "parms is %d,less than 6!" %len(parms)
        return json.dumps(rdata)
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    code = "" 
    if action == "stock": 
        code = r.hget("stock:channel",parms[2][2:])
    else:
        code = parms[2]
    if code is None or code =="":
        print "code is None!"
        return json.dumps(rdata)
    
    if not check_int(dayfrom) or not check_int(dayto) or not check_int(timedelta):
        print "day is not digit!"
        return json.dumps(rdata)
    
    key = "channel:"+code+":doc_tcnt"
    if schema == "schema": 
        for i in xrange(int(dayfrom),int(dayto)+1):
            tdate = (dt.date.today() + dt.timedelta(i)).strftime('%Y%m%d')
            rdata.append(tdate)
    else:
        for i in xrange(int(dayfrom),int(dayto)+1):
            tmsfrom = ( dt.date.today() + dt.timedelta(i-1) ).strftime('%Y%m%d')
            tmsfrom = tmsfrom+timedelta #"140000"
            tmsto = ( dt.date.today() + dt.timedelta(i) ).strftime('%Y%m%d')
            tmsto = tmsto+timedelta
            cnt = 0
            for docid in r.zrangebyscore(key, int(tmsfrom),int(tmsto), 0, -1):
                cnt += int(r.hget("copynum", docid))
#             cnt = 0 if cnt is None else cnt
#             print "%s--->%s cnt is:%d" % (tmsfrom,tmsto,cnt)
            rdata.append(str(cnt)) 
    return json.dumps(rdata)
    
def getNewsCnts(parms=[]):
    print parms
    rdata = []
    if len(parms) < 6:
        print "parms is %d,less than 6!" %len(parms)
        return json.dumps(rdata)
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    code = "" 
    if action == "stock": 
        code = r.hget("stock:channel",parms[2][2:])
    else:
        code = parms[2]
    if code is None or code =="":
        print "code is None!"
        return json.dumps(rdata)
    
    if not check_int(dayfrom) or not check_int(dayto) or not check_int(timedelta):
        print "day is not digit!"
        return json.dumps(rdata)
    
    key = "channel:"+code+":doc_tcnt"
    
#     tmsfrom = ( dt.datetime.now() + dt.timedelta(int(dayfrom)-1) )
#     tmsto = ( dt.datetime.now() + dt.timedelta(int(dayto)+1) )
#     
#     tmsfromstr = "%.4d%.2d%.2d140000" % (tmsfrom.year,tmsfrom.month,tmsfrom.day) 
#     tmsto = "%.4d%.2d%.2d140000" % (tmsto.year,tmsto.month,tmsto.day) 
#     print tmsfrom ,"=",tmsto,"=",key
    if schema == "schema": 
        for i in xrange(int(dayfrom),int(dayto)+1):
            tdate = (dt.date.today() + dt.timedelta(i)).strftime('%Y%m%d')
            rdata.append(tdate)
    else:
        for i in xrange(int(dayfrom),int(dayto)+1):
            tmsfrom = ( dt.date.today() + dt.timedelta(i-1) ).strftime('%Y%m%d')
            tmsfrom = tmsfrom+timedelta #"140000"
            tmsto = ( dt.date.today() + dt.timedelta(i) ).strftime('%Y%m%d')
            tmsto = tmsto+timedelta
            cnt = r.zcount(key,int(tmsfrom),int(tmsto))
            cnt = 0 if cnt is None else cnt            
#             print "%s--->%s cnt is:%d" % (tmsfrom,tmsto,cnt)
            rdata.append(str(cnt)) 
#         for docid,tms in r.zrangebyscore(key, tmsfrom, tmsto, 0, -1, withscores=True):
#             rdata.append(r.hget("copynum", docid))
    return json.dumps(rdata)
     
#     
# def getNewsCntsFromDate(parms=[]):
#     print parms
#     rdata = []
#     if len(parms) < 6:
#         print "parms is %d,less than 6!" %len(parms)
#         return json.dumps(rdata)
#     (action,schema,code,dayfrom,daycnt,timedelta)=parms
#     code = "" 
#     if action == "stock": 
#         code = r.hget("stock:channel",parms[2][2:])
#     else:
#         code = parms[2]
#     if code is None or code =="":
#         print "code is None!"
#         return json.dumps(rdata)
#     
#     if not check_int(dayfrom) or not check_int(daycnt) or not check_int(timedelta):
#         print "day is not digit!"
#         return json.dumps(rdata)
#     
#     print dayfrom+timedelta
#     key = "channel:"+code+":doc_tcnt"
#     if schema == "schema": 
#         for i in xrange( int(daycnt)+1 ):
#             fromdate=dt.datetime.strptime(dayfrom, "%Y%m%d")  
#             tdate = (fromdate + dt.timedelta(i)).strftime('%Y%m%d')
#             rdata.append(tdate)
#     else:
#         for i in xrange( int(daycnt)+1 ):
# #             tmsfrom = ( dt.date.today() + dt.timedelta(i-1) ).strftime('%Y%m%d')
# #             tmsfrom = tmsfrom+timedelta #"140000"
# #             tmsto = ( dt.date.today() + dt.timedelta(i) ).strftime('%Y%m%d')
# #             tmsto = (fromdate + dt.timedelta(i)).strftime("%Y%m%d%H%M%S")
# #             tmsto = tmsto+timedelta
#             tmsfrom = dayfrom+timedelta
#             fromdate=dt.datetime.strptime(dayfrom, "%Y%m%d")
#             tmsto = (fromdate + dt.timedelta(i) ).strftime('%Y%m%d')
#             tmsto = tmsto+timedelta
#             cnt = r.zcount(key,int(tmsfrom),int(tmsto))
#             cnt = 0 if cnt is None else cnt            
# #             print "%s--->%s cnt is:%d" % (tmsfrom,tmsto,cnt)
#             rdata.append(str(cnt))  
#     return json.dumps(rdata)
    
    
def getChannelNewsCopynumListByTime(parms=[]):
    print parms
    if len(parms) != 5:
        print "parms is %d,not 5!" %len(parms)
        return json.dumps(rdata)
    
    (action,schema,code,dayfrom,dayto)=parms
    rdata = []
    code = "" 
    if action == "stock": 
        code = r.hget("stock:channel",parms[2][2:])
    else:
        code = parms[2] 
    if code is None or code =="":
        print "code is None!"
        return json.dumps(rdata) 

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
    
@deprecated
def getChannelNewsCountsList(parms=[]):
    print parms
    rdata = []
    if len(parms) < 5:
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

def getChannelStock(parms=[]):
    (cpcode,)=parms
    cpstocklst=[]
    bmkkey = "bmk:%s" % r.hget("stock:channel", cpcode[2:])
    if not r.exists(bmkkey):
        return "[]"
    print bmkkey
    channels = r.hget(bmkkey,"channels").split(",")
    
    ttl = r.hget(bmkkey,"ttl")
    #根据标签取概念频道项下的股票
    for bstr in r.zrevrange("bmk:doc:share",0,-1):
        bkey = "bmk:"+bstr.replace("|-|",":")
        tags = r.hget(bkey,"tag") 
        tags = "" if tags is None else tags
        bttl = r.hget(bkey,"ttl")
        if re.search(ttl,tags) and bttl not in channels:
            channels.append( bttl ) 
            
    def addhead(channel):
        if int(channel) > 599999:
            return "sh"+channel
        else:
            return "sz"+channel 
        
    channels = [addhead(channel) for channel in channels if channel.isdigit()]
    cpstk = """ "%s":'''%s''', """ % (cpcode,",".join(channels))
    print cpstk
#     cpstocklst.append(",".join(channels))
    return json.dumps(channels)

def getCPinfo(parms=[]):
    (schema,code)=parms
    beacons = []
    rdata = []
    
#     gobj = r.hgetall("group:829105579")
    gobj = r.hgetall("group:"+code)
#     print gobj,schema
    if not gobj.has_key("name") :
        return "[]"
    for bstr in r.zrevrange("bmk:doc:share",0,-1):
#             busr,bid = bstr.split("|-|")
        key = "bmk:"+bstr.replace("|-|",":")
        bttl = r.hget(key,"tag")
        bttl = "" if bttl is None else bttl
        if re.search(gobj["name"],bttl): 
            beacons.append(r.hgetall(key))
            r.hset("cp:channel", key, r.hget(key, "crt_usr")+":"+r.hget(key, "id"))
    if schema == "schema":
        rdata = ["cp99%.4d" % i for i in range(1,len(beacons)+1)]
        for i, bobj in enumerate(beacons):
            cpkey = "99%.4d" % (i+1,)
            r.hset("stock:channel", cpkey, bobj["crt_usr"]+":"+bobj["id"])
            print cpkey, bobj["crt_usr"]+":"+bobj["id"]
    else: 
        rdata = [bobj["name"] for bobj in beacons]
#         print beacons
#         print '["%s"]' % '","'.join(rdata)
    return '["%s"]' % '","'.join(rdata)
#     return json.dumps(rdata)
            
class functionMapping:
  def __init__(self):
    self.controllers = {
      'querySinaFrequence': querySinaFrequence,
      'getChannelNewsCountsList': getChannelNewsCountsList,
      'getChannelNewsCopynumListByTime': getChannelNewsCopynumListByTime,
      'getNewsCnts': getNewsCnts,
      'getNewsCoypNums': getNewsCoypNums,
      'getChannelStock': getChannelStock,
      'getCPinfo': getCPinfo,
#       'getNewsCntsFromDate': getNewsCntsFromDate,
      #'/logout/':logout,
    }

if __name__ == '__main__':
#     print getCPinfo(["schema","829105579"])
#     print getCPinfo(["data","829105579"])
#     print "==getChannelStock=="
#     print getChannelStock(["cp990001"])
#     print getChannelStock(["cp990002"])
#     exit(0)

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
    
    