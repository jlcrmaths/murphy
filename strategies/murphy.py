# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

EMA_FAST = 12
EMA_SLOW = 26
RSI_LEN = 14
RSI_MAX = 70
RSI_MIN = 30
VOL_AVG_LEN = 20
HIGH_BREAK_LEN = 20
ATR_LEN = 14
CAPITAL_TOTAL = 10000
RIESGO_POR_OPERACION = 0.01

def generate_signal(df: pd.DataFrame):
    if df is None or df.empty:
        return None

    df = df[['timestamp','open','high','low','close','volume']].copy()
    df['ema_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
    delta = df['close'].diff()
    gain = np.where(delta>0, delta,0)
    loss = np.where(delta<0, -delta,0)
    avg_gain = pd.Series(gain).rolling(window=RSI_LEN).mean()
    avg_loss = pd.Series(loss).rolling(window=RSI_LEN).mean()
    rs = avg_gain/avg_loss
    df['rsi'] = 100-(100/(1+rs))
    df['vol_avg'] = df['volume'].rolling(window=VOL_AVG_LEN).mean()
    df['max_high_lookback'] = df['high'].shift(1).rolling(window=HIGH_BREAK_LEN).max()
    df['atr'] = (df['high']-df['low']).rolling(window=ATR_LEN).mean()

    min_len = max(EMA_SLOW*2, VOL_AVG_LEN+HIGH_BREAK_LEN+RSI_LEN+ATR_LEN)
    if len(df)<min_len:
        return None

    last = df.iloc[-1]
    trend_up = last['ema_fast']>last['ema_slow']
    breakout = last['high']>last['max_high_lookback']
    vol_ok = last['volume']>last['vol_avg']
    rsi_ok = RSI_MIN<last['rsi']<RSI_MAX

    if trend_up and breakout and vol_ok and rsi_ok:
        entry_price = last['close']
        atr = last['atr']
        stop_loss = entry_price-1.5*atr
        take_profit = entry_price+2*atr
        riesgo_por_accion = entry_price-stop_loss
        capital_riesgo = CAPITAL_TOTAL*RIESGO_POR_OPERACION
        shares = int(capital_riesgo/ riesgo_por_accion)
        print("[Murphy] Condiciones cumplidas → COMPRA ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': round(entry_price,3),
            'tp': round(take_profit,3),
            'sl': round(stop_loss,3),
            'rsi': round(last['rsi'],2),
            'ema_fast': round(last['ema_fast'],3),
            'ema_slow': round(last['ema_slow'],3),
            'reason':'Cruce de medias + ruptura con volumen y RSI válido',
            'shares':shares,
            'risk_per_share':round(riesgo_por_accion,3)
        }
    return None
