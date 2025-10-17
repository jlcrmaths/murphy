# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df: pd.DataFrame):
    """
    Estrategia basada en cruce de EMAs:
    - Cruce alcista → señal BUY
    - Cruce bajista → señal SELL
    """
    df = df.copy()
    df['ema_fast'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=30, adjust=False).mean()
    last, prev = df.iloc[-1], df.iloc[-2]

    # Cruce alcista
    if prev['ema_fast'] < prev['ema_slow'] and last['ema_fast'] > last['ema_slow']:
        print("[EMA] Cruce alcista ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 1.02,
            'sl': last['close'] * 0.98,
            'reason': 'Cruce alcista de EMAs',
            'shares': 100,
            'color': 'green'
        }

    # Cruce bajista
    if prev['ema_fast'] > prev['ema_slow'] and last['ema_fast'] < last['ema_slow']:
        print("[EMA] Cruce bajista ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 0.98,
            'sl': last['close'] * 1.02,
            'reason': 'Cruce bajista de EMAs',
            'shares': 100,
            'color': 'red'
        }

    return None

