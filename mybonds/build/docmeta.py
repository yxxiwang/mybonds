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

def saveData(udata):
    for doc in udata["docs"]:
        if not doc["validTime"]:
            continue
        docid = getHashid(doc["url"])
        tms = doc["create_time"]
        r.zadd("channel:"+beaconusr+":"+beaconid+":doc_cts",int(tms),'{"id":%s,"num":%d}' %(docid,doc["copyNum"]))
    
def channelDocs(beaconusr,beaconid): 
    channel = getchannelByid(beaconusr,beaconid)
    if channel is None: 
        print "%s:%s haven't channel !" %(beaconusr,beaconid)
        return
    urlstr="http://www.gxdx168.com/research/svc?channelid="+urllib2.quote(channel) +"&length=2000"  
    udata = bench(loadFromUrl,parms=urlstr)
    if udata.has_key("docs"): 
        saveData(udata)
    else:
        print "%s:%s udata haven't key docs ! do it again.." %(beaconusr,beaconid)
        udata = bench(loadFromUrl,parms=urlstr)
        if udata.has_key("docs"): 
            saveData(udata)
        else:
             print "=============== %s:%s ===============" %(beaconusr,beaconid)

def channels():
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s" %(beaconusr,beaconid)
        channelDocs(beaconusr,beaconid)
        

if __name__ == "__main__":  
    usage = """usage: %prog [options] {load|import|meta|print}
               eg:  
                   %prog meta -u=all -d=3 -m=model1 -s=all
                   %prog print 
            Try '%prog -h' or '%prog --help' for more information.
            """
    parser = argparse.ArgumentParser(description='Process stock,bond,etc codes.')
    parser.add_argument("-c", "--code", default=[], type=str, nargs='+',
                    help="The code to be processed.")
    
    parser.add_argument("-s", "--start", dest="sdate",default="20130101",
                      help="begin date default is 20100101")
         
    parser.add_argument("-e", "--end", dest="edate",default="20140101",
                      help="end date default is 20140101") 
    
    parser.add_argument("-l", "--loglevel", dest="loglevel",default="info",
                      help="loglevel can be:[debug|info]  default is info")
    
    parser.add_argument("-v", "--verbose",action="store_true", dest="verbose",default=True)
    
    parser.add_argument("-q", "--quiet",action="store_false", dest="verbose",
                      help="don't print status messages to stdout")
    
    options = parser.parse_args()
#     print options
#     print sys.argv
#     parser.print_usage()
    if len(sys.argv) < 2:  
        parser.print_usage()
        sys.exit(2)
    
    if options.verbose: 
        codes = options.code
        loglevel = options.loglevel
        start_date = options.sdate
        end_date = options.edate
        print "reading cods  %s..." % options.code
        if codes[0]=="all":
            channels()
        else:
            for code in codes:
                beaconusr,beaconid = code.split(":")
                print "proc %s:%s" %(beaconusr,beaconid)
                channelDocs(beaconusr,beaconid)
        
        
#     action =sys.argv[0]
#     print action
#     if 'dateload' == action:
#         dateload(filename,output=output)

