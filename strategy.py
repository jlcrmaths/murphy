# -*- coding: utf-8 -*-
import math
import pandas as pd
import numpy as np
from config import (
    EMA_FAST, EMA_SLOW, RSI_LEN, RSI_MIN, RSI_MAX,
    HIGH_BREAK_LEN, VOL_AVG_LEN, ATR_LEN, ATR_MULT_SL, RR,
    BUDGET, MAX_RISK_FRACTION
)

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()

def rsi(series: pd.Series, length: int) -> pd.Series:
    delta = series.diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up, index=series.index).ewm(alpha=1/length, adjust=False).mean()
    roll_down = pd.Series(down, index=series.index).ewm(alpha=1/length, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, length: int) -> pd.Series:
    high, low, close = df['high'], df['low'], df['close']
    prev_close = close.shift(1)
    tr = pd.concat([(high-low), (high-prev_close).abs(), (low-prev_close).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1/length, adjust=False).mean()

def generate_signal(df: pd.DataFrame):
    # Validación: asegúrate de suficientes velas
    min_len = max(EMA_SLOW*2, VOL_AVG_LEN+HIGH_BREAK_LEN+RSI_LEN+ATR_LEN)
    if len(df) < min_len:
        return None

    df = df.copy()
    df['ema_fast'] = ema(df['close'], EMA_FAST)
    df['ema_slow'] = ema(df['close'], EMA_SLOW)
    df['rsi'] = rsi(df['close'], RSI_LEN)
    df['vol_avg'] = df['volume'].rolling(VOL_AVG_LEN).mean()
    df['atr'] = atr(df, ATR_LEN)
    df['max_high_lookback'] = df['high'].rolling(HIGH_BREAK_LEN).max().shift(1)

    df['trend_up'] = (df['ema_fast'] > df['ema_slow']) & (df['ema_fast'].shift(1) <= df['ema_slow'].shift(1))
    df['breakout'] = df['close'] > df['max_high_lookback']
    df['vol_ok'] = df['volume'] > df['vol_avg']
    df['rsi_ok'] = (df['rsi'] >= RSI_MIN) & (df['rsi'] <= RSI_MAX)

    df['entry_cond'] = df[['trend_up','breakout','vol_ok','rsi_ok']].all(axis=1)

    last_idx = df.index[-1]
    if not bool(df.loc[last_idx, 'entry_cond']):
        return None

    entry = float(df.loc[last_idx, 'close'])
    atr_val = float(df.loc[last_idx, 'atr'])

    sl = round(entry - ATR_MULT_SL * atr_val, 4)
    risk_per_share = max(entry - sl, 0.0001)
    tp = round(entry + RR * risk_per_share, 4)

    shares_by_budget = int(BUDGET // entry)
    risk_eur = BUDGET * MAX_RISK_FRACTION
    shares_by_risk = int(risk_eur // risk_per_share) if risk_per_share > 0 else 0
    shares = min(shares_by_budget, shares_by_risk) if shares_by_risk > 0 else shares_by_budget

    return {
        'timestamp': str(last_idx),
        'entry': round(entry, 4),
        'tp': tp,
        'sl': sl,
        'shares': int(shares),
        'risk_per_share': round(risk_per_share, 4)
    }
