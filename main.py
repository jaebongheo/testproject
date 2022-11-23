
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
from bs4 import BeautifulSoup
import FinanceDataReader as fdr
import re
from tqdm import tqdm


if __name__ == '__main__':
#*******************
# Data Load
#*******************
    url = "http://finance.naver.com/sise/entryJongmok.nhn?&page="
    result = []
    for i in range(1, 21):
        tmp_url = url + str(i)
        res = requests.get(tmp_url)
        doc = BeautifulSoup(res.text, 'html5lib')
        items = doc.find_all('td', {'class':'ctg'})
        for item in items:
            text = item.a.get('href')
            k = re.search('[\d]+', text)
            if k:
                code = k.group()
                name = item.text
                data = code, name
                result.append(data)

    data = pd.DataFrame(result, columns=['code', 'stock'])
    price_df = pd.DataFrame()
    for stock in tqdm(data.code): # 쥬피터노트북 전용 진행률바
        try:
            price_df = pd.concat([price_df, fdr.DataReader(stock, start='2020-1-1')[['Close']]], axis = 1)
        except:
            print(stock)
            continue
    price_df.columns = data.stock
    price_df = price_df.dropna(axis=1)

    price_df = price_df[np.random.choice(price_df.columns.tolist(), 20, replace=False)]
    market = fdr.DataReader('KS11', start='2020-1-1')[['Close']] # 0.9.50 버그 KS200지수는 당일치만 추출된다.
    market.columns = ['코스피지수']

#***************************************************
#   prortfolio, cov, beta, diversification ratio
#***************************************************

    # print(market)
    # print(price_df)

