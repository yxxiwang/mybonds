#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time,logging
import redis,re
import numpy
import traceback 
import datetime as dt
from numpy.ma.core import isMA
from sys import path
from os import getcwd
import os
from numpy import bench
path.append(getcwd())# current dir
if os.name =="nt":
#     path.append(os.path.abspath('..\..\..'))# mybonds's parrent dir
    path.append("C:\Users\wangxi\git\mybonds")
else:#os.name=="posix"
#     path.append(os.path.abspath('../../..'))# mybonds's parrent dir
    path.append("/root") 
from mybonds.apps import *
from mybonds.apps.geeknews import saveFulltextById
from mybonds.apps.newspubfunc import *
import argparse
 
# logger = logging.getLogger(__name__)
def addPopularity():
    """ 将所有新闻的popularity添加上,原来没有该字段的给 0
    """
    keys = rdoc.keys("doc:*")
    for key in keys:
#         print "proc key %s" % key
        if not rdoc.hexists(key,"popularity"):
            print "proc key %s" % key
            rdoc.hset(key,"popularity","0")
    return 0
#     r.srem("usr:" + username+ ":fllw" , heartusr+"|-|"+heartid)

def makeDocTimeCnt():
    """
                根据doc_dcnt初始数据 生成  实时新闻条数 基础数据 doc_tcnt
    """
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s " %(beaconusr,beaconid)
        doc_dcnt_key = "channel:"+beaconusr+":"+beaconid+":doc_dcnt"
        doc_tcnt_key = "channel:"+beaconusr+":"+beaconid+":doc_tcnt"
        channel_cnt_key = "channel:"+beaconusr+":"+beaconid+":cnt"
        for docid in r.zrange(doc_dcnt_key,0,-1):
            tms = rdoc.hget("doc:"+docid,"create_time")
            if tms is None or tms==0:
                print "warnning: %s is not exsist!" % docid
                continue
#             if os.name =="nt":
#                 tms=int(tms)/1000 
            tms=getTime(int(tms)/1000)
#             tms = tms.replace(":","")
            tms = re.sub(r":|-|\s", "", tms)
            r.zadd(doc_tcnt_key,long(tms),docid)
            
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
        channel_cnt_key = "channel:"+beaconusr+":"+beaconid+":cnt"
        for docstr,tms in r.zrange(doc_cts_key,0,-1,withscores=True):
#             print docstr,tms,doc_cts_key
            if tms==0:
                r.zrem(doc_cts_key,docstr)
                continue
            tdate = dt.date.fromtimestamp(float(tms)/1000).strftime('%Y%m%d')
            num = int(json.loads(docstr)["num"])
            id = json.loads(docstr)["id"]
            r.hset("copynum",id,num)
            r.zadd(doc_dcnt_key,int(tdate),id)
        
        cnt = 0
        for i in xrange(120):
            tdate = (dt.date.today() - timedelta(i)).strftime('%Y%m%d')
            cnt = r.zcount(doc_dcnt_key,int(tdate),int(tdate))
            if cnt >0:
                r.zadd(channel_cnt_key,cnt,int(tdate))
#             print doc_dcnt_key,"--",int(tdate),"==",cnt
#             if cnt !=0:
#                 print cnt
            
#             print "%s incr 1 ,num:%d" %(tdate,num)
#             r.hincrby(doc_dcnt_key,tdate,1)
#             r.hincrby(doc_dnum_key,tdate,num)

def cleanChannelCnt(op="print"): 
    """ 清理多余的 频道统计的key"""
    for bstr in r.keys("channel:*cnt"):
        bkey = "bmk:"+":".join(bstr.split(":")[1:3])
        if not r.exists(bkey):
            print "%s is not exists with %s !" % (bkey,bstr)
            if op=="delete":
                r.delete(bstr) 
                
def cleanChannelByCode(parms=("doc:1257408","print")):
    """ 只清理指定的频道新闻数据."""
    if type(parms).__name__ == "str":
        parms = (parms,) 
    op=parms[-1]
    (beaconusr,beaconid) = parms[0].split(":")
    if op == "delete":
        deleteBeacon(beaconusr,beaconid)
#         r.delete("channel:"+beaconusr+":"+beaconid+":doc_cts")
#         key = "bmk:"+beaconusr+":"+beaconid 
#         ttl = r.hget(key,"ttl") 
#         r.delete(key + ":doc:tms")
#         print "%s:doc:tms ---> %s  cleaned.." % (key,ttl)
    else:
        bkey = "bmk:"+parms[0]
        ttl = r.hget(bkey,"ttl")
        print "%s ---> %s" % (bkey,ttl)
        
        
