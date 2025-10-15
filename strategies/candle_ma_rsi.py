# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def generate_signal(df: pd.DataFrame):
    df = df.copy()
    df['ema_fast'] = df['close'].ewm(span=10, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=20, adjust=False).mean()
    df['delta'] = df['close'].diff()
    df['gain'] = np.where(df['delta'] > 0, df['delta'], 0)
    df['loss'] = np.where(df['delta'] < 0, -df['delta'], 0)
    df['rsi'] = 100 - (100 / (1 + pd.Series(df['gain']).rolling(14).mean() / pd.Series(df['loss']).rolling(14).mean()))

    last, prev = df.iloc[-1], df.iloc[-2]

    # patrón de vela: cuerpo mayor a 70% del rango → vela decisiva
    body = abs(last['close'] - last['open'])
    range_ = last['high'] - last['low']
    strong_candle = range_ > 0 and body / range_ > 0.7

    # Cruce alcista con RSI moderado y vela fuerte
    if strong_candle and prev['ema_fast'] < prev['ema_slow'] and last['ema_fast'] > last['ema_slow'] and last['rsi'] > 40:
        print("[Candle+MA+RSI] Señal de COMPRA detectada ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 1.02,
            'sl': last['close'] * 0.98,
            'reason': 'Cruce de EMA con vela fuerte y RSI>40',
            'shares': 100
        }

    # Cruce bajista con RSI alto y vela fuerte
    if strong_candle and prev['ema_fast'] > prev['ema_slow'] and last['ema_fast'] < last['ema_slow'] and last['rsi'] < 60:
        print("[Candle+MA+RSI] Señal de VENTA detectada ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['close'] * 0.98,
            'sl': last['close'] * 1.02,
            'reason': 'Cruce de EMA con vela fuerte y RSI<60',
            'shares': 100
        }

    return None
