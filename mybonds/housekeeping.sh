#/bin/sh
python /root/mybonds/build/__init__.py cleanDocChannelByTime 3 delete notwithtag
python /root/mybonds/build/__init__.py cleanStockChannel delete
redis-cli keys queue:* | grep done| xargs redis-cli del
 