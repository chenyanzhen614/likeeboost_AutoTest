#coding:utf-8
import requests
import json
import pymysql
import pygsheets
import os
import time
import datetime

#查看文件的目录
cur = os.getcwd()
auth_file = os.path.join(cur,"yanzhen.json")
#authorization授权
gc = pygsheets.authorize(service_file=auth_file)
# 打开对应google sheet
sh = gc.open('likeeboostAutoCase')
#选取sheet
wks = sh.worksheet_by_title("P0case")
#清空Actual response的值
wks.update_value('H11',"")

#调接口获取结果
def get_results(addr,interface_name):
    ip ='http://139.5.108.152:8011'
    url = ip + interface_name
    #转换为dict类型
    parameter = eval(str(wks.get_value(addr)))
    reponse = requests.post(url,json=parameter)
    wks.update_value('H11',interface_name + ':')
    wks.update_value('H11',reponse.text)
    print (parameter)
    return reponse 

#比较结果
def compare_two_dict(dict1, dict5):
    flag = True
    keys1 = dict1.keys()
    keys5 = dict5.keys()
    for key in keys1:
        if key in keys1 and key in keys5:
            if dict1[key] == dict5[key]:
                    flag = flag & True
            else:
                flag = flag & False
                print key
                print dict1[key]
                print dict5[key]
        else:
            raise Exception('key_list contains error key')
    if flag:
        result = 'PASS'
    else:
        result = 'FAILED'
    return result


#查询数据库
def mysql_select(sql):
    db = pymysql.connect("146.196.79.131","dev","devPwd234%","bigo_goods")
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return result

#更新数据库
def mysql_update(sql):
    db = pymysql.connect("146.196.79.131","dev","devPwd234%","bigo_goods")
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close() 

#获取价格
reponse=get_results('C11','/order/price')
orderSN=reponse.json()['data']['orderSN']

#create order
reponse=get_results('D11','/order/add')
order_status=reponse.json()['data']['status']
assert order_status == 1 

##审核通过
reponse=get_results('E11','/order/audit')

#查询数据库
sql1= "select status from orders   WHERE  order_id =  \"%s\" " % orderSN
assert mysql_select(sql1) == 2 
#最初的推广时间
sql2= "select delivery_time from orders WHERE order_id =  \"%s\" " % orderSN
assert mysql_select(sql2) == 120   

#延时一次 
#处理时间
dtime = datetime.datetime.now()
end_time = int(round(time.mktime(dtime.timetuple())* 1000))
sql= "update orders set popularize_end_time=\"%s\"   where order_id = \"%s\" " %(end_time,orderSN)
mysql_update(sql)
time.sleep(10)
sql3= "select delivery_time from orders WHERE order_id =  \"%s\" " % orderSN
assert int(mysql_select(sql3)) == 180


##推广时间结束，最小曝光量<实际曝光量<最大曝光量，粉丝粉丝量<目标涨粉量，订单状态改为不变，推广开始和结束时间根据刊例配置的延长时间进行延长
sql_N= "update popularize_status_new set order_id = \"%s\",expose_count ='1001',follow_count='50'   where update_time = ('1575826750') " % orderSN
mysql_update(sql_N)
end_time = int(round(time.mktime(dtime.timetuple())* 1000))
sql_O= "update orders set popularize_end_time=\"%s\"   where order_id = \"%s\" " %(end_time,orderSN)
mysql_update(sql_O)
time.sleep(10)
#检查结果
sql4= "select delivery_time from orders WHERE order_id =  \"%s\" " % orderSN
assert int(mysql_select(sql4)) == 240

#推广时间结束，最小曝光量<实际曝光量<最大曝光量，粉丝粉丝量>=目标涨粉量，订单状态改为：已完成，不退款
sql_N= "update popularize_status_new set order_id = \"%s\",expose_count ='1001',follow_count='101'   where update_time = ('1575826750') " % orderSN
mysql_update(sql_N)
end_time = int(round(time.mktime(dtime.timetuple())* 1000))
sql_O= "update orders set popularize_end_time=\"%s\"   where order_id = \"%s\" " %(end_time,orderSN)
mysql_update(sql_O)
time.sleep(10)
#检查结果
sql4= "select delivery_time from orders WHERE order_id =  \"%s\" " % orderSN
assert int(mysql_select(sql4)) == 240
sql5= "select status from orders WHERE order_id =  \"%s\" " % orderSN
assert mysql_select(sql5) == 4
sql6= "select status from popularize_order_sync WHERE order_id =  \"%s\" " % orderSN
assert mysql_select(sql6) == 2 

##查询订单
reponse=get_results('F11','/order/get')
orderSN4=reponse.json()['data']['orderInfos'][0]
print(orderSN4)

orderinfo=eval(str(wks.get_value('I11')))
#比较结果
result1=compare_two_dict(orderinfo, orderSN4)
print result1
