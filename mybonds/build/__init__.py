#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time
import redis
import numpy
import traceback 
import datetime as dt
from numpy.ma.core import isMA
from sys import path
from os import getcwd
import os
path.append(getcwd())# current dir
if os.name =="nt":
#     path.append(os.path.abspath('..\..\..'))# mybonds's parrent dir
    path.append("C:\Users\wangxi\git\mybonds")
else:#os.name=="posix"
#     path.append(os.path.abspath('../../..'))# mybonds's parrent dir
    path.append("/root") 
from mybonds.apps import *
from mybonds.apps.newspubfunc import *
import argparse
 
def convUsrFllw():
    """ 将  用户关注的key 由 set 类型换成 zset 类型.
                            该函数已经被执行过,即可以宣布作废(现在应该已经用不上了)
    """
    keys = r.keys("usr:*:fllw")
    for key in keys:
        print "proc key %s" % key
        beaconstrs = r.smembers(key)
        for beaconstr in beaconstrs:
            print "zadd %s into %s" %(beaconstr,key+":z")
            r.zadd(key+":z",time.time(),beaconstr)
            
        print "delete key %s" %(key)
        r.delete(key)
        print "rename %s to %s" %(key+":z",key)
        r.rename(key+":z",key) 
    return 0
#     r.srem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)

def makeDocDateCnt():
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s " %(beaconusr,beaconid)
#         channelDocs(beaconusr,beaconid)
        doc_cts_key = "channel:"+beaconusr+":"+beaconid+":doc_cts"
        doc_dcnt_key = "channel:"+beaconusr+":"+beaconid+":doc_dcnt"
        doc_dnum_key = "channel:"+beaconusr+":"+beaconid+":doc_dnum"
        for docstr,tms in r.zrevrangebyscore(doc_cts_key,(time.time()+8*3600)*1000,0,withscores=True):
            print docstr,tms,doc_cts_key
            tdate = dt.date.fromtimestamp(float(tms)/1000).strftime('%Y%m%d')
            num = int(json.loads(docstr)["num"])
            print "%s incr 1 ,num:%d" %(tdate,num)
            r.hincrby(doc_dcnt_key,tdate,1)
            r.hincrby(doc_dnum_key,tdate,num)
            
    
def reflect(functionname):
    function = globals()[functionname]
    return function()

if __name__ == "__main__":  
    usage = """usage:python %prog func
               eg:  
                  python %prog convUsrFllw 
            """
    if len(sys.argv) >= 2:
        func = sys.argv[1] 
        reflect(func)
    else:
        print usage.replace("%prog", sys.argv[0])
 
    

    
    

