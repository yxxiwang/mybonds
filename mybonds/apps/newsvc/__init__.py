#!/usr/bin/python
# -*- coding: utf-8 -*-
from numpy.ma.core import isMA  
import json, numpy, time
import csv, string, random
import sys,os
import redis
import traceback
import urllib2
import datetime as dt

from mybonds.apps import *
from mybonds.apps.newspubfunc import *
# # 
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379 
# REDIS_EXPIRETIME = 186400
# DOC_EXPIRETIME = 86400*7
# KEY_UPTIME = 1800
# QUANTITY = 1500
# QUANTITY_DURATION = 300
# r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
# rdoc = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)

