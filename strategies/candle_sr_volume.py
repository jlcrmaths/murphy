# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df: pd.DataFrame):
    df = df.copy()
    df['vol_avg'] = df['volume'].rolling(20).mean()
    df['max20'] = df['high'].rolling(20).max()
    df['min20'] = df['low'].rolling(20).min()

    last = df.iloc[-1]

    # vela decisiva: cuerpo grande y volumen alto
    body = abs(last['close'] - last['open'])
    range_ = last['high'] - last['low']
    strong_candle = range_ > 0 and body / range_ > 0.7
    vol_ok = last['volume'] > 1.5 * last['vol_avg']

    # Ruptura de resistencia con confirmación de volumen
    if strong_candle and last['close'] > last['max20'] * 0.999 and vol_ok:
        print("[Candle+SR+Vol] Ruptura alcista confirmada ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 1.015,
            'sl': last['close'] * 0.985,
            'reason': 'Ruptura de resistencia con volumen y vela fuerte',
            'shares': 100
        }

    # Ruptura bajista de soporte con volumen
    if strong_candle and last['close'] < last['min20'] * 1.001 and vol_ok:
        print("[Candle+SR+Vol] Ruptura bajista confirmada ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 0.985,
            'sl': last['close'] * 1.015,
            'reason': 'Ruptura de soporte con volumen y vela fuerte',
            'shares': 100
        }

    return None
