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

# from mybonds.apps import *
# import __init__ as lib

from mybonds.apps.geeknews import *  
from mybonds.apps.newspubfunc import *  
import argparse

num = 0
def channels():
    start = time.time()
    cnt = r.zcard("bmk:doc:share")
    i = 0
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        i= i+1
        beaconusr,beaconid = beaconstr.split("|-|")
        elaspestr =""
        minbefore =0
        stop = time.time()
        diff = stop - start
        hourbefore = diff // 3600
        if hourbefore == 0:
            minbefore = diff // 60
            elaspestr = str(minbefore) + " minites "
        else:
            elaspestr = str(hourbefore) + " hours "
        print "<-----proc %s:%s (%d of %d), time elaspe %s(%d sec) ------>" % (beaconusr,beaconid,i,cnt,elaspestr,diff)
        
#         print "proc %s:%s and num is %d" %(beaconusr,beaconid,num)
        
        rt = refreshDocs(beaconusr, beaconid,daybefore=num,force=force)
        if not rt == SUCCESS:
            urlstr = beaconUrl(beaconusr, beaconid)
            pushQueue("beacon", beaconusr, "beacon", beaconid,urlstr=urlstr)
#         channelDocs(beaconusr,beaconid)
        
def initProc(codes,force=False):
        if codes[0]=="all":
            channels()
        else:
            for code in codes:
                beaconusr,beaconid = code.split(":")
                print "proc %s:%s and num is %d" %(beaconusr,beaconid,num)
#                 channelDocs(beaconusr,beaconid)
                refreshDocs(beaconusr, beaconid,daybefore=num,force=force)
    

if __name__ == "__main__":  
    usage = """ eg: %s -c all -a 3600 -n 200
            """  % sys.argv[0]
    parser = argparse.ArgumentParser(description='Process stock,bond,etc codes.')
    parser.add_argument("-c", "--code", default=[], type=str, nargs='+',
                    help="The code to be processed.")
    
    parser.add_argument("-a", "--auto", dest="auto",default=0,type=int,
                    help="auto process every other second.")
    
    parser.add_argument("-n", "--num", dest="num",default=20,type=int,
                    help="fetchdata before date from backend (use in urls).")
    
    parser.add_argument("-f", "--force", dest="force",default=False,
                    help="force flag")
    
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
        print usage
        sys.exit(2)
    
    if options.verbose: 
        codes = options.code
        loglevel = options.loglevel
        start_date = options.sdate
        end_date = options.edate
        auto = options.auto
        num = options.num
        force = options.force
        print "reading cods  %s..." % options.code
        if auto!=0:
           while True:
               initProc(codes,force)
               time.sleep(auto)
        else:
            initProc(codes,force)
            
        
#     action =sys.argv[0]
#     print action
#     if 'dateload' == action:
#         dateload(filename,output=output)

