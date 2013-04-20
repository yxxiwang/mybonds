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

def channelDocs(beaconusr,beaconid): 
    channel = getchannelByid(beaconusr,beaconid)
    urlstr="http://www.gxdx168.com/research/svc?channelid="+urllib2.quote(channel) +"&length=2000"  
    udata = bench(loadFromUrl,parms=urlstr)
    for doc in udata["docs"]:
        docid = getHashid(doc["url"])
        tms = doc["create_time"]
        r.zadd("channel:"+beaconusr+":"+beaconid+":doc_cts",int(tms),docid)

def channels():
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s" %(beaconusr,beaconid)
        channelDocs(beaconusr,beaconid)
        
channels()
    

