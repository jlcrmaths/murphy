# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df):
    """
    Estrategia de ruptura basada en ATR
    - BUY si cierre rompe máximo de n días + volatilidad ATR
    - SELL si cierre rompe mínimo de n días - ATR
    """
    n = 14
    df = df.copy()
    df['high_max'] = df['high'].rolling(n).max()
    df['low_min'] = df['low'].rolling(n).min()
    df['tr'] = df['high'] - df['low']
    df['atr'] = df['tr'].rolling(n).mean()
    
    latest = df.iloc[-1]
    signal = {}
    if latest['close'] > latest['high_max'] - 0.5*latest['atr']:
        signal = {'signal':'BUY', 'reason':'Ruptura de máximo + ATR'}
    elif latest['close'] < latest['low_min'] + 0.5*latest['atr']:
        signal = {'signal':'SELL', 'reason':'Ruptura de mínimo - ATR'}
    return signal
