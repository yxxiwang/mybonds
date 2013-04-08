#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time
from daemon import Daemon
import json, urllib2
import __init__ as lib
import traceback

class DaemonProcess(Daemon):
	
	def run(self):
		while True:
# 			sys.stdout.write("=run====\n")
			# retrive
 			for qtype in ("rcm", "ppl" , "nav" ,"beacon","tag","navtag", "rdd","read","sendemail"):
 			 	for i in range(lib.r.llen("queue:" + qtype)): 
 			 	 	self.retriveData(qtype) 
			time.sleep(1)
			
	def retriveData(self, qtype):
		qobj = lib.r.rpoplpush("queue:" + qtype, "queue:" + qtype + ":done")
		qinfo = {}
		tag = ""
		url=""
		rt = 6
# 		print "retriveData...qtype is :"+qtype
		start = time.clock()  
		try:
			if not qobj is None:
			# 	    	urlstr = qobj["url"] 
				sys.stdout.write("processing data:\n")
				sys.stdout.write(qobj)
				qinfo = json.loads(qobj) 
				username = qinfo["usr"]
				otype = qinfo["o"]
				url = qinfo["url"]
				if qtype == "tag":
					tag = qinfo["tag"]
					rt = lib.saveTagdoc(username, otype, tag,True) 
				elif qtype =="navtag": 
					navtag = qinfo["navtag"]
					rt = lib.saveTagdoc(username, otype, navtag,True) 
				elif qtype =="beacon": 
					beacon = qinfo["beacon"]
					rt = lib.saveBeacon(username, beacon) 
				elif qtype =="read": 
					rt = lib.requestUrl(url)
				elif qtype =="sendemail":
					if otype=="bybeacon":
						hourbefore = qinfo["sendemail"]
						rt = lib.sendEmailFromUserBeacon(username,hourbefore,otype)
					else:
						email = qinfo["sendemail"]
						rt = lib.sendemailbydocid(email,qinfo["docid"],otype)
				else:
					rt = lib.saveDocs(username, otype)
# 			else: 
# 				sys.stdout.write("is nothing to do....\n") 
		except:
			traceback.print_exc()
#			traceback.print_exc(file=sys.stdout)
#			exc_type, exc_value, exc_traceback = sys.exc_info()
#			traceback.print_exception(exc_type, exc_value, exc_traceback,
#                              limit=2)
		if not rt == 0:
			qobj = lib.r.rpoplpush("queue:" + qtype + ":done", "queue:" + qtype + ":error")
		urlstop = time.clock()  
		diff = urlstop - start  
		print "retriveData(%s) has taken on %s;and rt is %d" % (url,str(diff),rt) 
		return rt
			
def runserver(daemon):
	print "-------is running----------"
	while True: 
		qtype = "retirveRCM" 
		for qtype in ("rcm", "ppl" ,"nav","beacon","tag","navtag", "rdd","read","sendemail"):
		 	for i in range(lib.r.llen("queue:" + qtype)): 
		 	 	daemon.retriveData(qtype) 
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
#	daemon = DaemonProcess(pid, stdout=stdout, stderr=stderr)
	if len(sys.argv) > 2:
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
			runserver(daemon)
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)
