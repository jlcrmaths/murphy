# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_signal(df: pd.DataFrame):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    last = df.iloc[-1]

    if last['rsi'] < 30:
        print("[RSI] Sobreventa detectada → posible rebote ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 1.03,
            'sl': last['close'] * 0.97,
            'reason': 'RSI < 30 (sobreventa)',
            'shares': 100
        }

    if last['rsi'] > 70:
        print("[RSI] Sobrecompra detectada → posible corrección ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 0.97,
            'sl': last['close'] * 1.03,
            'reason': 'RSI > 70 (sobrecompra)',
            'shares': 100
        }

    return None
