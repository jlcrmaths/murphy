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

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# --- Función auxiliar para enviar archivos ---
def send_file_to_telegram(filename: str, caption: str = "📈 Informe de señales IBEX Murphy"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    try:
        with open(filename, "rb") as f:
            files = {"document": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            r = requests.post(url, files=files, data=data, timeout=30)
            if r.status_code != 200:
                print(f"[Telegram] Error al enviar archivo: {r.text}")
            else:
                print(f"[Telegram] Archivo '{filename}' enviado correctamente ✅")
    except Exception as e:
        print(f"[Telegram] Excepción al enviar archivo: {e}")

# --- Función auxiliar para enviar textos largos ---
def send_long_telegram_message(full_text: str):
    """Envía un texto largo en trozos de ≤4000 caracteres."""
    MAX_LEN = 4000
    parts = [full_text[i:i + MAX_LEN] for i in range(0, len(full_text), MAX_LEN)]
    for i, part in enumerate(parts, start=1):
        if len(parts) > 1:
            part += f"\n\n📄 Parte {i}/{len(parts)}"
        send_telegram_message(part)

# --- Mapas de emojis y explicaciones ---
emoji_map = {
    "buy": ("🟢 Comprar", "Tendencia alcista confirmada."),
    "sell": ("🔴 Vender", "Señales bajistas predominantes."),
    "close": ("⛔ Cerrar posición", "Cambio de tendencia tras una compra."),
    "hold": ("⚪ Mantener", "Sin cambios significativos."),
    "watch": ("🟡 En seguimiento", "Señales mixtas, falta confirmación."),
    "rebound": ("🔵 Rebotando", "Posible giro tras una fase bajista.")
}

# --- Crear resumen solo con recomendaciones clave ---
alerts = []
for r in results:
    rec = r["recommendation"]
    if rec in ("buy", "sell", "close", "rebound"):  # filtramos solo señales importantes
        emoji, desc = emoji_map.get(rec, ("❔", ""))
        alerts.append(f"*{r['ticker']}* → {emoji} — {desc} ({r['strategy']})")

# --- Enviar mensaje Telegram resumido ---
if alerts:
    msg = (
        "📊 *IBEX Murphy Advisor — Recomendaciones destacadas*\n\n"
        + "\n".join(alerts)
        + "\n\n💡 _Se adjunta archivo CSV con el informe completo de estrategias._"
    )
    send_long_telegram_message(msg)
    send_file_to_telegram("signals_summary.csv")  # adjunta el informe completo
else:
    print("\n[Info] Sin cambios relevantes — no se envían alertas.")


