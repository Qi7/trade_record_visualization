#!/usr/bin/env python
# coding: utf-8


import jqdatasdk as jq
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
import talib as tb

jq.auth('用户名', '密码')

"""
交易合约
聚宽合约名称
K线频率

j, XDCE
jd, XDCE
"""
commodity_config = {'jd': ['jd2101', 'JD2101.XDCE'],
                    'pp': ['pp2101', 'PP2101.XDCE'],
                    'zc': ['ZC101', 'ZC2101.XZCE'],
                    'ap': ['AP101', 'AP2101.XZCE'],
                    'ni': ['ni2102', 'NI2102.XSGE']
                    }
commodity = 'ni'

record_contract = commodity_config[commodity][0]
jq_contract = commodity_config[commodity][1]
kline_freq = '5m'
start_date = '2020-11-10'
end_date = '2020-11-17'

# mpf.plot(df_k, type='candle')

df_record = pd.read_excel('record_visualization/trade_record.xlsx')
df_record['dt'] = pd.to_datetime(df_record.date_.astype('str') + ' ' + df_record['报单时间'])

df_record1 = df_record.loc[df_record['合约'] == record_contract, :].set_index('dt')

df_k = jq.get_price(jq_contract, frequency=kline_freq, start_date=start_date, end_date=end_date)

k_line_index = df_k.index.values

bar_height = np.mean(df_k.high - df_k.low)


# 寻找record在k线的时间戳里的位置
def find_index(ts_):
    return np.where(k_line_index >= ts_)[0][0]


df_record1.loc[:, 'idx'] = [find_index(x) for x in np.array(df_record1.index)]

fig, ax = plt.subplots()
sma30 = mpf.make_addplot(tb.SMA(df_k.open, 30), ax=ax)
mpf.plot(df_k, type='candle', style='binance', ax=ax, addplot=[sma30])
ax.plot(np.array(df_k.rolling(20)['high'].max().shift(1)), linewidth=1)
ax.plot(np.array(df_k.rolling(20)['low'].min().shift(1)), linewidth=1)
ax.set_title(record_contract + ':' + kline_freq)

mpl.rcParams['figure.figsize'] = (20, 12)
mpl.rcParams["font.family"] = "STSong"

for i in range(df_record1.shape[0]):
    record = df_record1.iloc[i, :]
    y_ = record['报单价格']
    x_ = record['idx']

    if record['买卖'] == '买':
        y_anno = y_ - bar_height * 3
    elif record['买卖'] == '卖':
        y_anno = y_ + bar_height * 3
    else:
        y_anno = y_
    ax.annotate(record['开平'] + str(record['报单手数']) + '手' + '\n' + record['报单状态'], xy=(x_, y_), xycoords='data',
                xytext=(x_, y_anno), textcoords='data',
                arrowprops=dict(arrowstyle='wedge', connectionstyle="arc3"))
