#!/usr/bin/python
# -*- coding: utf-8 -*- 
import math
import random
import redis
import numpy as np
import timeit
import mybonds.mybonds.apps

r=redis.StrictRedis()

random.seed()
def first():
    n = 10000
    
    for i in range(n):
        x = random.random()
        y = random.random()
        z = (x,y)
    
        if x**2+y**2 <= 1:
            print z
        else:
            del z
        
def doNormal():
    n = 1000
    counter = 0
    for i in range(n): 
        x = random.random()
        y = random.random()
        z = (x,y)
    
        if x**2+y**2 <= 1:
            counter += 1
            print(z)
        else:
            del z
    
    print counter
    pi = (counter/n) *4
    print pi

def doNumpy():
    import numpy as np
    
    N   = 10000000
    pts = np.random.random((N,2))
    
    # Select the points according to your condition
    idx = (pts**2).sum(axis=1)  < 1.0
    #print pts[idx], idx.sum()
    pi = (idx.sum()/N) *4
    #print "--"
    return pi

def doVolumeAVG(N):
		data_lst = r.hvals("hSTK:600016:VOL")
		data_lst = [float(val) for val in data_lst]
		l = np.array(data_lst[0:-2])
		#N = 1000
		volsum = 0
		for i in range(N):
		    vol_lst = l[np.random.randint(len(l), size=(len(l),1))]
		    
		    volavg = vol_lst.sum()/len(l)
		    print volavg 
		    volsum +=volavg

		return volsum/N

num = 0 
#for i in range(30):
#	pi = doNumpy()
#	num +=pi

#print "pi avg is :",num/30
#print doVolumeAVG(100)
#first()
def bench(func,parms=None): 
    import time
    start = time.clock()   
    rt = func() if parms is None else func(parms)
    stop = time.clock()  
    diff = stop - start  
    print "%s(%s) has taken %s" % (func.func_name,parms, str(diff)) 
    return rt

print bench(doNumpy)
# print(timeit.timeit("print(doNumpy())", setup="from __main__ import doNumpy", number=10))
# 
# print(timeit.timeit("print(doVolumeAVG(100))", setup="from __main__ import doVolumeAVG", number=10))

