# recommender.py adaptado
# -*- coding: utf-8 -*-
import numpy as np
from positions_state import get_last_action

def decide_action(signal: dict, df, positions_df=None) -> str:
    """
    Determina la acción a tomar basándose en la señal combinada, RSI y tendencia.
    Señales amarillas pasan a HOLD aunque no haya acción previa.
    """
    ticker = signal.get("ticker", "UNKNOWN")
    color = signal.get("color", "red")
    last_action = get_last_action(ticker, positions_df) if positions_df is not None else "NONE"

    # EMA rápida y lenta
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    trend_up = df["ema_fast"].iloc[-1] > df["ema_slow"].iloc[-1]

    # RSI aproximado
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = -delta.clip(upper=0).rolling(window=14).mean()
    rs = np.where(loss == 0, 0, gain / loss)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = float(rsi[-1]) if not np.isnan(rsi[-1]) else 50.0

    print(f"[Recommender] {ticker}: color={color}, trend={'up' if trend_up else 'down'}, RSI={current_rsi:.2f}, last={last_action}")

    action = "NONE"

    # ================= LARGO =================
    if color == "green" and trend_up and current_rsi < 75:
        action = "BUY"
    elif color == "yellow":
        # Amarillo → mantener vigilancia, independientemente de la posición anterior
        action = "HOLD"
    elif color == "red" and not trend_up and current_rsi > 70:
        if last_action in ["BUY", "HOLD"]:
            action = "SELL"

    # ================= CORTO =================
    if color == "red" and not trend_up and current_rsi > 30:
        if last_action in ["NONE", "SELL", "COVER"]:
            action = "SHORT"
    if last_action == "SHORT" and color == "green" and trend_up:
        action = "COVER"

    # Recompra inteligente
    if last_action in ["HOLD", "SELL"] and color == "green" and trend_up and current_rsi < 65:
        action = "BUY"

    return action

def explain_action(action: str) -> str:
    explanations = {
        "BUY": "Tendencia alcista con confirmación de fuerza 📈",
        "HOLD": "Zona de consolidación o vigilancia ⚠️",
        "SELL": "Cerrar posición larga 🔻",
        "SHORT": "Oportunidad de venta en corto 📉",
        "COVER": "Cerrar posición corta 📊",
        "NONE": "Sin consenso suficiente o mercado lateral ⚪"
    }
    return explanations.get(action, "Sin explicación disponible.")