def updateChannelAndStock(parms=("24")):
    urlstr = "http://%s/research/svc?hotstock=%s" % (getsysparm("BACKEND_DOMAIN"), parms[0])    
    udata = loadFromUrl(urlstr) 
    udata.reverse()
    for rc in udata:#{"channelName":"000002(万科Ａ)","channelId":"*000002(万科Ａ)","eventCreateTime":-1,"docId":-1,"docCreateTime":-1,"size":0}
#         beaid = getHashid(doc["channelId"])        
        beaconname = rc["channelName"].replace("*","")
        addBeacon("stockmark", getHashid(rc["channelId"]), rc["channelName"], beaconname=beaconname, desc=rc["channelName"],tag="热门股票".decode("utf8"))
#         r.hset("bmk:stockmark:" + getHashid(rc["channelId"]),"crt_tms",time.time())
        r.zadd("bmk:doc:share",time.time(),"stockmark|-|"+getHashid(rc["channelId"]))
        
    urlstr = "http://%s/research/svc?hotconcept=%s" % (getsysparm("BACKEND_DOMAIN"), parms[0])    
    udata = loadFromUrl(urlstr) 
    udata.reverse()
    for rc in udata:#{"channelName":"000002(万科Ａ)","channelId":"*000002(万科Ａ)","eventCreateTime":-1,"docId":-1,"docCreateTime":-1,"size":0}
#         beaid = getHashid(doc["channelId"])        
        beaconname = rc["channelName"].replace("*","")
        addBeacon("doc", getHashid(rc["channelId"]), rc["channelName"], beaconname=beaconname, desc=rc["channelName"],tag="热门概念".decode("utf8"))
        r.zadd("bmk:doc:share",time.time(),"doc|-|"+getHashid(rc["channelId"]))

    
def relateChannelAndStock(parms=("829105579","print")):
    """ 根据groupid关联股票频道."""  
    if type(parms).__name__ == "str":
        parms = (parms,) 
    op=parms[-1]
    for groupid in parms[:-1]:
        gobj = r.hgetall("group:"+groupid)
        if gobj is None or gobj=={}:
            print "group is not exsist !"  
            continue
        gobj["groupid"]=groupid
        for bstr in r.zrevrange("bmk:doc:share",0,-1):
            bkey = "bmk:"+bstr.replace("|-|",":")
            (beaconusr,beaconid) = bstr.split("|-|")
            ttl = r.hget(bkey,"ttl") 
            tag = r.hget(bkey,"tag") 
            name = r.hget(bkey,"name")
#             tag = tag.strip()
            if re.search(gobj["name"],tag):
                print "bmk:%s -->%s(%s)" % (bstr.replace("|-|",":"),ttl,tag)
                
    
def cleanChannelByTag(parms=("11111","print")):
    """ 根据groupid清理频道."""  
    if type(parms).__name__ == "str":
        parms = (parms,) 
    op=parms[-1]
    for groupid in parms[:-1]:
        gobj = r.hgetall("group:"+groupid)
        if gobj is None or gobj=={}:
            print "group is not exsist !"  
            continue
        gobj["groupid"]=groupid
        for bstr in r.zrevrange("bmk:doc:share",0,-1):
            bkey = "bmk:"+bstr.replace("|-|",":")
            (beaconusr,beaconid) = bstr.split("|-|")
            ttl = r.hget(bkey,"ttl") 
            tag = r.hget(bkey,"tag") 
            name = r.hget(bkey,"name")
#             tag = tag.strip()
            if re.search(gobj["name"],tag):
                print "bmk:%s -->%s(%s)" % (bstr.replace("|-|",":"),ttl,tag) 
                if op=="delete" :
                    deleteBeacon(beaconusr,beaconid)
                    if ttl is not None : rdoc.delete("doc:"+ttl)
                        
