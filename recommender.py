# -*- coding: utf-8 -*-
"""
Recommender mejorado con soporte para posiciones cortas.
Decide acción final basada en:
- color final (green/yellow/red)
- tendencia EMA
- RSI
- estado anterior (memoria positions_state.csv)
"""

import numpy as np
from positions_state import get_last_action, update_action, save_positions

def decide_action(signal: dict, df, positions_df=None) -> str:
    """
    Determina la acción a tomar:
    - BUY / SELL para posiciones largas
    - SHORT / COVER para posiciones cortas
    - HOLD / NONE si no hay consenso
    """
    ticker = signal.get("ticker", "UNKNOWN")
    color = signal.get("color", "red")
    last_action = get_last_action(ticker, positions_df) if positions_df is not None else "NONE"

    # EMA
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    trend_up = df["ema_fast"].iloc[-1] > df["ema_slow"].iloc[-1]

    # RSI aproximado (14)
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = np.where(loss == 0, 0, gain / loss)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = float(rsi[-1]) if not np.isnan(rsi[-1]) else 50.0

    print(f"[RecommenderShort] {ticker}: color={color}, trend={'up' if trend_up else 'down'}, RSI={current_rsi:.2f}, last={last_action}")

    action = "NONE"

    # === LARGO ===
    if color == "green" and trend_up and current_rsi < 75:
        action = "BUY"
    elif color == "yellow" or (70 <= current_rsi < 85 and trend_up):
        action = "HOLD"
    elif color == "red" and not trend_up and current_rsi > 70:
        if last_action in ["BUY", "HOLD"]:
            action = "SELL"
        else:
            # oportunidad de corto
            if current_rsi > 70 and not trend_up:
                action = "SHORT"

    # Recompra / cierre corto
    if last_action == "SHORT":
        if color == "green" and trend_up:
            action = "COVER"  # cerrar corto y posible largo
        elif current_rsi < 30:
            action = "COVER"

    # Evitar señales sin consenso
    if action not in ["BUY", "SELL", "SHORT", "COVER"]:
        action = "NONE"

    return action

def explain_action(action: str) -> str:
    explanations = {
        "BUY": "Tendencia alcista confirmada 📈",
        "HOLD": "Zona de consolidación o sobrecompra leve ⚠️",
        "SELL": "Cerrar posición larga 🔻",
        "SHORT": "Abrir posición corta ⬇️",
        "COVER": "Cerrar posición corta ⬆️",
        "NONE": "Sin consenso suficiente ⚪"
    }
    return explanations.get(action, "Sin explicación disponible.")


