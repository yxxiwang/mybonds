#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time
import json, urllib2
import redis
import codecs
import datetime as dt

#if __name__ == "__main__":
r = redis.StrictRedis()
rdoc = redis.StrictRedis(db=1)
logs = r.zrevrange("log",0,-1,withscores=True)
#f = open("log.csv","w")
infos = ""
tms=time.time()
tt = time.gmtime(tms+8*3600)
tdate = dt.date.fromtimestamp(tms+8*3600).strftime('%Y%m%d')
ttime = str(tt.tm_hour)+"-"+str(tt.tm_min)+"-"+str(tt.tm_sec) 

f = codecs.open( "log_"+tdate+"_"+ttime+".csv", "w")
f.write( codecs.BOM_UTF8 )
#f.write( unicodeString.encode( "utf-8" ) )
for log,tms in logs:
    logobj = json.loads(log)
    ip = logobj["ip"]
    user = logobj["usr"]
    act = logobj["act"]
    obj = logobj["o"]
    url = "http://www.ip.cn/getip.php?action=queryip&ip_url="+ip+"&from=web"
    #rr= requests.get(url)
    #r.hset("usrlst",logobj["usr"],rr.text)
    if ip == "110.75.186.225":
        continue
	if act=="reserch":
		id=obj
		obj = rdoc.hget("doc:"+id, "url")
		infos = rdoc.hget("doc:"+id, "ttl")
    else:
		infos = ""
	
    if isinstance(obj, unicode):
    	print obj
#    	obj = obj.decode("utf8")
#    r.hset("usrlst",user,ip)
#    r.hset("ips",ip,ip)
	tt = time.gmtime(tms)
	tdate = dt.date.fromtimestamp(tms).strftime('%Y%m%d')
	ttime = str(tt.tm_hour)+":"+str(tt.tm_min)+":"+str(tt.tm_sec)
    logstr='%s,%s,%s,%s,%s,"%s","%s"' %(tdate,ttime,user,ip,act,obj,infos.decode("utf8"))
    print logstr
#    f.write(logstr)
    f.write( logstr.encode( "utf-8" ) )
    f.write("\n")
f.close()
	 
	 