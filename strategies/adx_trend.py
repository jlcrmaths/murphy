# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_signal(df):
    """
    Estrategia basada en ADX (Average Directional Index)
    Señal:
        - BUY si ADX > 25 y +DI > -DI
        - SELL si ADX > 25 y +DI < -DI
    """
    df = df.copy()
    high, low, close = df['high'], df['low'], df['close']
    
    df['tr'] = np.maximum.reduce([high - low, 
                                  abs(high - close.shift()), 
                                  abs(low - close.shift())])
    df['dm_plus'] = np.where(high.diff() > low.diff(), np.maximum(high.diff(),0), 0)
    df['dm_minus'] = np.where(low.diff() > high.diff(), np.maximum(low.diff(),0), 0)
    
    tr14 = df['tr'].rolling(14).sum()
    plus14 = df['dm_plus'].rolling(14).sum()
    minus14 = df['dm_minus'].rolling(14).sum()
    
    df['di_plus'] = 100 * plus14 / tr14
    df['di_minus'] = 100 * minus14 / tr14
    df['adx'] = 100 * abs(df['di_plus'] - df['di_minus']) / (df['di_plus'] + df['di_minus'])
    
    latest = df.iloc[-1]
    signal = {}
    if latest['adx'] > 25:
        if latest['di_plus'] > latest['di_minus']:
            signal = {'signal': 'BUY', 'reason': 'ADX fuerte y +DI > -DI'}
        else:
            signal = {'signal': 'SELL', 'reason': 'ADX fuerte y +DI < -DI'}
    return signal
