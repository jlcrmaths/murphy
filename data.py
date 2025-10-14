# -*- coding: utf-8 -*-
"""
Módulo data.py (versión estable)
--------------------------------
Descarga datos históricos de cotización usando Yahoo Finance (gratuito)
y los devuelve en formato normalizado para el bot.
"""

import pandas as pd
import yfinance as yf


def download_bars(ticker: str, days: int = 180, interval: str = "1d") -> pd.DataFrame:
    """
    Descarga los datos de cotización de un ticker usando Yahoo Finance.

    Args:
        ticker (str): Código del valor, por ejemplo 'CABK.MC'.
        days (int): Días de histórico a descargar (por defecto 180).
        interval (str): Intervalo entre datos ('1d', '1h', etc.).

    Returns:
        pd.DataFrame o None: DataFrame con columnas ['timestamp','open','high','low','close','volume'].
    """
    try:
        period = f"{days}d"
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)

        if df is None or df.empty:
            print(f"[Advertencia] {ticker}: sin datos descargados.")
            return None

        # Aplana columnas si vienen con MultiIndex (por ejemplo ('Close', ''))
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0].lower() for col in df.columns]
        else:
            df.columns = [col.lower() for col in df.columns]

        # Asegura que las columnas principales existan
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                print(f"[Error] {ticker}: falta columna '{col}' en los datos.")
                return None

        # Convierte arrays 2D a Series 1D
        for c in required_cols:
            df[c] = df[c].squeeze()

        # Convertimos el índice a columna si no existe 'date' o 'timestamp'
        if 'date' in df.columns:
            df.rename(columns={'date': 'timestamp'}, inplace=True)
        elif 'datetime' in df.columns:
            df.rename(columns={'datetime': 'timestamp'}, inplace=True)
        else:
            # Si la fecha está en el índice, la convertimos
            df = df.reset_index()
            # Detectamos si la columna se llama "Date" o "Datetime"
            if 'Date' in df.columns:
                df.rename(columns={'Date': 'timestamp'}, inplace=True)
            elif 'Datetime' in df.columns:
                df.rename(columns={'Datetime': 'timestamp'}, inplace=True)
            else:
                # Si no existe ninguna, asumimos que la primera columna es la fecha
                df.rename(columns={df.columns[0]: 'timestamp'}, inplace=True)

        # Normalizamos formato final
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        return df

    except Exception as e:
        print(f"[Error en download_bars] {ticker}: {e}")
        return None


# 🧪 Prueba manual
if __name__ == "__main__":
    ticker = "SAN.MC"  # Banco Santander
    df = download_bars(ticker)
    if df is not None:
        print(df.head())
        print(f"\n{ticker}: {len(df)} registros descargados correctamente.")
    else:
        print(f"No se pudieron obtener datos para {ticker}.")

