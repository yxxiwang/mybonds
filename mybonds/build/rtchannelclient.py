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
    socket.connect (RTCfg.zmqPort['systemParameterClientPort'])  
      
#     #  Do 10 requests, waiting each time for a response  
#     for request in range (1,10):  
    print "Sending request ","..."  
    socket.send ("getChannelNewsCountsList stock sh603000  7  ")  
      
    #  Get the reply.  
    message = socket.recv()
    print message
#     print "Received reply ", "[", message, "]"  
    
    
    
      