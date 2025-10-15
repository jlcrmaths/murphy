# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# === Parámetros técnicos ===
EMA_FAST = 12
EMA_SLOW = 26
RSI_LEN = 14
RSI_MAX = 70
RSI_MIN = 30
VOL_AVG_LEN = 20
HIGH_BREAK_LEN = 20
ATR_LEN = 14

# === Parámetros de gestión del riesgo ===
CAPITAL_TOTAL = 10000        # Capital simulado total
RIESGO_POR_OPERACION = 0.01  # 1% del capital por operación


def generate_signal(df: pd.DataFrame):
    """
    Estrategia técnica avanzada inspirada en John J. Murphy.
    Combina:
      - Cruce de medias exponenciales (EMA)
      - RSI (fuerza relativa)
      - Volumen medio
      - Ruptura de máximos recientes
      - ATR para calcular stop-loss y take profit
      - Gestión del riesgo (cálculo de número de acciones)
    """

    if df is None or df.empty:
        print("[Debug] DataFrame vacío o None.")
        return None

    # === Cálculo de indicadores ===
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()

    # EMAs
    df['ema_fast'] = df['close'].ewm(span=EMA_FAST, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=EMA_SLOW, adjust=False).mean()

    # RSI
    delta = df['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=RSI_LEN).mean()
    avg_loss = pd.Series(loss).rolling(window=RSI_LEN).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Volumen medio
    df['vol_avg'] = df['volume'].rolling(window=VOL_AVG_LEN).mean()

    # Máximos previos
    df['max_high_lookback'] = df['high'].shift(1).rolling(window=HIGH_BREAK_LEN).max()

    # ATR (promedio del rango verdadero)
    df['atr'] = (df['high'] - df['low']).rolling(window=ATR_LEN).mean()

    # Comprobación mínima de longitud
    min_len = max(EMA_SLOW * 2, VOL_AVG_LEN + HIGH_BREAK_LEN + RSI_LEN + ATR_LEN)
    if len(df) < min_len:
        print(f"[Debug] Insuficientes datos ({len(df)}/{min_len}).")
        return None

    last = df.iloc[-1]

    # === Condiciones individuales ===
    trend_up = last['ema_fast'] > last['ema_slow']
    breakout = last['high'] > last['max_high_lookback']
    vol_ok = last['volume'] > last['vol_avg']
    rsi_ok = RSI_MIN < last['rsi'] < RSI_MAX

    # === Depuración detallada ===
    print(f"\n[DEBUG] Evaluando {last['timestamp']}")
    print(f"EMA_fast={last['ema_fast']:.3f}, EMA_slow={last['ema_slow']:.3f} → trend_up={trend_up}")
    print(f"High={last['high']:.3f}, Máx_prev={last['max_high_lookback']:.3f} → breakout={breakout}")
    print(f"Vol={last['volume']:.0f}, Vol_avg={last['vol_avg']:.0f} → vol_ok={vol_ok}")
    print(f"RSI={last['rsi']:.2f} → rsi_ok={rsi_ok}")

    # === Señal de compra (todas las condiciones cumplidas) ===
    if trend_up and breakout and vol_ok and rsi_ok:
        entry_price = last['close']
        atr = last['atr']

        stop_loss = entry_price - 1.5 * atr
        take_profit = entry_price + 2 * atr

        # Gestión del riesgo → número de acciones
        riesgo_por_accion = entry_price - stop_loss
        if riesgo_por_accion <= 0:
            print("[Debug] ATR inválido, riesgo_por_accion <= 0")
            return None

        capital_riesgo = CAPITAL_TOTAL * RIESGO_POR_OPERACION
        shares = int(capital_riesgo / riesgo_por_accion)

        print("[SIGNAL] Condiciones cumplidas → COMPRA detectada ✅")
        print(f"[INFO] Entry={entry_price:.3f}, Stop={stop_loss:.3f}, TP={take_profit:.3f}, Shares={shares}")

        return {
            'timestamp': last['timestamp'],
            'entry': round(entry_price, 3),
            'tp': round(take_profit, 3),
            'sl': round(stop_loss, 3),
            'rsi': round(last['rsi'], 2),
            'ema_fast': round(last['ema_fast'], 3),
            'ema_slow': round(last['ema_slow'], 3),
            'reason': 'Cruce de medias + ruptura con volumen y RSI válido',
            'shares': shares,
            'risk_per_share': round(riesgo_por_accion, 3)
        }

    print("[Debug] No se cumple alguna condición → sin señal.\n")
    return None
