# -*- coding: utf-8 -*-
"""
🤖 IBEX Murphy Adaptive Bot — Versión alterna de escaneo
Usa un conjunto diferente de estrategias para combinar señales.
Memoria persistente y filtros idénticos a la versión principal.
"""

import pandas as pd
import importlib
import time
from datetime import datetime

from data import download_bars
from notifier import send_telegram_message, format_alert
from recommender import decide_action, explain_action
from positions_state import load_positions, save_positions, get_last_action, update_action

# === Estrategias alternas ===
STRATEGIES_ALTERNA = [
    "strategies.candle_ma_rsi",
    "strategies.candle_sr_volume",
    "strategies.candle_boll_rsi",
    "strategies.engulfing",
    "strategies.atr_breakout",
    "strategies.bollinger_rebound",
    "strategies.rsi_reversal"
]

PAUSE_SEC = 0.25  # pausa corta entre estrategias

# === Leer tickers desde archivo ===
TICKERS = []
with open("tickers_ibex.txt", "r", encoding="utf-8") as f:
    for line in f:
        t = line.strip()
        if t and not t.startswith("#"):
            TICKERS.append(t)

def combine_signals(signals: list) -> dict:
    """
    Combina señales por consenso.
    Verde = al menos 2 verdes
    Amarillo = 1 verde o alguna amarilla
    Rojo = resto
    """
    if not signals:
        return None

    count_green = sum(1 for s in signals if s and s.get("color") == "green")
    count_yellow = sum(1 for s in signals if s and s.get("color") == "yellow")

    final_color = "red"
    if count_green >= 2:
        final_color = "green"
    elif count_green == 1 or count_yellow >= 1:
        final_color = "yellow"

    valid_signals = [s for s in signals if s and "timestamp" in s]
    if not valid_signals:
        return None

    for s in valid_signals:
        if not isinstance(s["timestamp"], pd.Timestamp):
            s["timestamp"] = pd.Timestamp(s["timestamp"])

    latest = max(valid_signals, key=lambda s: s["timestamp"])
    latest["color"] = final_color
    return latest

# === EJECUCIÓN PRINCIPAL ===
print("=" * 60)
print("🤖 IBEX Murphy Adaptive Bot — Escaneo alterno")
print("=" * 60)

positions_df = load_positions()

for ticker in TICKERS:
    print(f"\n[Info] Escaneando {ticker}...")
    df = download_bars(ticker)
    if df is None or df.empty:
        print(f"[Aviso] {ticker}: sin datos recientes, se omite.")
        continue

    signals = []
    for strat_path in STRATEGIES_ALTERNA:
        try:
            module = importlib.import_module(strat_path)
            signal = module.generate_signal(df)
            if signal:
                signal["strategy_name"] = strat_path.split(".")[-1]
                signals.append(signal)
            print(f"[DEBUG] {ticker} - {signal}")
        except Exception as e:
            print(f"[Error] {ticker} ({strat_path}): {e}")
        time.sleep(PAUSE_SEC)

    final_signal = combine_signals(signals)
    if not final_signal:
        print(f"[Info] {ticker}: sin señales claras.")
        continue

    final_signal["ticker"] = ticker
    action = decide_action(final_signal, df, positions_df)
    last_action = get_last_action(ticker, positions_df)

    # === FILTROS INTELIGENTES ===
    if action == last_action:
        print(f"[Filtro] {ticker}: acción '{action}' repetida → sin aviso.")
        continue

    if action == "SELL" and last_action not in ["BUY", "HOLD"]:
        print(f"[Filtro] {ticker}: SELL ignorado (sin posición previa).")
        continue

    if action == "BUY" and last_action in ["BUY", "HOLD"]:
        print(f"[Filtro] {ticker}: BUY ignorado (ya en posición o seguimiento).")
        continue

    if action == "NONE":
        print(f"[Recommender] {ticker} → ninguna acción tomada.")
        continue

    # === ACTUALIZAR ESTADO ===
    positions_df = update_action(ticker, action, positions_df)
    save_positions(positions_df)

    # === ENVIAR MENSAJE TELEGRAM ===
    explanation = explain_action(action)
    try:
        msg = format_alert(ticker, final_signal)
    except KeyError:
        msg = (
            f"<b>{action}</b> en <b>{ticker}</b><br>"
            f"Hora: <code>{final_signal.get('timestamp', 'N/A')}</code><br>"
            f"Estrategia: <code>{final_signal.get('strategy_name', 'desconocida')}</code>"
        )

    send_telegram_message(f"📊 <b>{action}</b> → {explanation}\n\n{msg}")

print("\n✅ Escaneo alterno completado. Señales enviadas a Telegram (si aplicaba).")
print("=" * 60)
print(f"🕒 Fin de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)






