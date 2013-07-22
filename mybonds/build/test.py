#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random,argparse
import sys, time,logging,os,traceback
import redis,re,numpy
import datetime as dt
from numpy.ma.core import isMA
from sys import path
from os import getcwd
from numpy import bench
path.append(getcwd())# current dir
if os.name =="nt":
#     path.append(os.path.abspath('..\..\..'))# mybonds's parrent dir
    path.append("C:\Users\wangxi\git\mybonds")
else:#os.name=="posix"
#     path.append(os.path.abspath('../../..'))# mybonds's parrent dir
    path.append("/root")

    
def plotshow():
    import numpy as np
    import matplotlib.pyplot as plt
    
    r1 = 26.56 # GPS radius
    r2 = 6.371 # Earth radius
    
    theta = np.linspace(0, 360, 361) / 180. * np.pi # angles of plotting points
    
    # Polar coordinate to Cartesian coordinate
    x1 = r1*np.cos(theta)
    y1 = r1*np.sin(theta)
    
    x2 = r2*np.cos(theta)
    y2 = r2*np.sin(theta)
    
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.set_aspect("equal")
    
    plt.plot(x1, y1, color="red", label="GPS")
    plt.plot(x2, y2, color="blue", label="Earth")
    
    plt.title("Earth and GPS orbit, unit: 1000 km")
    
    plt.legend()
    
    plt.show()
    
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
            """
    if len(sys.argv) >= 2:
        func = sys.argv[1]  
        if len(sys.argv) >=3:
            parms = sys.argv[2:] 
            reflect(func,parms)
        else:
            reflect(func)
    else:
        logger.exception("msg")
        print( usage.replace("%prog", sys.argv[0]))


