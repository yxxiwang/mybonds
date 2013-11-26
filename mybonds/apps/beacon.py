#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json  
import sys
import time
import os
import redis
import traceback 
import datetime as dt
from datetime import timedelta
from mybonds.apps.newspubfunc import *
from pip.download import geturl

class Beacon:
    beaconid = ""
    beaconusr = ""
    beaconname = ""
    key = ""
    usecache = "1"
    username=""
    days = 1
    bobj = {}
    def __init__(self, beaconusr, beaconid):
        self.beaconid = beaconid
        self.beaconusr = beaconusr
        self.key = "bmk:%s:%s" % (beaconusr, beaconid)
#     self.controllers = {
#       'querySinaFrequence': querySinaFrequence, 
#     }
    def beaconUrl(self,channelparm="channelpick",daybefore=1):
        """
                            根据频道所属用户及频道id生成从后台取频道的请求地址
        """
        key = self.key
        beaconusr = self.beaconusr
        beaconid = self.beaconid
        
        channel = self.getchannelforurl() 
        mindoc = self.getmindoc() 
        
#         if beaconusr=="rd":
#             channelparm = "%s=%s" % ("hottopicid",channel)
            
        if channelparm == "extendid":
            channelparm= "%s=%s:%s" % (channelparm,channel,self.getdesc())
        else:
            channelparm = "%s=%s" % (channelparm,channel)
        today = dt.date.fromtimestamp(time.time()) 
        if daybefore == -1:
            after = 0
        else:
            after = int((time.time() - daybefore * 86400) * 1000)
            
        before = int(time.time() * 1000)
        if int(mindoc) <= 0 :
            urlstr = "http://%s/research/svc?%s&after=%d&before=%d" % (getsysparm("BACKEND_DOMAIN"), channelparm, after, before)
        else:
            urlstr = "http://%s/research/svc?%s&after=%d&before=%d&mindoc=%s" % (getsysparm("BACKEND_DOMAIN"), channelparm, after, before, mindoc)
        return urlstr
    
    def getRelatedChannelUrl(self):
        return self.beaconUrl("relatedchannelid",self.days)
    
    def getChannelpickUrl(self):
        return self.beaconUrl("channelpick",self.days)
    
    def getEleventpickUrl(self):
        return self.beaconUrl("channeleventpick",self.days)
    
    def getPopularyUrl(self):
        return self.beaconUrl("popularid",self.days)
    
    def getExtendUrl(self):
        return self.beaconUrl("extendid",self.days)

    def getchannel(self):
        channel = r.hget(self.key, "ttl")
        channel = "" if channel is None else channel
        channel = channel.decode("utf8")
        return channel
    
    def getchannelforurl(self):
        channel = r.hget(self.key, "ttl")
        channel = "" if channel is None else channel
        channel = urllib2.quote(channel)
        return channel
    
    def getmindoc(self):
        mindoc = r.hget(self.key, "mindoc")
        mindoc = 0 if mindoc is None else mindoc
        return mindoc
    
    def getdesc(self):
        desc = r.hget(self.key, "desc")
        desc = "" if desc is None else desc
        desc = desc.decode("utf8")
        return desc
    
    def getBeaconName(self):
        beaconname = r.hget(self.key, "name")
        beaconname = "" if beaconname is None else beaconname
        beaconname = beaconname.decode("utf8")
        return beaconname
    
