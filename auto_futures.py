from datetime import date, datetime
from workalendar.asia import Taiwan
cal = Taiwan()
if cal.is_working_day(date.today()) == False:
    exit()
else:
    pass

from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import etree # for xpath selector



url = 'https://www.taifex.com.tw/cht/3/futContractsDate'
def get_csv():
    origin_csv = pd.read_csv('G:/Taiwanese_Futures/期貨法人未平倉_new.csv', encoding= 'utf-8')
    origin_csv = origin_csv.sort_values('Date', ascending=True)
    origin_csv = origin_csv.reset_index()
    origin_csv = origin_csv.drop(['index'], axis=1)
    origin_csv.info()
    return origin_csv

def get_value(url):
    req = requests.get(url, verify=False)
    soup = BeautifulSoup(req.content, 'html.parser')
    soup_string = str(soup)
    selector=etree.HTML(soup_string)
    lst = [7,9,11]
    target1 = []
    target2 = []
    for i in range(4, 7):
        if i == 4:
            target1 += selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[2]/td/table/tbody/tr[4]/th[3]/div')
        else:
            target1 += selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[2]/td/table/tbody/tr[%d]/th/div'%i)
        for y in lst:
            target2 += selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[4]/table/tbody/tr[2]/td/table/tbody/tr[%d]/td[%d]/div[1]/font'%(i,y))

    for idx, i in enumerate(target2):
        target2[idx].text = target2[idx].text.strip()
        target2[idx].text = target2[idx].text.replace(',','')
        print(target2[idx].text)

    for idx, i in enumerate(target1):
        target1[idx].text = target1[idx].text.strip()
        if i.text == '自營商':
            i.text = 'Self_employed'
        elif i.text == '投信':
            i.text = 'Investment_Trust'
        else:
            i.text = 'foreign_investment'
        print(i.text)
    target1 = [target1[idx].text for idx, i in enumerate(target1)]
    target2 = [target2[idx].text for idx, i in enumerate(target2)]
    return target1, target2


def data_append():
    target1, target2 = get_value(url)
    today = datetime.today()
    today = today.strftime('%Y/%m/%d')
    value_lst = []
    idx_temp = 0
    for i in target1:
        value_lst += [today] + [i]
        for y in range(3):
            value_lst += [target2[idx_temp + y]]
        idx_temp += 3


    origin_csv = get_csv()
    idx_temp = 0
    for i in range(3):
        origin_csv.loc[len(origin_csv)] = value_lst[idx_temp:idx_temp + 5]
        idx_temp += 5
    origin_csv['Date'] = origin_csv['Date'].apply(pd.Timestamp)
    origin_csv = origin_csv.sort_values('Date', ascending=False)
    origin_csv = origin_csv.reset_index()
    origin_csv = origin_csv.drop(['index'], axis=1)
    origin_csv.to_csv('期貨法人未平倉_new.csv', index = False)
    print('''░░░░░░░░░░░░░░░░░░░░░░█████████
░░███████░░░░░░░░░░███▒▒▒▒▒▒▒▒███
░░█▒▒▒▒▒▒█░░░░░░░███▒▒▒▒▒▒▒▒▒▒▒▒▒███
░░░█▒▒▒▒▒▒█░░░░██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
░░░░█▒▒▒▒▒█░░░██▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒███
░░░░░█▒▒▒█░░░█▒▒▒▒▒▒████▒▒▒▒████▒▒▒▒▒▒██
░░░█████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
░░░█▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒██
░██▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒██▒▒▒▒▒▒▒▒▒▒██▒▒▒▒██
██▒▒▒███████████▒▒▒▒▒██▒▒▒▒▒▒▒▒██▒▒▒▒▒██
█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒████████▒▒▒▒▒▒▒██
██▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
░█▒▒▒███████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
░██▒▒▒▒▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█
░░████████████░░░█████████████████
''')

data_append()
