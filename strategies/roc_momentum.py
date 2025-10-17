# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df):
    """
    Estrategia basada en ROC (Rate of Change)
    - BUY si ROC(12) > 0 y creciente
    - SELL si ROC(12) < 0 y decreciente
    """
    n = 12
    df = df.copy()
    df['roc'] = (df['close'] - df['close'].shift(n)) / df['close'].shift(n) * 100
    
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    signal = {}
    if latest['roc'] > 0 and latest['roc'] > prev['roc']:
        signal = {'signal':'BUY', 'reason':'ROC positivo y en aumento'}
    elif latest['roc'] < 0 and latest['roc'] < prev['roc']:
        signal = {'signal':'SELL', 'reason':'ROC negativo y en descenso'}
    return signal
