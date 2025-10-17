# recommender.py
# -*- coding: utf-8 -*-
"""
🧠 Recommender mejorado con memoria de posiciones
Decide la acción final (BUY, HOLD, SELL, NONE) en función de:
- color final (green/yellow/red)
- tendencia (EMA)
- RSI
- y estado anterior (memoria en positions_state.csv)
"""

import numpy as np
from positions_state import get_last_action, update_action, save_positions

def decide_action(signal: dict, df, positions_df=None) -> str:
    """
    Determina la acción a tomar basándose en la señal combinada, RSI y tendencia.
    Si se proporciona positions_df, consulta el estado previo del ticker.
    """
    ticker = signal.get("ticker", "UNKNOWN")
    color = signal.get("color", "red")
    last_action = get_last_action(ticker, positions_df) if positions_df is not None else "NONE"

    # Calcular RSI y tendencia general
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    trend_up = df["ema_fast"].iloc[-1] > df["ema_slow"].iloc[-1]

    # RSI aproximado (14 periodos)
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = np.where(loss == 0, 0, gain / loss)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = float(rsi[-1]) if not np.isnan(rsi[-1]) else 50.0

    print(f"[Recommender] {ticker}: color={color}, trend={'up' if trend_up else 'down'}, RSI={current_rsi:.2f}, last={last_action}")

    # === Decisiones principales ===
    action = "NONE"

    # 🔹 COMPRAR: color verde o fuerza + tendencia alcista
    if color == "green" and trend_up and current_rsi < 75:
        action = "BUY"

    # 🔹 MANTENER: señales amarillas o sobrecompra leve
    elif color == "yellow" or (70 <= current_rsi < 85 and trend_up):
        action = "HOLD"

    # 🔹 VENDER: RSI alto o cruce bajista
    elif color == "red" and not trend_up and current_rsi > 70:
        # Solo vender si se había comprado antes
        if last_action in ["BUY", "HOLD"]:
            action = "SELL"
        else:
            action = "NONE"  # ignora ventas sin compra previa

    # 🔹 VIGILAR: sobrecompra fuerte pero aún en tendencia
    elif current_rsi >= 85 and trend_up:
        action = "HOLD"

    # 🔹 RECOMPRA inteligente:
    elif last_action in ["HOLD", "SELL"] and color == "green" and trend_up and current_rsi < 65:
        action = "BUY"

    # 🔹 Por defecto
    else:
        action = "NONE"

    return action


def explain_action(action: str) -> str:
    """
    Devuelve una explicación breve y comprensible del motivo de la acción.
    """
    explanations = {
        "BUY": "Tendencia alcista con confirmación de fuerza 📈",
        "HOLD": "Zona de sobrecompra o consolidación — mantener vigilancia ⚠️",
        "SELL": "Señal de agotamiento o cruce bajista detectado 🔻",
        "NONE": "Sin consenso suficiente o mercado lateral ⚪"
    }
    return explanations.get(action, "Sin explicación disponible.")

