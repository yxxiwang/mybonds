#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time,logging
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
 
# logger = logging.getLogger(__name__)
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
    """
                根据初始数据 生成  每日新闻条数 统计数据
    """
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s " %(beaconusr,beaconid)
#         channelDocs(beaconusr,beaconid)
        doc_cts_key = "channel:"+beaconusr+":"+beaconid+":doc_cts"
        doc_dcnt_key = "channel:"+beaconusr+":"+beaconid+":doc_dcnt"
        doc_dnum_key = "channel:"+beaconusr+":"+beaconid+":doc_dnum"
        for docstr,tms in r.zrange(doc_cts_key,0,-1,withscores=True):
            print docstr,tms,doc_cts_key
            if tms==0:
                r.zrem(doc_cts_key,docstr)
                continue
            tdate = dt.date.fromtimestamp(float(tms)/1000).strftime('%Y%m%d')
            num = int(json.loads(docstr)["num"])
            id = json.loads(docstr)["id"]
            r.hset("copynum",id,num)
            r.zadd(doc_dcnt_key,int(tdate),id)
#             print "%s incr 1 ,num:%d" %(tdate,num)
#             r.hincrby(doc_dcnt_key,tdate,1)
#             r.hincrby(doc_dnum_key,tdate,num)
            
def cleanBeacon(op="print"):
    """ 清理已经删除的频道,并将其从用户的关注列表中清理掉."""
#     for bstr in r.zrevrange("bmk:doc:share",0,-1):

    def deleteBeacon(beaconusr,beaconid):            
        r.zrem("bmk:doc:share",beaconusr+"|-|"+beaconid)
        r.zrem("bmk:doc:share:byfllw",beaconusr+"|-|"+beaconid) 
        r.zrem("bmk:doc:share:bynews",beaconusr+"|-|"+beaconid) 
        r.zrem("usr:" + beaconusr+":fllw",beaconusr+"|-|"+beaconid)
        r.delete("channel:"+beaconusr+":"+beaconid+":doc_cts")
        key = "bmk:"+beaconusr+":"+beaconid
        for usr in r.smembers(key+":fllw"):
            r.zrem("usr:" + usr+":fllw",beaconusr+"|-|"+beaconid)
        r.delete(key + ":doc:tms")
        r.delete(key + ":fllw")
        r.delete(key)
        
    for bstr in r.keys("channel:*doc_cts"):
        bkey = "bmk:"+":".join(bstr.split(":")[1:3])
        if r.type(bkey) != "hash":
            continue
        if r.hget(bkey,"ttl") is None or r.hget(bkey,"ttl")=="" :
            print bstr , ",is null!"
            if op=="delete":
                deleteBeacon(bkey.split(":")[1],bkey.split(":")[2])
        
    for bstr in r.keys("bmk:*"):
#         print bstr,op
        if len(bstr.split(":"))!=3:
            continue
        bkey = ":".join(bstr.split(":")[0:3])
#         print bkey,"==",r.type(bkey)
#         bkey = "bmk:"+bstr.replace("|-|",":")
        if r.type(bkey) != "hash":
            continue
        if r.hget(bkey,"ttl") is None or r.hget(bkey,"ttl")=="" :
            print bkey , ",is null!"
            if op=="delete":
                deleteBeacon(bkey.split(":")[1],bkey.split(":")[2])
                
    key_lst = r.keys("usr:*:fllw")
    for key in key_lst:
        for bstr in r.zrevrange(key,0,-1):
            bkey = "bmk:"+bstr.replace("|-|",":")
            if r.hget(bkey,"ttl") is None:
                print "%s is null in %s,should remove!" % (bkey , key)
                if op=="delete":
                    r.zrem(key,bstr)
    
            
def cleanCountData():
    pass
    
def initBeaconDisplayName():
    """初始化频道的 显示名称 为频道名称"""
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s " %(beaconusr,beaconid)
        key = "bmk:%s:%s" % (beaconusr,beaconid)
        r.hset(key,"name",r.hget(key,"ttl"))
        
def reflect(functionname,parms=""):
    function = globals()[functionname]
    if parms =="":
        return function()
    else:
        return function(parms)

if __name__ == "__main__":  
    usage = """usage:python %prog func
               eg:  
                  python %prog convUsrFllw 
                  python %prog initBeaconDisplayName 
                  python %prog cleanBeacon {print|delete} 
                  python %prog makeDocDateCnt 
                  python %prog convUsrFllw 
            """
    if len(sys.argv) >= 2:
        func = sys.argv[1] 
        if len(sys.argv) ==3:
            parms = sys.argv[2] 
            reflect(func,parms)
        else:
            reflect(func)
    else:
        logger.exception("msg")
        print( usage.replace("%prog", sys.argv[0]))
 
    

    
    

