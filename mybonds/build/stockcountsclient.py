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
    socket.connect('tcp://localhost:39527')
#     socket.connect ('tcp://121.199.37.23:30000')
      
#     #  Do 10 requests, waiting each time for a response  
#     for request in range (1,10):  
    print "Sending request ","..."  
    print "============getNewsCnts================"
    
    socket.send ("getNewsCnts stock schema cp990001 -28 -7 140000") 
    message = socket.recv()
    print message 
    socket.send ("getNewsCnts stock data cp990001  -28 -7 140000")  
    message = socket.recv()
    print message
    
    print "===========getNewsCoypNums================="
    
    socket.send ("getNewsCoypNums stock schema cp990001 -28 -7 140000")   
    message = socket.recv()
    print message 
    socket.send ("getNewsCoypNums stock data cp990001  -28 -7 140000")  
    message = socket.recv()
    print message
#     
    print "============getNewsCntsFromDate================"
    
    socket.send ("getNewsCntsFromDate stock schema cp990001 20130702 -20 140000")   
    message = socket.recv()
    print message
    socket.send ("getNewsCntsFromDate stock data cp990001  20130702 -20 140000")  
    message = socket.recv()
    print message
    
    print "===========getNewsCoypNumsFromDate================="
    
    socket.send ("getNewsCoypNumsFromDate stock schema cp990001 20130702 -20 140000")
    message = socket.recv()
    print message
    socket.send ("getNewsCoypNumsFromDate stock data cp990001  20130702 -20 140000")  
    message = socket.recv()
    print message
    
#     
#     socket.send ("getChannelNewsCountsList stock sh600001  7  ")   
#     message = socket.recv()
#     print message 
#     print "Received reply ", "[", message, "]"  
    
    
    
      