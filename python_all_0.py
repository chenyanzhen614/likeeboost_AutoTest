#coding:utf-8
import requests
import json
import pymysql
import pygsheets
import os

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
wks.update_value("H2","")

#调接口获取结果
def get_results(addr,interface_name):
    ip ='http://139.5.108.152:8011'
    url = ip + interface_name
    #转换为dict类型
    parameter = eval(str(wks.get_value(addr)))
    reponse = requests.post(url,json=parameter)
    wks.update_value("H2",interface_name + ':')
    wks.update_value("H2",reponse.text)
    print (parameter)
    return reponse 

#比较结果
def compare_two_dict(dict1, dict2):
    flag = True
    keys1 = dict1.keys()
    keys2 = dict2.keys()
    for key in keys1:
        if key in keys1 and key in keys2:
            if dict1[key] == dict2[key]:
                    flag = flag & True
            else:
                flag = flag & False
                print key
                print dict1[key]
                print dict2[key]
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

#获取价格
reponse=get_results('C2','/order/price')
orderSN=reponse.json()['data']['orderSN']

#create order
reponse=get_results('D2','/order/add')
order_status=reponse.json()['data']['status']
assert order_status == 1 

##审核通过
reponse=get_results('E2','/order/audit')

#查询数据库
sql= "select status from orders   WHERE  order_id =  \"%s\" " % orderSN
assert mysql_select(sql) == 2 


##订单完成，全退款
reponse=get_results('F2','/order/audit')

##查询订单
reponse=get_results('F2','/order/get')
orderSN4=reponse.json()['data']['orderInfos'][0]
#print(type(orderSN4))

orderinfo=eval(str(wks.get_value("I2")))
#比较结果
result1=compare_two_dict(orderinfo, orderSN4)
print result1
