# recommender.py
# -*- coding: utf-8 -*-
"""
🧠 Recommender con memoria de posiciones y soporte de cortos
Decide la acción final (BUY, HOLD, SELL, SHORT, COVER, NONE)
en función de:
- color final (green/yellow/red)
- tendencia (EMA)
- RSI
- estado anterior guardado en positions_state.csv
- evita avisos repetidos en Telegram
"""

import numpy as np
from positions_state import get_last_action, update_action, load_positions, should_notify

def decide_action(signal: dict, df, positions_df=None) -> str:
    """
    Determina la acción a tomar basándose en la señal combinada, RSI y tendencia.
    Si se proporciona positions_df, consulta el estado previo del ticker.
    """
    ticker = signal.get("ticker", "UNKNOWN")
    color = signal.get("color", "red")
    last_action = get_last_action(ticker, positions_df) if positions_df is not None else "NONE"

    # Calcular EMA rápida y lenta
    df = df.copy()
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
    trend_up = df["ema_fast"].iloc[-1] > df["ema_slow"].iloc[-1]

    # RSI (14 periodos)
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
    elif color == "yellow" or (70 <= current_rsi < 85 and trend_up):
        if last_action in ["BUY", "HOLD"]:
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

    # ================= RECOMPRA INTELIGENTE =================
    if last_action in ["HOLD", "SELL"] and color == "green" and trend_up and current_rsi < 65:
        action = "BUY"

    return action


def process_signal_and_notify(signal, df, send_func):
    """
    Evalúa la señal, decide acción y envía notificación solo si hay cambio.
    """
    ticker = signal.get("ticker", "UNKNOWN")

    # Cargar posiciones guardadas
    positions_df = load_positions()

    # Decidir nueva acción
    final_action = decide_action(signal, df, positions_df)

    # Si no hay acción o es NONE, no avisamos
    if final_action == "NONE":
        print(f"[Info] {ticker}: sin acción relevante.")
        return

    # Comprobar si debe notificarse (evita avisos repetidos)
    if should_notify(ticker, final_action, positions_df):
        # Guardar nueva acción
        update_action(ticker, final_action, positions_df)

        # Enviar mensaje
        reason = explain_action(final_action)
        msg = f"📊 *{ticker}* → {final_action}\n{reason}"
        print(f"[Notify] {msg}")
        send_func(msg)
    else:
        print(f"[Info] {ticker}: señal '{final_action}' ya notificada previamente.")


def explain_action(action: str) -> str:
    """
    Devuelve una explicación breve y comprensible del motivo de la acción.
    """
    explanations = {
        "BUY": "Tendencia alcista con confirmación de fuerza 📈",
        "HOLD": "Zona de consolidación o sobrecompra — mantener vigilancia ⚠️",
        "SELL": "Cerrar posición larga 🔻",
        "SHORT": "Oportunidad de venta en corto 📉",
        "COVER": "Cerrar posición corta 📊",
        "NONE": "Sin consenso suficiente o mercado lateral ⚪"
    }
    return explanations.get(action, "Sin explicación disponible.")






