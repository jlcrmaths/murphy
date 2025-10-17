# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df: pd.DataFrame):
    """
    Estrategia basada en MACD:
    - Cruce alcista → señal BUY
    - Cruce bajista → señal SELL
    """
    df = df.sort_values('timestamp')
    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    if len(df) < 35:
        return None

    last, prev = df.iloc[-1], df.iloc[-2]

    # Cruce alcista
    if prev['macd'] < prev['signal'] and last['macd'] > last['signal']:
        print("[MACD] Cruce alcista detectado ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 1.02,
            'sl': last['close'] * 0.98,
            'reason': 'Cruce alcista de MACD',
            'shares': 100,
            'color': 'green'
        }

    # Cruce bajista
    if prev['macd'] > prev['signal'] and last['macd'] < last['signal']:
        print("[MACD] Cruce bajista detectado ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 0.98,
            'sl': last['close'] * 1.02,
            'reason': 'Cruce bajista de MACD',
            'shares': 100,
            'color': 'red'
        }

    return None


