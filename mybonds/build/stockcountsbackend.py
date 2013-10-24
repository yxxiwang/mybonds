#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os,string,sys,time,re
import redis,json
import zmq
# import RTCfg
import CfgGrp
import datetime as dt
import datetime
# import fcntl

r = redis.StrictRedis()
ccnt_data={}
ccopynum_data={}
cp_data ={}
cp_stock_data = {}

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def querySinaFrequence(parms=[]):
    return ""
#   return RTCfg.timeWindow['sinaIntervalTime']

def getNewsCnts(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    
    dayto = int(dayto)+1 
    dayto = None if dayto == 0 else dayto
    dayfrom = int(dayfrom)
    rdata=[]
#     print "dayfrom=%d,dayto=%d,code=%s" %(dayfrom,dayto,code)
#     print ",".join(ccnt_data[code])
    if schema =="schema" :
        rdata = ccnt_data["date"][dayfrom:dayto]
        return json.dumps(rdata)
    else:
        rdata = ccnt_data[code][dayfrom:dayto] if ccnt_data.has_key(code) else "has no key:"+code
        return json.dumps(rdata)
    
def getNewsCntsFromDate(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    
    (action,schema,code,dayfrom,daycnt,timedelta)=parms
    rdata = []
    
    if not check_int(dayfrom) or not check_int(daycnt) or not check_int(timedelta):
        print "day is not digit!"
        return json.dumps(rdata)
     
    if dayfrom in ccnt_data["date"]:
        dayfrom = ccnt_data["date"].index(dayfrom)
    else:
        dayfrom = 0
        
#     print "dayfrom=%d," %(dayfrom,)
        
    daycnt = int(daycnt)
    st =0
    ed = dayfrom 
    if daycnt < 0:
        st = daycnt+dayfrom
        st = 0 if st < 0 else st
        ed = ed+1
    else:
        st = dayfrom
        ed = dayfrom + daycnt +1
        
    print "st=%d,ed=%d,code=%s" %(st,ed,code)
    print ",".join(ccnt_data[code])
    print ",".join(ccnt_data["date"])
    if schema =="schema" :
        rdata = ccnt_data["date"][st:ed]
        return json.dumps(rdata)  
    else:
        rdata = ccnt_data[code][st:ed] if ccnt_data.has_key(code) else "has no key:"+code
        return json.dumps(rdata)  
    
def getNewsCoypNums(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    (action,schema,code,dayfrom,dayto,timedelta)=parms
    
    rdata=[]
    if not check_int(dayfrom) or not check_int(dayto) or not check_int(timedelta):
        print "day is not digit!"
        return json.dumps(rdata)
    
    dayto = int(dayto)+1 
    dayto = None if dayto == 0 else dayto
    dayfrom = int(dayfrom)
    
    if schema =="schema" :
        rdata =  ccopynum_data["date"][dayfrom:dayto]
        return json.dumps(rdata) 
    else: 
        rdata = ccopynum_data[code][dayfrom:dayto] if ccopynum_data.has_key(code) else "has no key:"+code
        return json.dumps(rdata) 

def getNewsCoypNumsFromDate(parms=[]):
    print parms
    if len(parms) < 5:
        print "parms is %d,less than 5!" %len(parms)
        return "len(parms) is not 5"
    (action,schema,code,dayfrom,daycnt,timedelta)=parms
    
    rdata=[]
    if not check_int(dayfrom) or not check_int(daycnt) or not check_int(timedelta):
        print "day is not digit!"
        return json.dumps(rdata)
    
#     daycnt = int(daycnt)+1 
#     daycnt = None if daycnt == 0 else daycnt
    if dayfrom in ccopynum_data["date"]:
        dayfrom = ccopynum_data["date"].index(dayfrom)
    else:
        dayfrom = 0
    
    daycnt = int(daycnt)
    st =0
    ed = dayfrom 
    if daycnt < 0:
        st = daycnt+dayfrom
        st = 0 if st < 0 else st
        ed = ed+1
    else:
        st = dayfrom
        ed = dayfrom + daycnt +1
         
#     print dayfrom,daycnt
    if schema =="schema" :
        rdata =  ccopynum_data["date"][st:ed]
        return json.dumps(rdata)
    else: 
        rdata = ccopynum_data[code][st:ed] if ccopynum_data.has_key(code) else "has no key:"+code
        return json.dumps(rdata) 
    
def getChannelStock(parms=[]):
    (cpcode,)=parms
    return json.dumps(cp_stock_data[cpcode])

def getCPinfo(parms=[]):
    (schema,)=parms 
    if schema == "schema":
        return json.dumps(cp_data["code"])
    else:
        return json.dumps(cp_data["name"])

def sendemail(parms=[]):
#     (email,title,contents)=parms 
    rcv_email = parms[0]
    title = parms[1]
    content = " ".join(parms[2:])
#     rcv_email = "yxxiwang@gmail.com"
#     content = "testtest"
#     title = "title"
    print "email is :" + rcv_email
    print "title is :" + title
    print "content is :" + content
    from django.core.mail import send_mail
    print( "================sendemail============================")
    import smtplib, mimetypes
    from smtplib import SMTPException
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.Header import Header
    from email.mime.image import MIMEImage
    sender = 'admin@zhijixing.com'
    if rcv_email == "":
        rcv_email = 'yxxiwang@gmail.com'
    receivers = [rcv_email]

    msg = MIMEMultipart()
    msg['From'] = "灯塔资讯".decode("utf8")
    #msg['From'] = "dengtazixun"
    msg['To'] = rcv_email
    if title!="":
        msg['Subject'] = Header(title, charset='UTF-8')  # 中文主题
    else:
        msg['Subject'] = Header('欢迎来到指极星', charset='UTF-8')  # 中文主题

    txt = MIMEText(content, _subtype='html', _charset='UTF-8')
    msg.attach(txt)
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com')       
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login('admin@zhijixing.com', 'software91')
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print( "Successfully sent email")
        return "0"
    except SMTPException:
       print( "Error: unable to send email")
       traceback.print_exc()
       return "-1"
    else:
       pass 
    finally:
       smtpObj.quit()
    return "-1"

def initData(parms=[]):
    context = zmq.Context()   
    socket = context.socket(zmq.REQ)  
    socket.connect ('tcp://121.199.37.23:30000')
#     socket.connect ('tcp://localhost:30000')
    print "============getNewsCnts================"
    
    socket.send ("getNewsCnts stock schema sh300088 -120 0 140000")   
    message = socket.recv()
    print "dates is:",message
    
    ccnt_data["date"]= json.loads(message)
    ccopynum_data["date"]= json.loads(message)
#     for i in xrange(1,5):
    stockliststr = CfgGrp.AGroup["1"]
    for stockcode in stockliststr.split(","):
        print "proc: ",stockcode
        
        socket.send ("getNewsCnts stock data "+stockcode+"  -120 0 140000")  
        message = socket.recv() 
        ccnt_data[stockcode]=json.loads(message)
        
        socket.send ("getNewsCoypNums stock data "+stockcode+"  -120 0 140000")  
        message = socket.recv() 
        ccopynum_data[stockcode]=json.loads(message)
    
    #===============================================#
    #==================装载 概念频道  数据==================#
    #===============================================#
    socket.send ("getCPinfo schema 829105579")   
    message = socket.recv()
    print message 
    cp_data["code"] = json.loads(message)
    
    cplist = json.loads(message)
    for cpcode in cplist:
        print "proc: ",cpcode 
        socket.send_unicode("getNewsCnts stock data "+cpcode+"  -120 0 140000")  
        message = socket.recv() 
        ccnt_data[cpcode]=json.loads(message)
        
        socket.send_unicode("getNewsCoypNums stock data "+cpcode+"  -120 0 140000")  
        message = socket.recv() 
        ccopynum_data[cpcode]=json.loads(message)
    
    
    socket.send ("getCPinfo data 829105579")   
    message = socket.recv()
    print message 
    cp_data["name"] = json.loads(message)
    
    for cpcode in cp_data["code"]:
#         print cpcode
        socket.send_unicode("getChannelStock "+cpcode)   
        message = socket.recv()
#         print message
        cp_stock_data[cpcode] = json.loads(message)
    print "initData is over......"
    
class functionMapping:
  def __init__(self):
    self.controllers = {
      'querySinaFrequence': querySinaFrequence,
      'getNewsCnts': getNewsCnts,
      'getNewsCoypNums': getNewsCoypNums,
      'getNewsCntsFromDate': getNewsCntsFromDate,
      'getNewsCoypNumsFromDate': getNewsCoypNumsFromDate,
      'getChannelStock': getChannelStock,
      'getCPinfo': getCPinfo,
      'sendemail': sendemail,
      #'/logout/':logout,
    }

if __name__ == '__main__':

    context = zmq.Context()
    funcMapping = functionMapping()
    
    socket = context.socket(zmq.REP) 
    socket.bind("tcp://*:39527")
    initData()
    
#     print getCPinfo(["schema"])
#     print getCPinfo(["data"])
#     print getChannelStock(["cp990001"])
#     exit(0)
    
    print "====getNewsCnts is okay====="
    while True:
      #  Wait for next request from client
      message = socket.recv()
      message = message.rstrip()
      ary = re.split('\s+',message)
    
      #  Send reply back to client
      retFunc = funcMapping.controllers.get(ary[0])
      if retFunc:
        socket.send(retFunc(ary[1:]))
      else:
        socket.send("no this function")
    #     time.sleep(5)
    
    