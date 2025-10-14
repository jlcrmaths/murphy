# -*- coding: utf-8 -*-
"""
data.py — Descarga de cotizaciones bursátiles desde Yahoo Finance
Compatible con ibex_murphy_bot_github_v5
"""

import yfinance as yf
import pandas as pd

# Puedes ajustar estos valores si lo necesitas
DEFAULT_PERIOD = "6mo"
DEFAULT_INTERVAL = "1d"


def download_bars(ticker: str, period: str = DEFAULT_PERIOD, interval: str = DEFAULT_INTERVAL):
    """
    Descarga los datos históricos de un ticker usando Yahoo Finance.
    Devuelve un DataFrame con columnas: timestamp, open, high, low, close, volume
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df is None or df.empty:
            print(f"[Advertencia] {ticker}: sin datos recientes.")
            return None

        # Si las columnas tienen MultiIndex, las aplanamos
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

        # Convierte la columna 'close' en una Serie 1D (evita el error ndarray)
        df['close'] = df['close'].squeeze()

        # Si no hay índice de fecha, lo añadimos
        if not isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()

        # Creamos la columna timestamp (si no existe)
        if 'timestamp' not in df.columns:
            df = df.rename(columns={'date': 'timestamp'})

        # Nos quedamos solo con las columnas importantes
        cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = df[[c for c in cols if c in df.columns]]

        return df

    except Exception as e:
        print(f"[Error en download_bars] {ticker}: {e}")
        return None


# 🔹 Bloque de prueba directa (solo se ejecuta si lanzas este archivo manualmente)
if __name__ == "__main__":
    tickers = ["CABK.MC", "SAN.MC", "TEF.MC", "REP.MC"]
    for t in tickers:
        print(f"[Info] Descargando {t} ...")
        df = download_bars(t)
        if df is not None:
            print(f"{t}: {len(df)} registros descargados correctamente.")
            print(df.tail(3))  # mostramos las últimas 3 filas
        print("-" * 60)


