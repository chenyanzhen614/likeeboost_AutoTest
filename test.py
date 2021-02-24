#coding:utf-8
import time
import datetime
start_time =int(round(time.time()* 1000))
end_time = start_time - 3600000
i = 1
dtime = datetime.datetime.now()
ptime =dtime - datetime.timedelta(hours= i +1)
un_time = int(round(time.mktime(dtime.timetuple())* 1000))
p_time =int(round(time.mktime(ptime.timetuple())* 1000))
print un_time
print p_time
