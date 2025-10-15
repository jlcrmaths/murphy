# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df: pd.DataFrame):
    df['ema_fast'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=30, adjust=False).mean()
    last, prev = df.iloc[-1], df.iloc[-2]

    if prev['ema_fast'] < prev['ema_slow'] and last['ema_fast'] > last['ema_slow']:
        print("[EMA] Cruce alcista ✅")
        return {'timestamp': last['timestamp'], 'entry': last['close'], 'tp': last['close'] * 1.02,
                'sl': last['close'] * 0.98, 'reason': 'Cruce alcista de EMAs', 'shares': 100}

    if prev['ema_fast'] > prev['ema_slow'] and last['ema_fast'] < last['ema_slow']:
        print("[EMA] Cruce bajista ⚠️")
        return {'timestamp': last['timestamp'], 'entry': last['close'], 'tp': last['close'] * 0.98,
                'sl': last['close'] * 1.02, 'reason': 'Cruce bajista de EMAs', 'shares': 100}

    return None
