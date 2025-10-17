# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_signal(df):
    """
    Señal basada en Rate of Change (ROC):
        - BUY si ROC positivo y creciente
        - SELL si ROC negativo y decreciente
    """
    df = df.copy()
    df['roc'] = df['close'].pct_change(periods=5) * 100
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    signal = {}
    if latest['roc'] > 0 and latest['roc'] > prev['roc']:
        signal = {'signal': 'BUY', 'reason': 'ROC positivo y en aumento', 'color': 'green'}
    elif latest['roc'] < 0 and latest['roc'] < prev['roc']:
        signal = {'signal': 'SELL', 'reason': 'ROC negativo y en descenso', 'color': 'red'}
    return signal
