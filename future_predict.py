from datetime import date, datetime
from workalendar.asia import Taiwan
cal = Taiwan()
if cal.is_working_day(date.today()) == False:
    exit()
else:
    pass
    day = date.today()
    day.day
from bs4 import BeautifulSoup
from lxml import etree
import requests
## 如果網站日期小於昨天(避免假日補班日)
req = requests.get("https://www.taifex.com.tw/cht/3/futContractsDate", verify=False)
soup = BeautifulSoup(req.content, 'html.parser')
soup_string = str(soup)
selector=etree.HTML(soup_string)
dt = selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[1]/td/p/span[2]')
dt = datetime.strptime(dt[0].text[2::], "%Y/%m/%d").date()
if dt < day:
    exit()
else:
    pass


import pandas as pd
import numpy as np


date_today = date.today().strftime('%Y/%m/%d')

data = pd.read_csv('期貨法人未平倉_new.csv')

new_data = data[data.identity == 'foreign_investment']
#new_data['amount'] = new_data['amount'].replace('[,]', '', regex=True).astype(int)

def last_day_avg():  # 前五天未平倉平均
    list = []
    index = 0
    today_amount = new_data['amount'].iloc[index]
    for i in range(1,6):
        # index += i
        list += [new_data['amount'].iloc[i]] # 前五日每天留倉口數
    avg = np.average(list) # 加總平均
    return (today_amount - avg), today_amount, avg

def difference(): # 昨天與今天差距
    list = []
    index = 1
    yest_amount = new_data['amount'].iloc[index]
    for i in range(1, 6):
        # index += i
        list += [new_data['amount'].iloc[i+1]] # 前五日每天留倉口數
    avg = np.average(list)
    res = (yest_amount - avg)
    return res, yest_amount

res, today, avg = last_day_avg()
res2, yest = difference()
diff = (res - res2) # 與昨天差距
percent = ((today-avg)/avg)*100
with open('明天做多or做空.txt', 'w') as f:
    f.write('今天外資留倉：%d\n昨天留倉：%d\n前五日平均：%.2f\n(留倉 - 前5日平均)：%.2f\
        \n昨天(留倉 - 前5日平均)：%.2f\n與昨天差距：%.2f\n當日留倉大於前五日平均幾%s：%.2f%s'
        %(today, yest, avg, res, res2, diff, '%', percent, '%'))

def main_strategy():
    output = ''
    output2 = ''
    if diff >=0:
        output = '明天可能開"紅"'
    else:
        output = '明天可能開"綠"'
    if res >=1000:
        output2 = '明天建議做"多"'
    else:
        output2 = '明天建議做"空"'
    return output, output2
output1, output2 = main_strategy()
'''print('今天%s外資留倉：%d\n昨天留倉：%d\n前五日平均：%.2f\n(留倉 - 前5日平均)：%.2f\
    \n昨天(留倉 - 前5日平均)：%.2f\n與昨天差距：%.2f\n當日留倉大於前五日平均幾%s：%.2f%s\n\n%s\n\n%s'
    %(date_today, today, yest, avg, res, res2, diff, '%', percent, '%', output1, output2))'''
######################################################
## line notify
headers = {"Authorization": "Bearer " + "your token",
            "Content-Type": "application/x-www-form-urlencoded"}
params = {'message':'今天%s外資留倉：%d\n昨天留倉：%d\n前五日平均：%.2f\n(留倉 - 前5日平均)：%.2f\
    \n昨天(留倉 - 前5日平均)：%.2f\n與昨天差距：%.2f\n當日留倉大於前五日平均幾%s：%.2f%s\n\n%s\n\n%s'
    %(date_today, today, yest, avg, res, res2, diff, '%', percent, '%', output1, output2)}

r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)