def cleanDocChannelByTime(parms=("now","print","notwithtag")): 
    if type(parms).__name__ == "str":
        parms = (parms,) 
    parm1=parms[0]
    op = parms[1]
    withtag = parms[2]=="withtag"
    if parm1=="now":
        tms = time.time()*1000
    elif len(parm1)==10:
        tms = float(parm1)*1000
    elif len(parm1)==13:
        tms = float(parm1)
    else:
        tms = (time.time()-int(parm1)*86400)*1000
    if op in ("delete","print"):
        bstrs = r.zrangebyscore("bmk:doc:share",0,tms)
    elif op in ("deleteafter","printafter"):#几天前向后删除
        bstrs = r.zrangebyscore("bmk:doc:share",tms,time.time()*1000)
        
    for bstr in bstrs:
        (beaconusr,beaconid) = bstr.split("|-|")
        key = "bmk:"+beaconusr+":"+beaconid 
        ttl = r.hget(key,"ttl")
        tag= r.hget(key,"tag")
        tag = "" if tag is None else tag
        if beaconusr =="doc":
            if tag!="" and not withtag:
                print "[skipped] bmk:%s -->%s(%s)" % (bstr.replace("|-|",":"),ttl,tag)
            else:
                if op =="delete" or op == "deleteafter":
                    print "bmk:%s -->%s(%s) deleted..." % (bstr.replace("|-|",":"),ttl,tag)
                    deleteBeacon(beaconusr,beaconid)
                else:
                    print "bmk:%s -->%s(%s)" % (bstr.replace("|-|",":"),ttl,tag)
#                 cleanChannelByCode((bstr.replace("|-|",":"),op))
                
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
###########deleteBeacon is over######################
    
def cleanStockChannel(parms=("print")):
    if type(parms).__name__ == "str":
        parms = (parms,) 
    op=parms[-1]
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        key = "bmk:%s:%s" % (beaconusr,beaconid)
        ttl = r.hget(key,"ttl")#*万科A(000002)
        if ttl is None:
            print "%s --->ttl is none" % (key)  
            continue
        if len(ttl.split("(")) !=2 :
            continue
        ttl = ttl.split("(")[0][1:]  
        if ttl.isdigit():
            print "%s ---> %s" % (key,ttl)  
            if op=="delete" :
                deleteBeacon(beaconusr,beaconid)
#                 if ttl is not None : rdoc.delete("doc:"+ttl)  
                    
def cleanDocChannel(parms=("doc","print")):
    """ 清理由热点新闻所建立频道,并将其从用户的关注列表中清理掉.""" 
    
    if type(parms).__name__ == "str":
        parms = (parms,) 
    op=parms[-1]
    for usr in parms[:-1]:
        if usr=="" : usr="doc"  
        for bstr in r.zrevrange("bmk:doc:share",0,-1):
            bkey = "bmk:"+bstr.replace("|-|",":")
            (beaconusr,beaconid) = bstr.split("|-|")
            ttl = r.hget(bkey,"ttl") 
            tag = r.hget(bkey,"tag") 
            name = r.hget(bkey,"name")
    #         if ttl is None or (ttl.isdigit() and len(ttl) > 6 
            if beaconusr== usr:
                if tag !="" and usr =="doc" : 
                    print "%s ---> %s --> %s jumped.." % (bkey,ttl, tag)
                    continue
                print "%s ---> %s" % (bkey,ttl)
                if op=="delete" :
                    deleteBeacon(beaconusr,beaconid)
                    if ttl is not None : rdoc.delete("doc:"+ttl) 
            
def replaceStormarketTitle(op="print"):        
    import re   
    for bstr in r.zrevrange("bmk:doc:share",0,-1):
        bkey = "bmk:"+bstr.replace("|-|",":")
#         ttl = r.hget(bkey,"ttl") 
        name = r.hget(bkey,"name") 
        if bstr.split("|-|")[0] == "stockmarket":
            ttl = re.sub("\(|\d|\)","",name)
            print "%s => %s ---> %s" % (bkey,name,ttl)
            if op=="replace" :
                r.hset(bkey,"ttl",ttl) 
    
def cleanCopynum(parms):
    """清理copynum里面的过时的docid的数据"""
    pass
    
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
    ###########deleteBeacon is over######################
    
       
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
                    
def beaconNameHash(op="print"):
    print "==beaconNameHash=="
    for bstr in r.zrevrange("bmk:doc:share",0,-1):
#         print "proc %s" % bstr
        bkey = "bmk:"+bstr.replace("|-|",":")
        ttl = r.hget(bkey,"ttl")
        if ttl is None:
            print "%s is null,should remove!" % (bkey)
        else:
            r.hset("beacon:channel:bak",ttl,bkey)
    r.rename("beacon:channel:bak","beacon:channel")

