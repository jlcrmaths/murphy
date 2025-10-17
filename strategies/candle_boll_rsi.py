# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_signal(df: pd.DataFrame):
    """
    Estrategia combinada: Velas fuertes + Bandas de Bollinger + RSI
        - BUY si vela fuerte toca banda inferior y RSI < 30
        - SELL si vela fuerte toca banda superior y RSI > 70
    """
    df = df.copy()
    df['sma'] = df['close'].rolling(20).mean()
    df['std'] = df['close'].rolling(20).std()
    df['upper'] = df['sma'] + 2 * df['std']
    df['lower'] = df['sma'] - 2 * df['std']

    # RSI 14 periodos
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    last = df.iloc[-1]
    body = abs(last['close'] - last['open'])
    range_ = last['high'] - last['low']
    strong_candle = range_ > 0 and body / range_ > 0.6

    # Rebote en banda inferior con RSI bajo
    if strong_candle and last['close'] < last['lower'] and last['rsi'] < 30:
        print("[Candle+Boll+RSI] Rebote técnico detectado ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['sma'],
            'sl': last['close'] * 0.97,
            'reason': 'Rebote en banda inferior con RSI<30',
            'shares': 100,
            'color': 'green'
        }

    # Corrección en banda superior con RSI alto
    if strong_candle and last['close'] > last['upper'] and last['rsi'] > 70:
        print("[Candle+Boll+RSI] Corrección probable ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['sma'],
            'sl': last['close'] * 1.03,
            'reason': 'Corrección en banda superior con RSI>70',
            'shares': 100,
            'color': 'red'
        }

    return None

