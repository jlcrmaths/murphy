# -*- coding: utf-8 -*-
"""
Módulo data.py
--------------
Descarga datos históricos de cotización para los tickers especificados
usando Yahoo Finance (gratuito).

Devuelve un DataFrame con columnas:
['timestamp', 'open', 'high', 'low', 'close', 'volume']
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


def download_bars(ticker: str, days: int = 180, interval: str = "1d") -> pd.DataFrame:
    """
    Descarga los datos de cotización de un ticker usando Yahoo Finance.

    Args:
        ticker (str): Código del valor, por ejemplo 'CABK.MC'.
        days (int): Días de histórico a descargar (por defecto 180).
        interval (str): Intervalo entre datos ('1d', '1h', etc.).

    Returns:
        pd.DataFrame o None: DataFrame con columnas normalizadas o None si hay error.
    """
    try:
        # Descarga datos
        period = f"{days}d"
        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df is None or df.empty:
            print(f"[Advertencia] {ticker}: sin datos descargados.")
            return None

        # Aplana columnas si vienen con MultiIndex (por ejemplo ('Close', ''))
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]

        # Asegura que las columnas principales existan
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col not in df.columns:
                print(f"[Error] {ticker}: falta columna '{col}' en los datos.")
                return None

        # Convierte 'close' (y resto) a 1D si vienen como arrays 2D
        for c in ['open', 'high', 'low', 'close', 'volume']:
            df[c] = df[c].squeeze()

        # Reset index para convertir el índice de fechas en columna 'timestamp'
        df = df.reset_index()
        if 'date' in df.columns:
            df.rename(columns={'date': 'timestamp'}, inplace=True)

        # Solo mantenemos las columnas relevantes
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        # Asegura que 'timestamp' es datetime (y en UTC)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        return df

    except Exception as e:
        print(f"[Error en download_bars] {ticker}: {e}")
        return None


# Ejemplo de prueba rápida
if __name__ == "__main__":
    ticker = "CABK.MC"  # Caixabank
    df = download_bars(ticker)
    if df is not None:
        print(df.head())
    else:
        print(f"No se pudieron obtener datos para {ticker}.")
