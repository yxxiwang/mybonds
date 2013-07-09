#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os,string,sys,time,re
import redis
import zmq
import RTCfg
# import fcntl

def querySinaFrequence():
  return RTCfg.timeWindow['sinaIntervalTime']


class functionMapping:
  def __init__(self):
    self.controllers = {
      'querySinaFrequence': querySinaFrequence, 
      #'/logout/':logout,
    }

if __name__ == '__main__':

    context = zmq.Context()  
      
    #  Socket to talk to server  
    print "Connecting to hello world server..."  
    socket = context.socket(zmq.REQ)  
#     print RTCfg.zmqPort['systemParameterServicePort']
#     socket.connect (RTCfg.zmqPort['systemParameterClientPort'])  
#     socket.connect ('tcp://localhost:30000')
    socket.connect ('tcp://121.199.37.23:30000')
      
#     #  Do 10 requests, waiting each time for a response  
#     for request in range (1,10):  
    print "Sending request ","..."  
#     print "============getChannelNewsCountsList================"
#     socket.send ("getChannelNewsCountsList stock schema cp990001 -60 -1 ")   
#     message = socket.recv()
#     print message
#     socket.send ("getChannelNewsCountsList stock data cp990001  -60 -1  ")  
#     message = socket.recv()
#     print message
    
    print "============getNewsCnts================"
    
    socket.send ("getNewsCnts stock schema sh600792 -120 0 140000")   
    message = socket.recv()
    print message 
    socket.send ("getNewsCnts stock data sh600792  -120 0 140000")  
    message = socket.recv()
    print message
    
    print "===========getNewsCoypNums================="
    
    socket.send ("getNewsCoypNums stock schema cp990001 -60 -1 140000")   
    message = socket.recv()
    print message 
    socket.send ("getNewsCoypNums stock data cp990001  -60 -1 140000")  
    message = socket.recv()
    print message
    
#     print "===========getNewsCntsFromDate================="
#     
#     socket.send ("getNewsCntsFromDate stock schema cp990001 20130420 30 140000")   
#     message = socket.recv()
#     print message 
#     socket.send ("getNewsCntsFromDate stock data cp990001  20130420 30 140000")  
#     message = socket.recv()
#     print message
    
    print "===============getChannelNewsCopynumListByTime============="
     
    socket.send ("getChannelNewsCopynumListByTime stock schema sh600016 -7 -1 ")   
    message = socket.recv()
    print message 
    socket.send ("getChannelNewsCopynumListByTime stock data sh600016  -7 -1  ")  
    message = socket.recv()
    print message
    
    print "===============getCPinfo============="
     
    socket.send ("getCPinfo schema 829105579")   
    message = socket.recv()
    print message 
    socket.send ("getCPinfo data 829105579")  
    message = socket.recv()
    print message
    print "============================"
#     
#     socket.send ("getChannelNewsCountsList stock sh600001  7  ")   
#     message = socket.recv()
#     print message 
#     print "Received reply ", "[", message, "]"  
    
    
    
      