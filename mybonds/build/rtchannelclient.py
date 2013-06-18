#!/usr/bin/python

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
    socket.send ("getChannelNewsCountsList stock schema sh600000 -7 -1 ")   
    message = socket.recv()
    print message
     
    socket.send ("getChannelNewsCountsList stock data sh600000  -7 -1  ")  
    message = socket.recv()
    print message
#     
#     socket.send ("getChannelNewsCountsList stock sh600001  7  ")   
#     message = socket.recv()
#     print message 
#     print "Received reply ", "[", message, "]"  
    
    
    
      