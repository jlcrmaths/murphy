# -*- coding: utf-8 -*-
"""
🤖 IBEX Murphy Adaptive Bot — Escaneo completo con recomendador automático.
Evalúa múltiples estrategias y decide si comprar, mantener, vender o no hacer nada.
"""

import pandas as pd
import importlib
import itertools
import random
import time

from data import download_bars
from notifier import send_telegram_message, format_alert
from recommender import decide_action, explain_action

# --- Lista de estrategias activas ---
STRATEGIES = [
    "strategies.murphy",
    "strategies.macd_momentum",
    "strategies.rsi_reversal",
    "strategies.bollinger_rebound",
    "strategies.ema_crossover",
    "strategies.candle_ma_rsi",
    "strategies.candle_sr_volume",
    "strategies.candle_boll_rsi"
]

_cycle = itertools.cycle(STRATEGIES)

# --- Leer tickers desde archivo ---
TICKERS = []
with open("tickers_ibex.txt", "r", encoding="utf-8") as f:
    for line in f:
        ticker = line.strip()
        if ticker and not ticker.startswith("#"):
            TICKERS.append(ticker)

signals_summary = []
failed_tickers = []


def get_next_strategy():
    """Devuelve una estrategia ponderada por rendimiento."""
    try:
        from strategy_performance import get_strategy_scores
        scores = get_strategy_scores()
    except ImportError:
        scores = {}

    if not scores:
        module_name = next(_cycle)
        module = importlib.import_module(module_name)
        return module.generate_signal, module_name.split(".")[-1]

    weights = [scores.get(s.split(".")[-1], 0.5) for s in STRATEGIES]
    module_name = random.choices(STRATEGIES, weights=weights, k=1)[0]
    module = importlib.import_module(module_name)
    print(f"[Adaptive] Estrategia '{module_name.split('.')[-1]}' seleccionada con peso {scores.get(module_name.split('.')[-1], 0.5):.2f}")
    return module.generate_signal, module_name.split(".")[-1]


# --- Escaneo principal ---
for ticker in TICKERS:
    print(f"\n[Info] Escaneando {ticker} ...")
    df = download_bars(ticker)

    if df is None or df.empty:
        print(f"[Advertencia] {ticker}: sin datos recientes, omitido.")
        failed_tickers.append(ticker)
        continue

    ticker_signals = {"ticker": ticker, "signals": []}

    for strategy_path in STRATEGIES:
        module = importlib.import_module(strategy_path)
        try:
            signal = module.generate_signal(df)
            ticker_signals["signals"].append({
                "strategy": strategy_path.split(".")[-1],
                "signal": signal
            })
            print(f"[DEBUG] {ticker} - {strategy_path.split('.')[-1]}: {signal}")
        except Exception as e:
            print(f"[Error] {ticker} - {strategy_path.split('.')[-1]}: {e}")
            ticker_signals["signals"].append({
                "strategy": strategy_path.split(".")[-1],
                "signal": None
            })

    # --- Combinar señales relevantes ---
    valid_signals = [s["signal"] for s in ticker_signals["signals"] if s["signal"]]
    if not valid_signals:
        print(f"[Info] {ticker}: sin señales útiles → sin acción.")
        continue

    # Tomamos la señal más reciente como representativa
    final_signal = max(valid_signals, key=lambda x: x.get("timestamp", "1970-01-01"))
    final_signal["ticker"] = ticker

    # --- Decidir acción ---
    action = decide_action(final_signal, df)
    explanation = explain_action(action)

    # --- Solo enviamos si hay acción relevante ---
    if action != "NONE":
        msg = format_alert(ticker, final_signal)
        send_telegram_message(f"*{action}* → {explanation}\n\n{msg}")
    else:
        print(f"[Info] {ticker}: sin movimiento relevante ({action}).")

    signals_summary.append({
        "ticker": ticker,
        "action": action,
        "explanation": explanation,
        "timestamp": str(final_signal.get("timestamp"))
    })

    time.sleep(0.5)  # evitar rate limit de Yahoo

# --- Guardar resumen local ---
df_summary = pd.DataFrame(signals_summary)
df_summary.to_csv("signals_summary.csv", index=False, encoding="utf-8")
print("\n[Guardado] Archivo signals_summary.csv generado ✅")

# --- Mostrar resumen por consola ---
print("\n[Resumen final]")
for row in signals_summary:
    print(f"{row['ticker']:10s} → {row['action']:10s} | {row['explanation']}")


