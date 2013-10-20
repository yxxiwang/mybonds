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
from django.utils.encoding import smart_str
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
from mybonds.apps.beacon import Beacon
import argparse
 
def channels(num):
    start = time.time()
    cnt = r.zcard("bmk:doc:share")
    i = 0
    udata={}
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
        logger.info( "<-----proc %s:%s (%d of %d), time elaspe %s(%d sec) ------>" % (beaconusr,beaconid,i,cnt,elaspestr,diff) )
        
#         print "proc %s:%s and num is %d" %(beaconusr,beaconid,num)
        if not r.exists("bmk:"+beaconusr+":"+beaconid):#如果该频道不存在
            logger.warnning("bmk:%s:%s is not exist!" %(beaconusr,beaconid) )
            continue
        
        if beaconusr not in ["rd","extend"]:
            rt = refreshDocs(beaconusr, beaconid,days="-1",force=force)
            if not rt == SUCCESS:
                pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"-1"})
            
        rt = refreshDocs(beaconusr, beaconid,days="1",force=force)
        if not rt == SUCCESS:
            pushQueue("beacon",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})

        if beaconusr =="extend":
            pushQueue("docextend",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
            
        if beaconusr =="rd":         
            udata = newHotBoardData(beaconusr,beaconid,username="",usecache="0") 
            rt = WARNNING if udata=={} or udata is None else SUCCESS
            if not rt == SUCCESS:
                pushQueue("hotboard",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
                
            udata = procChannel("popularychannel",beaconusr,beaconid,"",days=str(num),usecache="0") 
            rt = WARNNING if udata=={} or udata is None else SUCCESS
            if not rt == SUCCESS:
                pushQueue("popularychannel",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
                 
            udata = procChannel("channelnews",beaconusr,beaconid,"",days=str(num),usecache="0") 
            rt = WARNNING if udata=={} or udata is None else SUCCESS
            if not rt == SUCCESS:
                pushQueue("channelnews",{"beaconusr":beaconusr,"beaconid":beaconid,"days":"1"})
        
def retriveData(qtype):
    qobj = r.rpoplpush("queue:" + qtype, "queue:" + qtype + ":processing")
    if qobj is None:
        return 
    qinfo = {}
    tag = ""
    url=""
    rt = 6 
    start = time.clock()  
    try: 
        logger.info("processing data:\n")
        logger.info(qobj)
        qinfo = json.loads(qobj)
#         username = qinfo["usr"]
#         otype = qinfo["o"]
#         url = qinfo["url"] 
        if qtype =="read": 
            rt = requestUrl(url)
        elif qtype =="beacon": 
            beaconusr = qinfo["beaconusr"]
            beaconid = qinfo["beaconid"]
            days = qinfo["days"] 
            rt = refreshDocs(beaconusr, beaconid,days) 
        elif qtype =="fulltext":  
            urlstr = qinfo["urlstr"] if qinfo.has_key("urlstr") else ""
            ids = qinfo["ids"] if qinfo.has_key("ids") else ""
            udata = saveFulltextById(ids,url=urlstr,frombackend=True) 
            rt= WARNNING if udata=={} or udata is None else SUCCESS
        elif qtype =="removedoc": 
            urlstr = qinfo["urlstr"]
            udata = bench(loadFromUrl,parms=urlstr)
            rt= WARNNING if udata=={} else SUCCESS
        elif qtype =="channelpick": 
            beaconusr = qinfo["beaconusr"]
            beaconid = qinfo["beaconid"]
            days = qinfo["days"]
            rt = refreshDocs(beaconusr, beaconid,days) 
        elif qtype =="hotboard": 
            beaconusr = qinfo["beaconusr"]
            beaconid = qinfo["beaconid"]
            days = qinfo["days"]
            udata = newHotBoardData(beaconusr, beaconid,username="",usecache="0") 
            rt = WARNNING if udata=={} or udata is None else SUCCESS
        elif qtype in ["popularychannel","channelnews","relatedchannel"]:
            beaconusr = qinfo["beaconusr"]
            beaconid = qinfo["beaconid"]
            days = qinfo["days"]
            beaconname = ""
            udata = procChannel(qtype,beaconusr,beaconid,beaconname,days=days,usecache="0") 
            rt = WARNNING if udata=={} or udata is None else SUCCESS
        elif qtype =="docextend":
            beaconusr = qinfo["beaconusr"]
            beaconid = qinfo["beaconid"]
            days = qinfo["days"] if qinfo.has_key("days") else "1"
            beacon = Beacon(beaconusr,beaconid)
            beacon.setDays(int(days))
            udata = beacon.saveExtendData() 
            rt = WARNNING if udata=={} or udata is None else SUCCESS 
        elif qtype =="sendemail":
            emailtype = qinfo["emailtype"]
            if emailtype=="bybeacon":
                hourbefore = qinfo["email"]
                rt = sendEmailFromUserBeacon(username,hourbefore,emailtype)
            elif emailtype=="lostkey":
                email = qinfo["email"]
                rt = sendEmailFindKey(username,email,url)
            elif emailtype=="bydocid":
                email = qinfo["email"]
                docid = qinfo["docid"]
                rt = sendemailbydocid(email,docid)
        else:
            logger.error( "error qtype %s " % qtype)
            rt = 0  
    except:
        traceback.print_exc() 
    if rt == SUCCESS: # SUCCESS=0
        qobj = r.rpoplpush("queue:" + qtype + ":processing", "queue:" + qtype + ":done")
    elif rt == SYSERROR: # SYSERROR=-1
        qobj = r.rpoplpush("queue:" + qtype + ":processing", "queue:" + qtype + ":error")
    else:# COMMUNICATERROR=6 ,WARNNING=8
#             qobj = lib.r.rpoplpush("queue:" + qtype + ":processing", "queue:" + qtype)
        qobj = r.rpop("queue:" + qtype + ":processing")
        qinfo = json.loads(qobj)
        cnt = qinfo["cnt"] if qinfo.has_key("cnt") else 0
        qinfo["cnt"]=cnt+1
        if qinfo["cnt"] < getsysparm("RETRY_TIMES"):
            logger.info( "process it again")
            r.lpush("queue:" + qtype,json.dumps(qinfo))
        else:
            logger.warn( "it's rearch the maxsim count of RETRYCOUNT")
            qinfo["cnt"] = 0# prepire to do again in housekeeping programe
            r.lpush("queue:" + qtype+":error",json.dumps(qinfo)) 
        
    urlstop = time.clock()
    diff = urlstop - start
#     content = smart_str(content)  
    logger.info( "retriveData(%s) has taken on %s;and rt is %d" % (smart_str(url),str(diff),rt) ) 
    return rt
            
def procQueue(type,codes,num,force=False):
    """save fulltext into mongodb, data from backend """
    for i in range(r.llen("queue:" + type+":processing")):#先处理遗留的队列
        qobj=r.rpoplpush( "queue:" + type + ":processing","queue:" + type)
        logger.info( "move qobj%s from queue:%s:processing to queue:%s" %(qobj,type,type) )
    num = r.llen("queue:" + type) if num == -1 else num
    for i in range(num): 
          retriveData(type) 
            
def loadData(codes,num,force=False):        
    """fetch beacon data from backend """
    if codes[0]=="all":
        channels(num)
    else:
        for code in codes:
            beaconusr,beaconid = code.split(":")
            logger.info( "proc %s:%s and num is %d" %(beaconusr,beaconid,num) )
            if beaconusr=="rd":
                newHotBoardData(beaconusr, beaconid,username="",usecache="0") 
            else:
                refreshDocs(beaconusr, beaconid,days=str(num),force=force)
            
def initProc(types,codes,num,force=False): 
    """type should be one of load,beacon,fulltext,sendemail,removedoc """
    try:
        for type in types:
            if type == "load":
                loadData(codes,num,force)
            else:
                procQueue(type,codes,num,force) 
    except:
        traceback.print_exc() 
    else:
        logger.info("initProc is over,time to sleep......")

if __name__ == "__main__":  
    usage = """ eg: %s -c all -a 3600 -n 200 -t load|beacon|fulltext|sendemail|removedoc
            """  % sys.argv[0]
    parser = argparse.ArgumentParser(description='Process stock,bond,etc codes.')
    parser.add_argument("-t", "--type", default=["load"], type=str, nargs='+',
                    help="The type to be processed.")
    
    parser.add_argument("-c", "--code", default=["all"], type=str, nargs='+',
                    help="The code to be processed.") 
    
    parser.add_argument("-a", "--auto", dest="auto",default=0,type=int,
                    help="auto process every other second.")
    
    parser.add_argument("-n", "--num", dest="num",default=1,type=int,
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
        types = options.type
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
               initProc(types,codes,num,force)
               time.sleep(auto)
        else:
            initProc(types,codes,num,force)
            
        
#     action =sys.argv[0]
#     print action
#     if 'dateload' == action:
#         dateload(filename,output=output)

