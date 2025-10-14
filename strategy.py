# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# === Parámetros (puedes ajustarlos en config.py si lo deseas) ===
EMA_FAST = 12
EMA_SLOW = 26
RSI_LEN = 14
RSI_MAX = 70
RSI_MIN = 30
VOL_AVG_LEN = 20
HIGH_BREAK_LEN = 20
ATR_LEN = 14


def generate_signal(df: pd.DataFrame):
    """
    Estrategia técnica basada en principios de John J. Murphy:
    - Tendencia: cruce EMA rápida / lenta.
    - Momento: RSI.
    - Volumen: confirmación con volumen medio.
    - Precio: ruptura de máximos recientes.
    - Riesgo: ATR para stop-loss y objetivos.
    """

    # Asegurarse de que el DataFrame tenga los datos necesarios
    if df is None or df.empty:
        print("[Debug] DataFrame vacío o None.")
        return None

    # Mantener solo las columnas necesarias
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()

    # Calcular indicadores
    df['ema_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=RSI_LEN).mean()
    avg_loss = pd.Series(loss).rolling(window=RSI_LEN).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    df['vol_avg'] = df['volume'].rolling(window=VOL_AVG_LEN).mean()
    df['max_high_lookback'] = df['high'].shift(1).rolling(window=HIGH_BREAK_LEN).max()
    df['atr'] = (df['high'] - df['low']).rolling(window=ATR_LEN).mean()

    # Requisitos mínimos de datos
    min_len = max(EMA_SLOW * 2, VOL_AVG_LEN + HIGH_BREAK_LEN + RSI_LEN + ATR_LEN)
    if len(df) < min_len:
        print(f"[Debug] Insuficientes datos ({len(df)}/{min_len}).")
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # === Condiciones individuales ===
    trend_up = last['ema_fast'] > last['ema_slow']
    breakout = last['high'] > last['max_high_lookback']
    vol_ok = last['volume'] > last['vol_avg']
    rsi_ok = RSI_MIN < last['rsi'] < RSI_MAX

    # === Depuración detallada ===
    print(f"\n[DEBUG] Evaluando {df.iloc[-1]['timestamp']}")
    print(f"EMA_fast={last['ema_fast']:.3f}, EMA_slow={last['ema_slow']:.3f} → trend_up={trend_up}")
    print(f"High={last['high']:.3f}, Máx_prev={last['max_high_lookback']:.3f} → breakout={breakout}")
    print(f"Vol={last['volume']:.0f}, Vol_avg={last['vol_avg']:.0f} → vol_ok={vol_ok}")
    print(f"RSI={last['rsi']:.2f} → rsi_ok={rsi_ok}")

    # === Condición compuesta ===
    if trend_up and breakout and vol_ok and rsi_ok:
        atr = last['atr']
        entry_price = last['close']
        stop_loss = entry_price - 1.5 * atr
        take_profit = entry_price + 2 * atr
        print("[SIGNAL] Condiciones cumplidas → COMPRA detectada ✅")

        return {
            'timestamp': last['timestamp'],
            'entry': round(entry_price, 3),
            'tp': round(take_profit, 3),
            'sl': round(stop_loss, 3),
            'rsi': round(last['rsi'], 2),
            'ema_fast': round(last['ema_fast'], 3),
            'ema_slow': round(last['ema_slow'], 3),
            'reason': 'Cruce de medias + ruptura con volumen y RSI válido'
        }

    print("[Debug] No se cumple alguna condición → sin señal.\n")
    return None
