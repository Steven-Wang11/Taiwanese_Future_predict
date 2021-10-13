# Taiwanese_Future_predict
## 介紹
這是一套預測明日台灣指數期貨開紅或綠的系統

## 使用方法
1.  先使用`auto_futurs.py`來爬取三大法人資訊。
2.  利用`rowdata_creator.py`整理成預測時需要計算的數據格式，並順便爬取台指期當日交易資訊。
3.  最後執行`future_predict.py`會輸出`.txt`檔案，本程也包含line bot推播通知程式碼範例
