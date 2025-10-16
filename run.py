# -*- coding: utf-8 -*-
"""
🤖 IBEX Murphy Adaptive Bot — Versión con recomendaciones automáticas
"""
import pandas as pd
import importlib
import time
from data import download_bars
from notifier import send_telegram_message, format_alert
from recommender import decide_action, explain_action

# === Estrategias registradas ===
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

PAUSE_SEC = 0.35

# === Leer tickers ===
TICKERS = []
with open("tickers_ibex.txt", "r", encoding="utf-8") as f:
    for line in f:
        t = line.strip()
        if t and not t.startswith("#"):
            TICKERS.append(t)

signals_summary = []

def combine_signals(signals: list) -> dict:
    """
    Combina señales de varias estrategias por mayoría.
    - Verde si al menos 2 dan green
    - Amarillo si 1 da green o yellow
    - Rojo si ninguna
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

    latest = max(signals, key=lambda s: s.get("timestamp", "1970-01-01"))
    latest["color"] = final_color
    return latest

# === Ejecución principal ===
for ticker in TICKERS:
    print(f"\n[Info] Escaneando {ticker} ...")
    df = download_bars(ticker)
    if df is None or df.empty:
        print(f"[Advertencia] {ticker}: sin datos recientes, omitido.")
        continue

    ticker_signals = []

    for strat_path in STRATEGIES:
        module = importlib.import_module(strat_path)
        try:
            signal = module.generate_signal(df)
            if signal:
                signal["strategy_name"] = strat_path.split(".")[-1]
                ticker_signals.append(signal)
            print(f"[DEBUG] {ticker} - {strat_path.split('.')[-1]}: {signal}")
        except Exception as e:
            print(f"[Error] {ticker} - {strat_path}: {e}")

        time.sleep(PAUSE_SEC)

    final_signal = combine_signals(ticker_signals)
    if not final_signal:
        print(f"[Info] {ticker}: sin señales relevantes.")
        continue

    # === Recomendador ===
    final_signal["ticker"] = ticker
    action = decide_action(final_signal, df)

    if action == "NONE":
        print(f"[Recommender] {ticker} → ninguna acción tomada.")
        continue

    explanation = explain_action(action)

    # === Mensaje seguro (sin KeyError) ===
    try:
        msg = format_alert(ticker, final_signal)
    except KeyError:
        # Si falta algún campo, construimos un mensaje simplificado
        msg = (
            f"*{action}* en *{ticker}*\n"
            f"Hora: `{final_signal.get('timestamp', 'N/A')}`\n"
            f"Estrategia: `{final_signal.get('strategy_name', 'desconocida')}`\n"
        )

    send_telegram_message(f"📊 *{action}* → {explanation}\n\n{msg}")

print("\n✅ Escaneo finalizado. Resultados enviados a Telegram (si aplicaba).")



