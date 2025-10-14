# -*- coding: utf-8 -*-
"""
data.py — Descarga y normalización de cotizaciones desde Yahoo Finance
Compatible con ibex_murphy_bot_github_v5
"""

import yfinance as yf
import pandas as pd


DEFAULT_PERIOD = "6mo"
DEFAULT_INTERVAL = "1d"


def download_bars(ticker: str, period: str = DEFAULT_PERIOD, interval: str = DEFAULT_INTERVAL):
    """
    Descarga los datos históricos de un ticker usando Yahoo Finance.
    Devuelve un DataFrame con columnas: timestamp, open, high, low, close, volume.
    """
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)

        if df is None or df.empty:
            print(f"[Advertencia] {ticker}: sin datos recientes.")
            return None

        # 🔹 Aplana las columnas si hay MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [f"{a}_{b}".strip().lower() for a, b in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

        # 🔹 Localiza columnas posibles
        candidates = {
            "open": [c for c in df.columns if "open" in c],
            "high": [c for c in df.columns if "high" in c],
            "low": [c for c in df.columns if "low" in c],
            "close": [c for c in df.columns if "close" in c or "adjclose" in c],
            "volume": [c for c in df.columns if "volume" in c],
        }

        # 🔹 Renombra y selecciona las columnas clave
        df_final = pd.DataFrame()
        df_final["timestamp"] = df.index
        for key, names in candidates.items():
            if names:
                df_final[key] = df[names[0]].astype(float)
            else:
                df_final[key] = None

        # 🔹 Elimina filas con datos faltantes
        df_final = df_final.dropna(subset=["close"])

        return df_final

    except Exception as e:
        print(f"[Error en download_bars] {ticker}: {e}")
        return None


# 🔹 Bloque de prueba manual
if __name__ == "__main__":
    tickers = ["CABK.MC", "SAN.MC", "TEF.MC", "REP.MC"]
    for t in tickers:
        print(f"\n[Info] Descargando {t} ...")
        df = download_bars(t)
        if df is not None and not df.empty:
            print(f"{t}: {len(df)} registros descargados correctamente.")
            print(df.tail(3))
        else:
            print(f"[Advertencia] {t}: sin datos o DataFrame vacío.")
        print("-" * 60)



