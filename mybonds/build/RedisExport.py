#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time
import redis,re
import traceback 
import datetime as dt
from sys import path
from os import getcwd
import os

r = redis.StrictRedis()
def exportkey(pattan="*"):
    """按照redis的key的模糊匹配规则 导出相应的数据 为command """
#     print pattan
    for rkey in r.keys(pattan):
#         print rkey
        if r.type(rkey) == "hash":
            for data in r.hgetall(rkey).iteritems():
                print "hset %s %s %s " % (rkey,data[0],data[1])
        elif r.type(rkey) =="zset":
            for data,score in r.zrevrange(rkey,0,-1,withscores=True):
                print "zadd %s %d %s" % (rkey,score,data)
        elif r.type(rkey) =="list":
            for data in r.lrange(rkey, 0, -1):
                print "rpush %s %s" % (rkey,data)
        elif r.type(rkey) == "string":
            print "set %s %s" % (rkey,data)
        elif r.type(rkey) == "set":
            for data in r.smembers(rkey):
                print "sadd %s %s" % (rkey,data)

def cleanvalue(parms=[]):
    """按照redis的key的模糊匹配规则  并根据数据清理规则,清理相应的数据"""
    pattan=parms[0]
    rules=parms[1:]
    
    def ismatch(rules,dkey):
        for rule in rules:
            if rule[0]==">" and dkey>rule[1:]:
                return True
            elif rule[0]=="<" and dkey<rule[1:]:
                return True
        
    for rkey in r.keys(pattan):
        if r.type(rkey) == "hash":
            for data in r.hgetall(rkey).iteritems():
                if ismatch(rules, data[0]):
                    print "hdel %s %s " % (rkey,data[0])
        elif r.type(rkey) =="zset":
            for data in r.zrevrange(rkey,0,-1):
                if ismatch(rules, data):
                    print "zrem %s %s" % (rkey,data) 
    
def reflect(functionname,parms=""):
    function = globals()[functionname]
    if parms =="":
        return function()
    else:
        return function(parms)

if __name__ == "__main__":  
    usage = """usage:python %prog func
               eg:  
                  python %prog exportkey if:*
                  python %prog cleanvalue if:* "<090000"  ">150100"
            """
    if len(sys.argv) >= 2:
        func = sys.argv[1] 
        if len(sys.argv) ==3:
            parms = sys.argv[2] 
            reflect(func,parms)
        elif len(sys.argv) >3:
            parms = sys.argv[2:] 
            reflect(func,parms)
        else:
            reflect(func)
    else:
        print( usage.replace("%prog", sys.argv[0]))
 
