# -*- coding: utf-8 -*-
"""
Módulo de recomendación para IBEX Murphy Bot.
Decide la acción óptima (BUY, HOLD, SELL, NONE) basándose en las señales y la tendencia.
"""

import pandas as pd
import numpy as np

def detect_trend(df):
    """
    Detecta tendencia global según medias móviles.
    Devuelve 'up', 'down' o 'flat'.
    """
    if len(df) < 20:
        return "flat"
    
    ema_fast = df['close'].ewm(span=10).mean().iloc[-1]
    ema_slow = df['close'].ewm(span=30).mean().iloc[-1]
    
    if ema_fast > ema_slow * 1.003:  # margen mínimo para evitar ruido
        return "up"
    elif ema_fast < ema_slow * 0.997:
        return "down"
    else:
        return "flat"


def calc_rsi(df, period=14):
    """Calcula RSI clásico."""
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def decide_action(final_signal, df):
    """
    Decide si se debe comprar, mantener, vender o no hacer nada.
    Usa la información de señales y el contexto técnico reciente.
    """
    try:
        color = final_signal.get('color', 'red')
        strategy = final_signal.get('strategy_name', 'unknown')
        ts = final_signal.get('timestamp')
    except Exception:
        return "NONE"

    # === Indicadores técnicos ===
    trend = detect_trend(df)
    rsi = calc_rsi(df)
    
    # === Contadores de señales ===
    color_counts = {'green': 0, 'yellow': 0, 'red': 0}
    if isinstance(color, str):
        color_counts[color] += 1

    # === Decisión principal ===
    action = "NONE"

    if color == "green" and trend == "up" and rsi < 65:
        action = "BUY"
    elif color == "green" and trend != "down" and 65 <= rsi <= 70:
        action = "BUY_LIGHT"
    elif color == "yellow" and trend == "up":
        action = "HOLD"
    elif trend == "down" and (color == "red" or rsi > 70):
        action = "SELL"
    else:
        action = "NONE"

    print(f"[Recommender] {final_signal.get('ticker', '')}: color={color}, trend={trend}, RSI={rsi:.2f} → {action}")
    return action


def explain_action(action):
    """Devuelve una breve explicación textual."""
    explanations = {
        "BUY": "📈 Señales alcistas sólidas. Posible entrada.",
        "BUY_LIGHT": "🟢 Rebote o impulso leve. Entrada especulativa.",
        "HOLD": "⚖️ Mantener posición. El mercado aún no confirma dirección.",
        "SELL": "📉 Señales bajistas detectadas. Riesgo de corrección.",
        "NONE": "😴 Sin señal relevante. No hacer nada."
    }
    return explanations.get(action, "Sin información.")
