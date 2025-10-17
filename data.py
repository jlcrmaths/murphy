# -*- coding: utf-8 -*-
import warnings
import yfinance as yf
import pandas as pd

# Ignorar warnings de futuro para YFinance
warnings.simplefilter(action='ignore', category=FutureWarning)

def download_data(tickers, period="6mo", interval="1d", auto_adjust=True):
    """
    Descarga los datos históricos de Yahoo Finance para una lista de tickers.
    
    :param tickers: Lista de símbolos (ej: ["AAPL", "MSFT"])
    :param period: Período de descarga (ej: "6mo", "1y")
    :param interval: Intervalo de datos (ej: "1d", "1h")
    :param auto_adjust: True para precios ajustados, False para precios originales
    :return: Diccionario con DataFrames por ticker
    """
    if isinstance(tickers, str):
        tickers = [tickers]
    
    # Descargar todos los tickers en paralelo
    df_all = yf.download(
        tickers,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=auto_adjust,
        threads=True
    )
    
    # Si solo es un ticker, yfinance devuelve un DataFrame simple
    data_dict = {}
    if len(tickers) == 1:
        data_dict[tickers[0]] = df_all.reset_index()
    else:
        # Para varios tickers, separar cada uno
        for ticker in tickers:
            if ticker in df_all.columns.levels[0]:
                df_ticker = df_all[ticker].reset_index()
                data_dict[ticker] = df_ticker

    return data_dict

# Ejemplo de uso
if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOG"]
    data = download_data(tickers, period="3mo", interval="1d", auto_adjust=True)
    for t, df in data.items():
        print(f"{t} -> {len(df)} filas")







