from datetime import date, datetime
from workalendar.asia import Taiwan # 讀取台灣國定假日
cal = Taiwan()
if cal.is_working_day(date.today()) == False: # is today workday?
    exit()
else:
    pass

from bs4 import BeautifulSoup
from lxml import etree # for xpath selector
import requests
import pandas as pd
import sys

def prepare(): # 數據前置準備
    url = 'https://www.taifex.com.tw/cht/3/futDailyMarketReport'
    target_data = pd.read_csv('外資.csv') # 要更新的檔案

    target_data.info()

    foreign_amount_df = pd.read_csv('期貨法人未平倉_new.csv') # 每日爬的數據
    foreign_amount_df['Date'] = foreign_amount_df['Date'].apply(pd.Timestamp)
    foreign_amount_df = foreign_amount_df[foreign_amount_df.identity == 'foreign_investment'] # 只要外資
    foreign_amount_df = foreign_amount_df.sort_values('Date', ascending=True) # 降排序
    foreign_amount_df = foreign_amount_df.reset_index() # 篩選或排序後都必須重新整理index
    foreign_amount_df = foreign_amount_df.drop(['index'], axis=1) # 刪除舊的index
    #foreign_amount_df.iloc[:,2:] = foreign_amount_df.iloc[:,2:].replace(',','',regex = True).astype(int) # dollar format to int
    foreign_amount_df.info()

    new_data = pd.DataFrame(columns = target_data.columns)
    return url, target_data, foreign_amount_df, new_data



def web_value_get(url): # 開始爬數據
    req = requests.get(url, verify = False)
    soup = BeautifulSoup(req.content, 'html.parser')
    soup_string = str(soup) # etree only support string type of html data
    selector=etree.HTML(soup_string)

    td_lst = [3,4,5,6,7] # 根據網站的xpath的idx，詳情請見網址
    target = []
    target += selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[3]/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td[2]/div')
    target[0].text = target[0].text.replace(' ','')
    for i in range(5):
        idx = td_lst[i]
        if idx != 7 and idx != 8:
            target += selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[3]/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td[%d]'%idx)
        else: # 刪除多餘的符號
            target += selector.xpath('/html/body/div[1]/div[4]/div[2]/div/div[3]/table/tbody/tr[2]/td/table[2]/tbody/tr[2]/td[%d]/font'%idx)
            if '▼' in target[-1].text:
                target[-1].text = target[-1].text.replace('▼','')
            else:
                target[-1].text = target[-1].text.replace('▲','')
    return target


def data_creat(target_data, foreign_amount_df, new_data, target): # prepare a new row for add to the newdata
    today = date.today().strftime('%Y/%m/%d') # the date of today
    value = [foreign_amount_df.iloc[len(foreign_amount_df)-1,i] for i in range(2, 5)] # get the lastest values from the 期貨法人未平倉_new.csv

    target = [target[idx].text for idx, i in enumerate(target)] # element format to text
    lst = []
    lst += [today] + ['foreign_investment'] + value + target # creat a list to save the values we need

    new_data.loc[len(new_data)] = lst # and finally we add new row from lst
    new_data = target_data.append(new_data).reset_index()
    new_data = new_data.drop(['index'], axis=1)
    new_data['Date'] = new_data['Date'].apply(pd.Timestamp) # for time series
    #new_data.iloc[:,2:] = new_data.iloc[:,2:].astype(int) # format object to int
    new_data.info()
    new_data.to_csv('外資.csv', index=False)
    print('*' * 10 + '\n\n\nDONE\n\n\n' + '*' * 10)


url, target_data, foreign_amount_df, new_data = prepare()
target = web_value_get(url)
data_creat(target_data, foreign_amount_df, new_data, target)
