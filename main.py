
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
            price_df = pd.concat([price_df, fdr.DataReader(stock, start='2022-11-1')[['Close']]], axis = 1)
        except:
            print(stock)
            continue
    price_df.columns = data.stock
    price_df = price_df.dropna(axis=1)

    price_df = price_df[np.random.choice(price_df.columns.tolist(), 20, replace=False)]
    market = fdr.DataReader('KS11', start='2022-11-1')[['Close']] # 0.9.50 버그 KS200지수는 당일치만 추출된다.
    market.columns = ['코스피지수']

#***************************************************
#   prortfolio, cov, beta, diversification ratio
#***************************************************
    # daily log return
    p = price_df.pct_change() # 기능상 전 종목 첫째행은 Na로 나타나 남
    rtn = np.log(price_df / price_df.shift(1)).dropna() # 위 결과와 유사한 값나옴 dropna()은 Na로 된 행을 삭제 해줌

    mean_rtn = rtn.mean(axis=0)
    cov_rtn = np.cov(rtn, rowvar=False)
    market_rtn = np.log(market / market.shift(1)).dropna()

    beta = {}
    market_var = np.var(market_rtn, ddof=1)
    for i in range(len(price_df.columns)):
        covar_mat = np.cov(rtn.iloc[:, i], market_rtn.iloc[:, 0], rowvar=False)
        cov = covar_mat[0,1]
        beta[rtn.columns[i]] = (cov/market_var)

    # 너무 어렵고 샘플대로 구현이 안되고 에러 난다.
    #  beta[rtn.columns[i]] = (cov/market_var).market -> 이건 내가 봐도 이상하다
    # 특히 코스피지수, 종목 데이타 같은기간 요청핬는데도 일짜 길이가 달랐다.
    # fdr.DataReader('KS11', start='2020-1-1')[['Close']]
    # fdr.DataReader(stock, start='2022-11-1')[['Close']]



    print(market)
    print(price_df)