#     def getBeaconTime(self):
#         beacontime = r.hget(self.key, "crt_tms")
#         beacontime = time.time() if beacontime is None else beacontime
#         beacontime = getTime(beacontime, formatstr="%YYear%mMouth%dDay".decode("utf8"), addtimezone=False) 
#         beacontime=beacontime.replace("Year","年".decode("utf8")).replace("Mouth","月".decode("utf8")).replace("Day","日".decode("utf8"))
#         return beacontime
    
    def getobject(self):
        return r.hgetall(self.key)
    
    def setUsecache(self,usecache):
        self.usecache = usecache
        
    def setUsername(self,username):
        self.username = username
        
    def setDays(self,days):
        self.days = days
        
    def refresh(self):
        key = self.key
        beaconusr = self.beaconusr
        beaconid = self.beaconid 
        dt = timeDiff(r.hget(key, "last_touch"), time.time())
        updt = timeDiff(r.hget(key, "last_update"), time.time())
        dt = dt if dt < updt else updt   
        
        if type == "newbeaconadd":  # newbeaconadd
            pushQueue("channelpick", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"7"})
            pushQueue("channelpick", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"1"})
            return
        
        if not r.hexists(key, "last_touch"):  # 如果不存在上次更新时间,视为未更新过
            logger.warn(key + "'s 'last_touch' is not exists,retrivedocs from backend...")
            if r.exists(key):  
                pushQueue("beacon", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"7"})
                pushQueue("beacon", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"1"})
            else:  # 如果没有那么巧,后台队列准备刷新该灯塔时,前台已经删除该灯塔
                logger.warn(key + " maybe deleted via front  so we ignore it...")
                
        elif not r.exists("bmk:" + beaconusr + ":" + beaconid + ":doc:tms"):  # 如果频道文章列表不存在,重新刷新数据 
            pushQueue("beacon", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"7"})
            pushQueue("beacon", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"1"})

        elif dt > getsysparm("KEY_UPTIME"):  # 如果上次更新时间过久,则重新刷新数据
            logger.warn("data is old,pushQueue(retirveSimilar)..%s,%s,%d" % (beaconusr, beaconid, dt))
            r.hset(key, "last_touch", time.time())  # 更新本操作时间  
            
            if beaconusr != "rd":
                pushQueue("beacon", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"7"})
            pushQueue("beacon", {"beaconusr":beaconusr, "beaconid":beaconid, "days":"1"})
        else:
            logger.warn("Attembrough: oh,refreshBeacon....but i have nothing to do .. bcz time is %d ,uptms=%d" % (dt, getsysparm("KEY_UPTIME")))
            
    def add(self, beaconttl, beaconname="", desc="", beacontime="", mindoc="", tag="", headlineonly="0"):
        key = self.key
        beaconusr = self.beaconusr
        beaconid = self.beaconid 
        if r.hexists(key, "ttl"):
            logger.info("--Beacon is exists." + beaconttl)
            self.refresh()
            return
        else:
            logger.info("--addBeacon--" + beaconttl)
            
        beaconname = beaconttl if beaconname == "" else beaconname
        beacontime = getTime(time.time(), formatstr="%Y%m%d%H%M%S") if beacontime == "" else beacontime
        mindoc = "0" if mindoc == "" else mindoc 
        
        r.hset(key, "id", beaconid)
        r.hset(key, "ttl", beaconttl)
        r.hset(key, "name", beaconname)
        r.hset(key, "desc", desc)
        r.hset(key, "crt_usr", beaconusr)
        r.hset(key, "crt_tms", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S"))) 
        r.hset(key, "last_touch", 0) 
        r.hset(key, "last_update", 0) 
        r.hset(key, "cnt", 0) 
        r.hset(key, "mindoc", mindoc) 
        r.hset(key, "tag", tag) 
        r.hset(key, "headlineonly", headlineonly) 
        
        r.zadd("usr:" + beaconusr + ":fllw", time.time(), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share", long(getUnixTimestamp(beacontime, "%Y%m%d%H%M%S")), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share:byfllw", time.time(), beaconusr + "|-|" + beaconid)
        r.zadd("bmk:doc:share:bynews", time.time() , beaconusr + "|-|" + beaconid)
        
        self.refresh()
        
    def getExtendlist(self):    
        udata = textend.find_one({"_id":self.beaconid})
        if udata is None or self.usecache=="0" :
            udata = self.saveExtendData()
        return udata
    
    def saveExtendData(self): 
        udata = self.getdoc(self.beaconid, self.getExtendUrl(), textend)
        if not r.exists(self.key):
            self.add(beaconttl, beaconname, desc, beacontime, mindoc, tag, headlineonly)
        return udata
        
    def getRelatedchannellist(self):
        udata = trelate.find_one({"_id":self.beaconid})
        if udata is None or self.usecache=="0" :
            udata = self.saveRelatedchannelData() 
        bea_lst=[]
        for bea in udata["beacons"]: 
            beacon={}
            beacon["beaconid"]=getHashid(bea["channelId"])
            beacon["beaconusr"]="doc"
#             print to_unicode_or_bust(bea["channelName"])
            beaconname = bea["channelName"].replace("*","")
            addBeacon("doc", beacon["beaconid"], bea["channelName"], beaconname=beaconname, desc=beaconname) 
            beacon["beacontime"]=getBeaconTime("doc",beacon["beaconid"])
            beacon["beaconname"]=to_unicode_or_bust(beaconname)
            bea_lst.append(beacon)
        udata["beacons"]=bea_lst
        udata["total"]=len(bea_lst)
        udata["success"]="true"
        udata["message"]="getRelatedchannellist"
        return udata
    
    def saveRelatedchannelData(self):
        url = self.getRelatedChannelUrl()
        logger.info("fetch url:" + url)
        udata={}
        beaconlist = bench(loadFromUrl, parms=url)
        if beaconlist is not None or beaconlist !={}:
            udata["_id"] = int(self.beaconid)
            udata["beacons"] =beaconlist
            trelate.save(udata)
            logger.info("save doc into mongdb :" + self.beaconid)
        else:
            return {}
#         udata = self.getdoc(self.beaconid, self.getRelatedChannelUrl(), trelate)
        return udata
        
    def getPopularylist(self):    
#         udata = tpopulary.find_one({"_id":self.beaconid})
#         if udata is None or self.usecache=="0" :
#             udata = self.savePopularyData()
#         return udata
        beaconusr = self.beaconusr
        beaconid = self.beaconid
        username = self.username
        usecache = self.usecache
        
        udata = newHotBoardData(beaconusr, beaconid,username=username,usecache=usecache)
        return udata

    def savePopularyData(self):
        udata = self.getdoc(self.beaconid, self.getPopularyUrl(), tpopulary)
        return udata
        
    def getLastDoc(self):
        key = self.key
        username=self.username
        beaconusr = self.beaconusr
        beaconid = self.beaconid 
        doc_lst = r.zrevrange(key + ":doc:tms", 0, 3)
        doc = {}
#         userfllws = r.zrevrange("usr:" + username+":fllw",0,-1)
#         todaytms=time.mktime(dt.date.today().timetuple())
        for docid in doc_lst:
            doc = rdoc.hgetall("doc:" + docid)
            if len(doc.keys()) == 0:
                continue 
#             doc["text"] = ""
#             doc["host"] = ""
#             doc["domain"] = ""
#             doc["url"] = ""
            doc["domain"]=doc["domain"].decode("utf8")
            doc["title"]=doc["title"].decode("utf8")
            doc["copyNum"] = str(doc["copyNum"])
            doc["tms"]=str(doc["create_time"])
            doc["create_time"] = timeElaspe(doc["create_time"])
             
            if r.zscore("usr:" + username + ":fllw", beaconusr+"|-|"+beaconid) is not None:  # 频道已经被该用户关注
                doc["isfllw"] = "true" 
            else:
                doc["isfllw"] = "false" 
            doc["beaconusr"] = beaconusr
            doc["beaconid"] = beaconid 
            doc["beaconname"] = self.getBeaconName()
            doc["beacontime"] = getBeaconTime(beaconusr,beaconid)
            doc["beacontodaycnt"] = getBeaconTodayCnt(beaconusr,beaconid)
            break
        return doc
        
    def getChannelpicklist(self):
        if self.beaconusr == "rd":
            udata = tchannelpick.find_one({"_id":self.beaconid})
            if udata is None  or self.usecache=="0" :
                udata = self.saveChannelpickData()
        else:
            udata = buildBeaconData(self.beaconusr, self.beaconid, start=0, end=100, isapi=True,orderby="utms") 
        return udata
    
    def saveChannelpickData(self):
        if self.beaconusr == "rd": 
            udata = self.getdoc(self.beaconid,self.getChannelpickUrl(),tchannelpick)
            return udata
        
        udata = saveDocsByUrl(self.getChannelpickUrl(),headlineonly="0")
        if udata is None or udata=={} or not udata.has_key("docs"):
            return udata
        
        key = self.key
        beaconusr = self.beaconusr
        for doc in udata["docs"]:
            if doc is None:
                continue
            if beaconusr=="doc":
                r.zadd(key+":doc:tms",int(doc["create_time"]),str(doc["docId"]))  
            else:
                r.zadd(key+":doc:tms:bak",int(doc["create_time"]),str(doc["docId"]))
            
            if beaconusr=="rd":
                r.zadd(key+":doc:utms:bak",utms,str(doc["docId"])) 
                rdoc.hset("doc:"+str(doc["docId"]),"eventid",doc["eventId"])
                utms = utms +1
                
                eventid = str(doc["eventId"]) if doc.has_key("eventId") else "-1"
                if eventid !="-1" and not r.exists("bmk:doc:"+eventid) :
                    beaconname = doc.get("title",str(doc["docId"]))
                    self.add("doc",eventid,eventid,beaconname=beaconname,tag="auto",headlineonly="1")
                
        if r.exists(key+":doc:tms:bak"):#如果频道数据为空,那么将不会有 key+":doc:tms:bak" 存在,rename的方法会返回错误
            r.rename(key+":doc:tms:bak",key+":doc:tms")
            
        if r.exists(key+":doc:utms:bak"):#如果频道数据为空,那么将不会有 key+":doc:tms:bak" 存在,rename的方法会返回错误
            r.rename(key+":doc:utms:bak",key+":doc:utms")
            
        r.hset(key, "last_update", time.time())  # 更新本操作时间   
        return udata
     
    def getEventPicklist(self):   
        def proc(doc): 
#             doc["beaconid"]=doc["beaconid"]
#             doc["beaconusr"]="doc"
#             doc["beaconname"]=doc["title"]
#             doc["isbeacon"]="true"
            if not doc.has_key("utms"):
                doc["utms"] = doc["tms"]  
            doc["copyNum"] = str(doc["copyNum"])  
            if doc.has_key("eventid") : doc.pop("eventid")
            self.add(doc["beaconid"],beaconname=doc["beaconname"],tag="auto",headlineonly="1")
            return doc
            
        udata = self.getPopularylist()
#         udata = dataProcForApi(udata)
        if udata.has_key("docs"):
            udata["docs"] =  [ proc(doc) for doc in udata["docs"] ]
            
        pickdata = self.getChannelpicklist()
        pickdata = dataProcForApi(pickdata)
        
        if udata.has_key("docs") and pickdata.has_key("docs") :
            udata["docs"] = udata["docs"]+pickdata["docs"]
        return udata
    
    def getdoc(self,id, url, tmongo):
        logger.info("fetch url:" + url)
        udata = bench(loadFromUrl, parms=url) 
        if udata.has_key("docs"): 
            udata["_id"] = id
            tmongo.save(udata)
            logger.info("save doc into mongdb :" + id)
        else:
            return udata
        
        ########## 保存每个文档的全文 信息 ####################
        ids = [] 
        for doc in udata["docs"]: 
            if rdoc.hexists("doc:"+str(doc["docId"]),"url"): continue
            ids.append(str(doc["docId"]))
        if len(ids)>0:
            pushQueue("fulltext",{"urlstr":"","ids":";".join(ids)}) 
        return udata
    
    def exists(self):
        return r.exists(self.key)
    
    def __str__(self):
        return unicode(self).encode('utf-8')+"->"+self.key

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    
