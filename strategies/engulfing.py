# -*- coding: utf-8 -*-
def generate_signal(df):
    """
    Estrategia basada en patrón de vela envolvente
    - BUY si vela verde envuelve la previa roja
    - SELL si vela roja envuelve la previa verde
    """
    if len(df) < 2:
        return {}
    prev, curr = df.iloc[-2], df.iloc[-1]
    signal = {}
    # Vela verde envuelve roja
    if curr['close'] > curr['open'] and prev['close'] < prev['open']:
        if curr['open'] < prev['close'] and curr['close'] > prev['open']:
            signal = {'signal':'BUY', 'reason':'Vela envolvente alcista'}
    # Vela roja envuelve verde
    elif curr['close'] < curr['open'] and prev['close'] > prev['open']:
        if curr['open'] > prev['close'] and curr['close'] < prev['open']:
            signal = {'signal':'SELL', 'reason':'Vela envolvente bajista'}
    return signal
