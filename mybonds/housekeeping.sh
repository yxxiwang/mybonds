#/bin/sh
python /root/mybonds/build/__init__.py cleanDocChannelByTime 3 delete withstar
python /root/mybonds/build/__init__.py cleanDocStockChannel doc delete
redis-cli keys queue:* | grep done| xargs redis-cli del
 