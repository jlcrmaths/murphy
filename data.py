# data.py
# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance")

import yfinance as yf
import pandas as pd
import os

DATA_FOLDER = "data_cache"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def download_bars(ticker, period="12mo", interval="1d", use_cache=True):
    """
    Descarga datos históricos de Yahoo Finance para un ticker.
    Guarda y reutiliza archivos locales para acelerar ejecuciones posteriores.
    Devuelve un DataFrame con columnas:
    ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    """
    file_path = os.path.join(DATA_FOLDER, f"{ticker}.csv")

    # --- Usar cache si existe ---
    if use_cache and os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=['timestamp'])
        print(f"[Info] Cargando datos de {ticker} desde cache ✅")
        return df

    print(f"[Info] Descargando datos para {ticker}...")

    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    except Exception as e:
        print(f"[Error] {ticker}: fallo en descarga ({e})")
        return None

    if df.empty:
        print(f"[Advertencia] {ticker}: sin datos recientes.")
        return None

    # --- Aplanar MultiIndex si existiera ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{a}_{b}".strip().lower() for a, b in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    # --- Renombrar columnas ---
    rename_map = {}
    for c in df.columns:
        if "open" in c: rename_map[c] = "open"
        elif "high" in c: rename_map[c] = "high"
        elif "low" in c: rename_map[c] = "low"
        elif "close" in c: rename_map[c] = "close"
        elif "volume" in c: rename_map[c] = "volume"
    df = df.rename(columns=rename_map)

    # --- Añadir columna timestamp ---
    df["timestamp"] = df.index
    df = df.reset_index(drop=True)

    # --- Seleccionar columnas útiles ---
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = df[[c for c in cols if c in df.columns]]

    # --- Guardar cache ---
    df.to_csv(file_path, index=False)
    print(f"[Info] Datos de {ticker} guardados en cache ✅")

    return df







