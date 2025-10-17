# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

ATR_LEN = 14  # Periodo de ATR

def generate_signal(df: pd.DataFrame):
    """
    Estrategia ATR Breakout:
    Detecta rupturas basadas en ATR y rango de velas recientes.
    """
    df = df.copy()
    
    # Calcular ATR
    df['high_low'] = df['high'] - df['low']
    df['high_prevclose'] = abs(df['high'] - df['close'].shift())
    df['low_prevclose'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['high_low', 'high_prevclose', 'low_prevclose']].max(axis=1)
    df['atr'] = df['tr'].rolling(ATR_LEN).mean()

    if len(df) < ATR_LEN + 1:
        return None  # datos insuficientes

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Condiciones de ruptura alcista
    breakout_up = last['close'] > prev['high'] + prev['atr']
    # Condiciones de ruptura bajista
    breakout_down = last['close'] < prev['low'] - prev['atr']

    # Vela decisiva: cuerpo > 70% del rango
    body = abs(last['close'] - last['open'])
    range_ = last['high'] - last['low']
    strong_candle = range_ > 0 and body / range_ > 0.7

    if strong_candle and breakout_up:
        print("[ATR Breakout] Ruptura alcista detectada ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] + last['atr'] * 2,
            'sl': last['close'] - last['atr'] * 1.5,
            'reason': 'Ruptura alcista con ATR',
            'shares': 100
        }

    if strong_candle and breakout_down:
        print("[ATR Breakout] Ruptura bajista detectada ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] - last['atr'] * 2,
            'sl': last['close'] + last['atr'] * 1.5,
            'reason': 'Ruptura bajista con ATR',
            'shares': 100
        }

    return None

