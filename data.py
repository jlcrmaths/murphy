# data.py
import yfinance as yf
import pandas as pd

def download_bars(ticker: str, period='5d', interval='30m'):
    """
    Descarga datos recientes del ticker especificado desde Yahoo Finance.
    Devuelve un DataFrame con columnas: open, high, low, close, volume.
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df is None or df.empty:
            print(f"[Advertencia] Sin datos para {ticker}")
            return None

        # Renombrar columnas a minúsculas
        df = df.rename(columns=str.lower)

        # Aplanar columnas si vienen como arrays 2D (para evitar el error)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns and df[col].ndim > 1:
                df[col] = df[col].squeeze()

        # Asegurar que sean numéricas
        df = df.apply(pd.to_numeric, errors='coerce')

        return df.dropna()

    except Exception as e:
        print(f"[Error descarga] {ticker}: {e}")
        return None
