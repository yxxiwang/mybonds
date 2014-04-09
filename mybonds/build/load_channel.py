#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys, time
import redis
import numpy

r = redis.StrictRedis()

def getHashid(ustr):
    h = 0
    if ustr == None:
        return h 
    for c in ustr:
        h = numpy.int64(31 * h + ord(c))
    h = abs(h)
    return str(h)

def to_unicode_or_bust(obj, encoding='utf-8'):
     if obj is None:
         return "" 
     if isinstance(obj, basestring):
         if not isinstance(obj, unicode):
             obj = unicode(obj, encoding)
     return obj

def load_data(input,parms):
#     r.delete("bmk:doc:share")
#     r.delete("bmk:doc:share:byfllw")
#     r.delete("bmk:doc:share:bynews")
    for line in open(input):
        if line.startswith("#"):
            continue
        if line.startswith("\n"):
            continue
        if line=="":
            continue
        dlist = line.split(",")
        (disname,name,usr,tag) = dlist[0],dlist[1],dlist[2],dlist[3:]
        tag = ",".join(tag)
#         tag ="" 
#         if len(dlist) >=5:
#             tag = dlist[4]
        #if usr=="stockmarket":
        #    continue
#         desc = name if desc=="" or desc is None else ""
#         name = to_unicode_or_bust(name)
#         id = getHashid(name) 
        id = getHashid(name.decode("utf8"))
        
        if r.zscore("bmk:doc:share",usr+"|-|"+id) and parms !="force":
            continue
        
#         print dlist
        print "usr=%s;id=%s;name=%s;tag=%s" % (usr,id,name,tag)
        r.zadd("bmk:doc:share",time.time(),usr+"|-|"+id)
        r.zadd("bmk:doc:share:byfllw",time.time(),usr+"|-|"+id)
        r.zadd("bmk:doc:share:bynews",time.time(),usr+"|-|"+id)
        r.zadd("usr:" + usr+":fllw",time.time(),usr+"|-|"+id)
        beaobj = r.hset("bmk:" + usr + ":" + id,"id",id)
        beaobj = r.hset("bmk:" + usr + ":" + id,"ttl",name)
        beaobj = r.hset("bmk:" + usr + ":" + id,"name",disname)
        beaobj = r.hset("bmk:" + usr + ":" + id,"desc",disname)
        beaobj = r.hset("bmk:" + usr + ":" + id,"crt_usr",usr)
        beaobj = r.hset("bmk:" + usr + ":" + id,"crt_tms",time.time())
        beaobj = r.hset("bmk:" + usr + ":" + id,"last_touch",0)
        beaobj = r.hset("bmk:" + usr + ":" + id,"last_update",0)
        beaobj = r.hset("bmk:" + usr + ":" + id,"cnt",0)
        beaobj = r.hset("bmk:" + usr + ":" + id,"tag",tag)
#         beaobj = r.hset("bmk:" + usr + ":" + id,"tag",tag.replace(";", ",")) 
        
if __name__ == "__main__":
    parms =""
    if len(sys.argv) ==2:
        parms = sys.argv[1] 
#     print sys.argv
    load_data("channel.dat",parms)
    