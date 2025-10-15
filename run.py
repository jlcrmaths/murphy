# run.py
# -*- coding: utf-8 -*-
import pandas as pd
from data import download_bars
import importlib
import itertools
import random

# --- Lista de 8 estrategias ---
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
        if ticker:
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
    print(f"[Info] Escaneando {ticker} ...")
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
            print(f"[DEBUG] {ticker} - {strategy_path.split('.')[-1]} -> {signal}")
        except Exception as e:
            print(f"[Error] {ticker} - {strategy_path.split('.')[-1]}: {e}")
            ticker_signals["signals"].append({
                "strategy": strategy_path.split(".")[-1],
                "signal": None
            })

    signals_summary.append(ticker_signals)

# --- Resumen final ---
print("\n[Resumen] Señales obtenidas:")
for t in signals_summary:
    print(f"{t['ticker']}:")
    for s in t["signals"]:
        print(f"  {s['strategy']}: {s['signal']}")

if failed_tickers:
    print("\n[Resumen] Tickers fallidos u omitidos:")
    for t in failed_tickers:
        print(f" - {t}")














