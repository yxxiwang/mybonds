#/bin/sh
python /root/mybonds/build/__init__.py cleanDocChannelByTime 1 delete notwithtag
#python /root/mybonds/build/__init__.py cleanStockChannel delete
python /root/mybonds/build/__init__.py updateChannelAndStock 24

redis-cli keys queue:* | grep done| xargs redis-cli del

redis-cli save
cp /data/dump.rdb  /data/dump.rdb.$(date +'%Y%m%d')
