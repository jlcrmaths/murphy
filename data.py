# -*- coding: utf-8 -*-
"""
📈 Funciones de descarga de datos para el bot
"""

import yfinance as yf
import pandas as pd

def download_bars(ticker: str, period='3mo', interval='1d') -> pd.DataFrame:
    """
    Descarga barras históricas para un ticker.
    Retorna DataFrame con columnas: ['open','high','low','close','volume']
    Siempre aplanando MultiIndex si existe.
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df.empty:
            return None

        # Normalizar nombres de columna
        df = df.rename(columns=str.lower)  # lowercase
        expected_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in expected_cols):
            # Caso MultiIndex
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0].lower() for col in df.columns]
            df = df[expected_cols]

        df = df.dropna()
        return df

    except Exception as e:
        print(f"[Error en download_bars] {ticker}: {e}")
        return None






