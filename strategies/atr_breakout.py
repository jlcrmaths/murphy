# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_signal(df):
    """
    Señal basada en ruptura de rango con ATR:
        - BUY si close rompe máximo previo + 1 ATR
        - SELL si close rompe mínimo previo - 1 ATR
    """
    df = df.copy()
    high, low, close = df['high'], df['low'], df['close']
    df['tr'] = np.maximum.reduce([high - low,
                                  abs(high - close.shift()),
                                  abs(low - close.shift())])
    df['atr14'] = df['tr'].rolling(14).mean()
    latest = df.iloc[-1]

    signal = {}
    if latest['close'] > df['high'].shift(1) + latest['atr14']:
        signal = {'signal': 'BUY', 'reason': 'Ruptura de máximo + ATR', 'color': 'green'}
    elif latest['close'] < df['low'].shift(1) - latest['atr14']:
        signal = {'signal': 'SELL', 'reason': 'Ruptura de mínimo - ATR', 'color': 'red'}
    return signal
