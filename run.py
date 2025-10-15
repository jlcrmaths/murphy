# run.py
import warnings
import yfinance as yf
import pandas as pd
from data import download_bars  # tu función corregida

# Ignorar FutureWarnings de yfinance
warnings.simplefilter(action='ignore', category=FutureWarning)

# Lista de tickers a escanear
tickers = [
    "AAPL", "MSFT", "GOOG", "CABK.MC", "SAB.MC", "CLEOP.MC", "OLE.MC", "MDF.MC",
    "ECOENER.MC", "EDR.MC", "AENA.MC"
]

failed_tickers = []

for ticker in tickers:
    try:
        df = download_bars(ticker)
        if df is None or df.empty:
            print(f"[Info] {ticker} omitido por falta de datos.")
            failed_tickers.append(ticker)
            continue

        # Validar columnas mínimas antes de cálculos
        required_cols = ["close", "open", "high", "low", "volume"]
        if not all(col in df.columns for col in required_cols):
            print(f"[Info] {ticker}: columnas insuficientes para indicadores.")
            failed_tickers.append(ticker)
            continue

        # --- Ejemplo: cálculo simple de EMA y RSI ---
        df["EMA_fast"] = df["close"].ewm(span=9, adjust=False).mean()
        df["EMA_slow"] = df["close"].ewm(span=21, adjust=False).mean()
        delta = df["close"].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        avg_gain = up.rolling(14).mean()
        avg_loss = down.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # --- Evaluación de condiciones (ejemplo) ---
        latest = df.iloc[-1]
        trend_up = latest["EMA_fast"] > latest["EMA_slow"]
        rsi_ok = 30 < latest["RSI"] < 70

        if trend_up and rsi_ok:
            print(f"[Señal] {ticker}: condiciones OK para posible compra ✅")
        else:
            print(f"[Debug] {ticker}: sin señal.")

    except Exception as e:
        print(f"[Error] {ticker}: {e}")
        failed_tickers.append(ticker)
        continue

# --- Resumen de tickers fallidos ---
if failed_tickers:
    print("\n[Resumen] Tickers que fallaron o se omitieron:")
    for t in failed_tickers:
        print(f" - {t}")
else:
    print("\n[Resumen] Todos los tickers procesados correctamente.")










