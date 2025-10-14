# data.py
import yfinance as yf
import pandas as pd

def download_bars(ticker, period="6mo", interval="1d"):
    print(f"[Info] Descargando datos para {ticker}...")

    df = yf.download(ticker, period=period, interval=interval, progress=False)

    if df.empty:
        print(f"[Advertencia] {ticker}: sin datos recientes.")
        return None

    # --- 🔧 Aplanar columnas si vienen con MultiIndex ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{a}_{b}".strip().lower() for a, b in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    # --- 🔧 Renombrar columnas a un formato uniforme ---
    rename_map = {}
    for c in df.columns:
        if "open" in c: rename_map[c] = "open"
        elif "high" in c: rename_map[c] = "high"
        elif "low" in c: rename_map[c] = "low"
        elif "close" in c: rename_map[c] = "close"
        elif "volume" in c: rename_map[c] = "volume"
    df = df.rename(columns=rename_map)

    # --- 🔧 Añadir columna de timestamp ---
    df["timestamp"] = df.index
    df = df.reset_index(drop=True)

    # --- 🔧 Seleccionar solo las columnas útiles ---
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = df[[c for c in cols if c in df.columns]]

    return df




