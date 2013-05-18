#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time
from daemon import Daemon
import json, urllib2
import traceback

from django.utils.encoding import smart_str

from sys import path
from os import getcwd
import os
path.append(getcwd())# current dir
if os.name =="nt":
	path.append(os.path.abspath('..\..\..'))# mybonds's parrent dir
	path.append("C:\Users\wangxi\git\mybonds")
else:#os.name=="posix"
	path.append(os.path.abspath('../../..'))# mybonds's parrent dir
	path.append("/root")
	
import __init__ as lib
from mybonds.apps import *

class DaemonProcess(Daemon):
	
	def run(self):
		while True:
# 			sys.stdout.write("=run====\n")
			# retrive
 			for qtype in ("sendemail","removedoc","beacon"):
 				for i in range(lib.r.llen("queue:" + qtype+":processing")):#先处理遗留的队列
 					qobj=lib.r.rpoplpush( "queue:" + qtype + ":processing","queue:" + qtype)
 					print "move qobj%s from queue:%s:processing to queue:%s" %(qobj,qtype,qtype)
 					
 			 	for i in range(lib.r.llen("queue:" + qtype)): 
 			 	 	self.retriveData(qtype) 
			time.sleep(1)
			
#remove from class DaemonProcess		
def retriveData(qtype):
	qobj = lib.r.rpoplpush("queue:" + qtype, "queue:" + qtype + ":processing")
	if qobj is None:
		return
	
	qinfo = {}
	tag = ""
	url=""
	rt = 6
# 		print "retriveData...qtype is :"+qtype
	start = time.clock()  
	try:
# 			if not qobj is None:
		# 	    	urlstr = qobj["url"] 
		sys.stdout.write("processing data:\n")
		sys.stdout.write(qobj)
		qinfo = json.loads(qobj) 
		username = qinfo["usr"]
		otype = qinfo["o"]
		url = qinfo["url"]
# 				if qtype == "tag":
# 					tag = qinfo["tag"]
# 					rt = lib.saveTagdoc(username, otype, tag,True) 
# 				elif qtype =="navtag": 
# 					navtag = qinfo["navtag"]
# 					rt = lib.saveTagdoc(username, otype, navtag,True) 
		if qtype =="read": 
				rt = lib.requestUrl(url)
		elif qtype =="beacon": 
			beacon = qinfo["beacon"]
			rt = lib.refreshDocs(username, beacon) 
		elif qtype =="fulltext": 
			ids = qinfo["fulltext"]
			udata = lib.saveFulltextById(url) 
			rt= WARNNING if udata=={} else SUCCESS
		elif qtype =="removedoc": 
#  					urlstr = qinfo["url"]
# 					docid = qinfo["docid"]
# 					key = "bmk:" + username + ":" + docid
# 					channel = lib.r.hget(key,"ttl")
# 					if os.name =="nt":
# 						channel = channel.decode("utf8")
# 					urlstr="http://www.gxdx168.com/research/svc?u="+urllib2.quote(channel) +"&o=2&likeid=-"+docid
			udata = lib.bench(loadFromUrl,parms=url)
			rt= WARNNING if udata=={} else SUCCESS
			
		elif qtype =="sendemail":
			if otype=="bybeacon":
				hourbefore = qinfo["email"]
				rt = lib.sendEmailFromUserBeacon(username,hourbefore,otype)
			elif otype=="lostkey":
				email = qinfo["email"]
				rt = lib.sendEmailFindKey(username,email,url)
			else:
				email = qinfo["email"]
				rt = lib.sendemailbydocid(email,qinfo["docid"],otype)
		else:
# 					rt = lib.saveDocs(username, otype)
			print "error qtype %s " % qtype
			rt = 0 
# 			else:
# 				sys.stdout.write("is nothing to do....\n") 
	except:
		traceback.print_exc()