def saveFullText(ids):
    """保存单个或者多个id到后台(mongodb或其他)"""
    saveFulltextById(ids)

def stockChannelHash():
    """建立一个根据股票代码到频道key的hash"""
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        key = "bmk:%s:%s" % (beaconusr,beaconid)
#         name = r.hget(key,"ttl")#*万科A(000002)
#         name = name.split("(")[1][:-1]
        name = r.hget(key,"ttl")#*000002(万科Ａ)
        name = name.split("(")[0][1:]
        if name.isdigit():
            print "proc %s:%s <----%s" %(beaconusr,beaconid,name)
            r.hset("stock:channel",name,"%s:%s" % (beaconusr,beaconid))
            
def getHash(name):
    print getHashid(name) 
#     return getHashid(name)

def conceptChannelHash(op="show"):
    """建立一个根据概念股票代码到频道key的hash"""
    import CfgGrp
    cplist = CfgGrp.CPGroup.items()
    cpstocklst = []
    cpsstk = {}
    for cpcode,cpname in cplist:
        print "proc ",cpcode,cpname.decode("utf8")
        print "stockmarket:"+getHashid(cpname.decode("utf8"))
        r.hset("stock:channel",cpcode[2:],"%s:%s" % ("stockmarket",getHashid(cpname.decode("utf8"))))
#         r.hdel("stock:channel",cpcode)
        if op == "frombackend":
            urlstr = "http://svc.zhijixing.com/research/svc?channelid=%s&page=0&length=20" % cpname.decode("utf8")
            udata = loadFromUrl(urlstr)
            if udata.has_key("channels"):
                channels = udata["channels"]
                channels = [channel for channel in channels if channel.isdigit()]
                cpstk = " \"%s\":\"%s\" " % (cpcode,",".join(channels))
                print cpstk
                cpstocklst.append(cpstk)
            else:
                udata = loadFromUrl(urlstr)
                channels = udata["channels"]
                channels = [channel for channel in channels if channel.isdigit()]
                cpstk = " \"%s\":\"%s\" " % (cpcode,",".join(channels))
                print cpstk
                cpstocklst.append(cpstk)
        elif op=="fromredis":
            bmkkey = "bmk:%s:%s" % ("stockmarket",getHashid(cpname.decode("utf8")) ) 
            if not r.exists(bmkkey):
                continue
            channels = r.hget(bmkkey,"channels").split(",")
            
            def addhead(channel):
                if int(channel) > 599999:
                    return "sh"+channel
                else:
                    return "sz"+channel 
                
            channels = [addhead(channel) for channel in channels if channel.isdigit()]
            cpstk = """ "%s":'''%s''', """ % (cpcode,",".join(channels))
            print cpstk
            cpstocklst.append(",".join(channels))
#             print cpstocklst
            
    cpstocklst = sorted(cpstocklst)
    print """ "%s":'''%s''', """ % ("cp990999",",".join(cpstocklst))

def initBeaconDisplayName():
    """初始化频道的 显示名称 为频道名称"""
    for beaconstr in r.zrevrange("bmk:doc:share",0,-1):
        beaconusr,beaconid = beaconstr.split("|-|")
        print "proc %s:%s " %(beaconusr,beaconid)
        key = "bmk:%s:%s" % (beaconusr,beaconid)
        r.hset(key,"name",r.hget(key,"ttl"))

def exportkey(pattan="*"):
    """按照redis的key的模糊匹配规则 导出相应的数据 为command (暂时只支持zset与hash 两种类型数据)"""
#     print pattan
    import redis
    r = redis.StrictRedis()
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
        
def deleteUser(username=""):
    if username=="":
        return "username is null!"
    urlstr = "http://%s/userdelete/?username=%s" %(getsysparm("DOMAIN"),username)
    procUrl(["wxi","wxi",urlstr])
        
def procUrl(parms=[]):
    """ 先登录,然后再执行webservice"""
    import cookielib, urllib, urllib2 
    (usr,pwd,url2) = parms
    
    loginstr = "http://%s/apply/slogin/?usr=%s&pwd=%s" %(getsysparm("DOMAIN"),usr,pwd)
    print "loginstr is:"+loginstr
    req1 = urllib2.Request(loginstr)
    response = urllib2.urlopen(req1)
    cookie = response.headers.get('Set-Cookie')
    
    # Use the cookie is subsequent requests
