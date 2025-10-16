# -*- coding: utf-8 -*-
"""
🤖 IBEX Murphy Adaptive Bot — versión con interpretación de señales y recomendaciones
"""

import pandas as pd
import importlib
import itertools
import random
import time
from data import download_bars
from notifier import send_telegram_message
from advisor import analyze_and_update

# --- Estrategias disponibles ---
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

# --- Escaneo principal ---
for ticker in TICKERS:
    print(f"\n[Info] Escaneando {ticker} ...")
    df = download_bars(ticker)
    
    if df is None or df.empty or "close" not in df.columns:
        print(f"[Advertencia] {ticker}: sin datos válidos, omitido.")
        failed_tickers.append(ticker)
        continue

    last_close = float(df["close"].iloc[-1])
    strategy_signals = {}

    for strategy_path in STRATEGIES:
        module = importlib.import_module(strategy_path)
        strategy_name = strategy_path.split(".")[-1]
        try:
            signal = module.generate_signal(df)
            if signal:
                # Si detecta señal de compra o venta
                if signal.get("type") == "buy":
                    strategy_signals[strategy_name] = "buy"
                elif signal.get("type") == "sell":
                    strategy_signals[strategy_name] = "sell"
                else:
                    strategy_signals[strategy_name] = None
            else:
                strategy_signals[strategy_name] = None

            print(f"[DEBUG] {ticker} - {strategy_name}: {strategy_signals[strategy_name]}")

        except Exception as e:
            print(f"[Error] {ticker} - {strategy_name}: {e}")
            strategy_signals[strategy_name] = None
        finally:
            time.sleep(0.2)

    # --- Obtener recomendación global del asesor ---
    recommendation = analyze_and_update(ticker, strategy_signals, last_close)
    print(f"[Recomendación] {ticker} → {recommendation.upper()}")

    # --- Guardar resultado para resumen ---
    signals_summary.append({
        "ticker": ticker,
        "price": last_close,
        "signals": strategy_signals,
        "recommendation": recommendation
    })

# --- Crear CSV resumen ---
results = []
for t in signals_summary:
    for strat, sig in t["signals"].items():
        results.append({
            "ticker": t["ticker"],
            "price": t["price"],
            "strategy": strat,
            "signal": sig,
            "recommendation": t["recommendation"]
        })

df_summary = pd.DataFrame(results)
df_summary.to_csv("signals_summary.csv", index=False)
print("\n[Guardado] Archivo signals_summary.csv generado ✅")

# --- Enviar alertas por Telegram solo si hay cambios relevantes ---

# --- Enviar alertas por Telegram solo si hay cambios relevantes ---
emoji_map = {
    "buy": ("🟢 Comprar", "Tendencia alcista confirmada."),
    "sell": ("🔴 Vender", "Señales bajistas predominantes."),
    "close": ("⛔ Cerrar posición", "Señal contraria detectada tras una compra."),
    "hold": ("⚪ Mantener", "Sin cambios significativos."),
    "watch": ("🟡 En seguimiento", "Señales mixtas o falta de confirmación."),
    "rebound": ("🔵 Rebotando", "Posible giro tras una fase bajista.")
}

alerts = []
for r in results:
    rec = r["recommendation"]
    if rec in emoji_map:
        emoji, desc = emoji_map[rec]
        alerts.append(f"*{r['ticker']}* → {emoji} — {desc} ({r['strategy']})")

if alerts:
    msg = (
        "📊 *IBEX Murphy Advisor — Recomendaciones actualizadas*\n\n"
        + "\n".join(alerts)
        + "\n\n💡 _Estas recomendaciones se basan en consenso técnico entre estrategias._"
    )
    send_telegram_message(msg)
else:
    print("\n[Info] Sin cambios relevantes — no se envían alertas.")