#			traceback.print_exc(file=sys.stdout)
#			exc_type, exc_value, exc_traceback = sys.exc_info()
#			traceback.print_exception(exc_type, exc_value, exc_traceback,
#                              limit=2)
	if rt == SUCCESS: # SUCCESS=0
		qobj = lib.r.rpoplpush("queue:" + qtype + ":processing", "queue:" + qtype + ":done")
	elif rt == SYSERROR: # SYSERROR=-1
			qobj = lib.r.rpoplpush("queue:" + qtype + ":processing", "queue:" + qtype + ":error")
	else:# COMMUNICATERROR=6 ,WARNNING=8
# 			qobj = lib.r.rpoplpush("queue:" + qtype + ":processing", "queue:" + qtype)
		qobj = lib.r.rpop("queue:" + qtype + ":processing")
		qinfo = json.loads(qobj)
		cnt = qinfo["cnt"] if qinfo.has_key("cnt") else 0
		qinfo["cnt"]=cnt+1
		if qinfo["cnt"] < RETRYCOUNT:
			print "process it again"
			lib.r.lpush("queue:" + qtype,json.dumps(qinfo))
		else:
			print "it's rearch the maxsim count of RETRYCOUNT"
			lib.r.lpush("queue:" + qtype+":error",json.dumps(qinfo)) 
		
	urlstop = time.clock()
	diff = urlstop - start
# 	content = smart_str(content)  
	print "retriveData(%s) has taken on %s;and rt is %d" % (smart_str(url),str(diff),rt) 
	return rt
			
def runserver(type):
	print "-------is running----------"
	while True: 
		qtype = "retirveRCM" 
		if type != "all":
			for i in range(lib.r.llen("queue:" + type+":processing")):#先处理遗留的队列
				qobj=lib.r.rpoplpush( "queue:" + type + ":processing","queue:" + type)
				print "move qobj%s from queue:%s:processing to queue:%s" %(qobj,type,type)
			for i in range(lib.r.llen("queue:" + type)): 
		 	 	retriveData(type) 
		else:
			for qtype in ("sendemail","removedoc","beacon","fulltext"):
				for i in range(lib.r.llen("queue:" + qtype+":processing")):#先处理遗留的队列
					qobj=lib.r.rpoplpush( "queue:" + qtype + ":processing","queue:" + qtype)
					print "move qobj%s from queue:%s:processing to queue:%s" %(qobj,qtype,qtype)
					
			 	for i in range(lib.r.llen("queue:" + qtype)): 
			 	 	retriveData(qtype) 
		time.sleep(1)
		
def print_info(op,pid,stdout,stderr): 
	sys.stdout.write("=daemon "+op+"=\n")
	sys.stdout.write("=pid="+pid+"\n")
	sys.stdout.write("=stdout="+stdout+"\n")
	sys.stdout.write("=stderr="+stderr+"\n")
	sys.stdout.write("=stdin=/dev/null\n")

if __name__ == "__main__":
# 	daemon = DaemonProcess('/tmp/daemon-example.pid')
	stdout = '/root/mybonds/daemon.out'
	stderr = '/root/mybonds/daemon.error'
	pid = '/tmp/daemon.pid'
	type = "all"
#	daemon = DaemonProcess(pid, stdout=stdout, stderr=stderr)
	if len(sys.argv) > 4:
		pid =sys.argv[2]
		stdout =sys.argv[3]
		stderr =sys.argv[4]
		daemon = DaemonProcess(pid, stdout=stdout, stderr=stderr)
	else:
		daemon = DaemonProcess(pid, stdout=stdout, stderr=stderr)
	if len(sys.argv) >= 2:
		if 'start' == sys.argv[1]: 
			print_info("start",pid,stdout,stderr) 		
			daemon.start()
		elif 'stop' == sys.argv[1]:	 
			print_info("stop",pid,stdout,stderr) 
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			print_info("restart",pid,stdout,stderr)		
			daemon.restart()
		elif 'run' == sys.argv[1]:
			print_info("run",pid,stdout,stderr)	
			if len(sys.argv) >= 3:
				type =sys.argv[2]
			runserver(type)
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)
