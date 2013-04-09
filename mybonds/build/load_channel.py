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

def load_data(input):
    r.delete("bmk:doc:share")
    r.delete("bmk:doc:share:byfllw")
    r.delete("bmk:doc:share:bynews")
    for line in open(input):
        (usr,name,desc) = line.split(",")
        if usr=="stockmarket":
            continue
#         desc = name if desc=="" or desc is None else ""
#         name = to_unicode_or_bust(name)
        id = getHashid(name)
        print "usr=%s ;id=%s;name=%s;desc=%s" % (usr,id,name,desc)
        r.zadd("bmk:doc:share",time.time(),usr+"|-|"+id)
        r.zadd("bmk:doc:share:byfllw",time.time(),usr+"|-|"+id)
        r.zadd("bmk:doc:share:bynews",time.time(),usr+"|-|"+id)
        r.sadd("usr:" + usr+":fllw",usr+"|-|"+id)
        beaobj = r.hset("bmk:" + usr + ":" + id,"id",id)
        beaobj = r.hset("bmk:" + usr + ":" + id,"ttl",name) 
        beaobj = r.hset("bmk:" + usr + ":" + id,"desc",desc) 
        beaobj = r.hset("bmk:" + usr + ":" + id,"crt_usr",usr) 
        beaobj = r.hset("bmk:" + usr + ":" + id,"crt_tms",time.time())
        beaobj = r.hset("bmk:" + usr + ":" + id,"brk_tms",time.time()) 
        beaobj = r.hset("bmk:" + usr + ":" + id,"cnt",0) 
        
if __name__ == "__main__":
    load_data("channel.dat")