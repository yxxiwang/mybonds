#!/usr/bin/python
# -*- coding: utf-8 -*- 
import json, urllib2, urllib
import csv, string,random
import sys, time
import redis
import numpy
import traceback 
import datetime as dt
from numpy.ma.core import isMA   

print "hello"
#map function
#basic syntax
def mul2(x):
  return x*2
testList = [1,2,3,4]
print map(mul2,testList)
print map(lambda x: x*3,testList)
#map function that has two arguments
def mul(x,y):
  return x*y
print map(mul,[1,2,3,4],testList)

#basic syntax(a function that yield)
def genMul2(N):
  for i in range(N):
   yield i * 2
for i in genMul2(5):print i
#inside for, the next method is called
#在for循环的内部，Python调用了next方法。
#下面的x叫做generator对象
x = genMul2(2)
#一直调用next方法，最后会抛出一个异常
print x
print x.next()
print x.next()
#print x.next()  !!!!error!!!!StopIteration