#     url2='http://localhost:8000/news/sfllowbeacon/?u=wang9529&fllwopt=add&beaconid=1108470809&beaconusr=rd'
    print "proc url:"+url2
    req2 = urllib2.Request(url2)
    req2.add_header('cookie', cookie)
    response = urllib2.urlopen(req2)
    print response.readlines()
    
def loginAndDo(parms=[]):
    (usr,pwd) = parms
    import cookielib, urllib, urllib2
    login = 'wxi'
    password = 'wxi'
    # Enable cookie support for urllib2
    cookiejar = cookielib.CookieJar()
    urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
     
    # Send login/password to the site and get the session cookie
    values = {'usr':login, 'pwd':password }
    data = urllib.urlencode(values)
#     request = urllib2.Request("http://localhost:8000/apply/login/", data)
    loginstr = "http://%s/apply/slogin/?usr=%s&pwd=%s" %(getsysparm("DOMAIN"),usr,pwd)
    request = urllib2.Request(loginstr)
    
    url = urlOpener.open(request)  # Our cookiejar automatically receives the cookies
    page = url.read(500000)
    print page
    for cookie in cookiejar:
        print type(cookie),cookie.name 
     
    # Make sure we are logged in by checking the presence of the cookie "id".
    # (which is the cookie containing the session identifier.)
    if not 'sessionid' in [cookie.name for cookie in cookiejar]:
        raise ValueError, "Login failed with login=%s, password=%s" % (login,password)
     
    print "We are logged in !" 
    # Make another request with our session cookie
    # (Our urlOpener automatically uses cookies from our cookiejar)
    url = urlOpener.open('http://localhost:8000/news/sfllowbeacon/?u=wang9529&fllwopt=add&beaconid=1108470809&beaconusr=rd')
    page = url.read(200000)
    print page
    
def getTime(parms):
    """ return the converted date & time 'yyyy-mm-dd hh:mm:ss' by input tms """
    addtimezone=False
    formatstr="%Y-%m-%d %H:%M:%S"
    if type(parms).__name__ == "str":
        parms = (parms,) 
    
    for tms in parms:
        if type(tms).__name__ == "str":
            if tms=="":
                tms="0"
#             tms=float(tms)
#             if tms/pow(10,10)>0: 
            if len(tms) >10:
                power = pow(10,len(tms)-10)
                tms=float(tms)
                tms = tms/power
            else:
                tms=float(tms)
                
        try:
            if addtimezone:
                tms=tms+3600*8
            tdate = dt.datetime.fromtimestamp(tms).strftime(formatstr)
        except:
            print "Attembrough: i use getDate(%s,formatstr=%s) but it's report error..." % (tms,formatstr)
            traceback.print_exc()
            print "" 
        else:
            print tdate

def getUnixTime(tstr):
    """return unix timestamp input mustbe yyyymmdd"""
    rt = 0
    formatstr='%Y%m%d'
    try:
       rt = time.mktime(dt.datetime.strptime(tstr, formatstr).timetuple())
    except:
        print "Attembrough: i use getUnixTimestamp(%s) but it's report error..." % (tstr) 
        traceback.print_exc()
        print 0
    else:
        print rt 
        
def mongoproc(parms):
    if type(parms).__name__ == "str":
        parms = (parms,) 
    fulldocs = tftxs.find({"title":"/"+"借壳".decode("utf8")+"/"},{"_id":1,"title":1}).limit(10)
#     print "借壳".decode("utf8")
#     fulldocs = tftxs.find({},{"_id":1,"title":1}).limit(30)
    for doc in fulldocs:
        print doc
    
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
                  python %prog deleteUser {user} 
                  python %prog saveFullText {docids} 
                  python %prog getTime 
                  python %prog getUnixTime 
                  python %prog updateChannelAndStock 24 
                  python %prog relateChannelAndStock 829105579 
                  python %prog cleanDocChannelByTime {7|now} {print|delete|printafter|deleteafter} {notwithtag|withtag}
                  python %prog cleanDocChannel doc {print|delete}
                  python %prog cleanChannelByTag 111111 {print|delete}
                  python %prog cleanStockChannel {print|delete}
                  python %prog cleanChannelByCode doc:1257408 {print|delete}
                  python %prog replaceStormarketTitle  {print|replace} 
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
        logger.exception("msg")
        print( usage.replace("%prog", sys.argv[0]))
 
    

    
    

