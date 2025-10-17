# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df):
    """
    Señal basada en patrón de velas Engulfing:
        - BUY si Bullish Engulfing
        - SELL si Bearish Engulfing
    """
    df = df.copy()
    signal = {}
    if len(df) < 2:
        return signal

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Bullish Engulfing
    if last['close'] > last['open'] and prev['close'] < prev['open'] and last['close'] > prev['open'] and last['open'] < prev['close']:
        signal = {'signal': 'BUY', 'reason': 'Bullish Engulfing', 'color': 'green'}
    # Bearish Engulfing
    elif last['close'] < last['open'] and prev['close'] > prev['open'] and last['open'] > prev['close'] and last['close'] < prev['open']:
        signal = {'signal': 'SELL', 'reason': 'Bearish Engulfing', 'color': 'red'}
    return signal

