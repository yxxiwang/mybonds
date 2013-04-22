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
def test():
    print "hello world!"
    
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
#         if 'convUsrFllw' ==func: 
#             print "func is %s" % func
#             bench(convUsrFllw)
#         else:
        reflect(func)
    else:
        print usage.replace("%prog", sys.argv[0])

            
    
    
    
    

