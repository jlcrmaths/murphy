# -*- coding: utf-8 -*-
"""
Módulo: data.py
Descarga de datos bursátiles desde Yahoo Finance con control de errores.
Compatible con MultiIndex y estructura estándar del bot Murphy.
"""

import yfinance as yf
import pandas as pd

FAILED_TICKERS = set()  # Lista negra temporal para símbolos que fallan


def download_bars(ticker: str, period: str = "12mo", interval: str = "1d") -> pd.DataFrame:
    """Descarga los datos de Yahoo Finance con manejo seguro de errores."""
    if ticker in FAILED_TICKERS:
        print(f"[Info] {ticker}: previamente falló, omitido.")
        return pd.DataFrame()

    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False  # explícito para evitar warnings
        )

        if df is None or df.empty:
            print(f"[Advertencia] {ticker}: sin datos o símbolo no válido.")
            FAILED_TICKERS.add(ticker)
            return pd.DataFrame()

        # Reiniciar índice y normalizar nombres de columnas
        df = df.reset_index()
        df.rename(columns=lambda x: x.lower(), inplace=True)
        df.rename(columns={"date": "timestamp"}, inplace=True)

        # Eliminar duplicados y filas sin cierre válido
        if 'close' in df.columns:
            df.dropna(subset=['close'], inplace=True)
        else:
            print(f"[Error] {ticker}: columna 'close' no encontrada en columnas {list(df.columns)}")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"[Error en download_bars] {ticker}: {e}")
        FAILED_TICKERS.add(ticker)
        return pd.DataFrame()





