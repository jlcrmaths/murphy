# advisor.py
# -*- coding: utf-8 -*-
"""
Asistente de decisión para el IBEX Murphy Bot.
Analiza las señales de las estrategias y recomienda: buy / sell / watch / hold.
"""

import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("positions_state.json")

# === Utilidades internas ===

def load_state() -> dict:
    """Carga el estado anterior desde JSON."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[Aviso] Archivo de estado corrupto, se reiniciará.")
    return {}

def save_state(state: dict) -> None:
    """Guarda el estado actualizado."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

# === Núcleo principal ===

def get_recommendation(ticker: str, strategy_signals: dict, prev_state: dict | None = None) -> str:
    """
    Devuelve la acción recomendada según las señales.
    - strategy_signals: dict { estrategia: 'buy' | 'sell' | None }
    - prev_state: dict con estado anterior (si existía)
    """
    n_buy = sum(1 for s in strategy_signals.values() if s == "buy")
    n_sell = sum(1 for s in strategy_signals.values() if s == "sell")

    # Evaluación de consenso actual
    if n_buy >= 3:
        rec = "buy"
    elif n_sell >= 2:
        rec = "sell"
    elif n_buy + n_sell == 0:
        rec = "hold"
    else:
        rec = "watch"

    # Ajuste según estado previo
    if prev_state:
        prev_status = prev_state.get("status")
        if prev_status == "buy" and rec == "sell":
            rec = "close"  # cierre de posición
        elif prev_status == "buy" and rec == "hold":
            rec = "hold"
        elif prev_status == "sell" and rec == "buy":
            rec = "rebound"  # rebote tras caída
    return rec

def update_state(ticker: str, rec: str, last_price: float, state: dict) -> None:
    """Actualiza el estado según la recomendación."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if rec in ("buy", "rebound"):
        state[ticker] = {"status": "buy", "entry_price": last_price, "timestamp": now}
    elif rec in ("sell", "close"):
        state[ticker] = {"status": "sold", "exit_price": last_price, "timestamp": now}
    elif rec == "watch":
        state[ticker] = {"status": "watch", "timestamp": now}
    elif rec == "hold":
        state[ticker] = {"status": "hold", "timestamp": now}

# === Función principal de orquestación ===

def analyze_and_update(ticker: str, strategy_signals: dict, last_price: float) -> str:
    """
    Analiza las señales del ticker, devuelve la recomendación y actualiza el estado global.
    """
    state = load_state()
    prev_state = state.get(ticker)
    rec = get_recommendation(ticker, strategy_signals, prev_state)
    update_state(ticker, rec, last_price, state)
    save_state(state)
    return rec
