# positions_state.py
# -*- coding: utf-8 -*-
"""
Gestiona el estado actual de cada ticker (BUY, HOLD, SELL, NONE)
para evitar señales incoherentes (por ejemplo, vender sin haber comprado).
"""

import os
import pandas as pd
from datetime import datetime

STATE_FILE = "positions_state.csv"

# === Cargar estado actual ===
def load_positions() -> pd.DataFrame:
    if os.path.exists(STATE_FILE):
        try:
            df = pd.read_csv(STATE_FILE)
            if not {"ticker", "last_action", "last_timestamp"}.issubset(df.columns):
                raise ValueError("Archivo positions_state.csv con formato incorrecto.")
            return df
        except Exception:
            pass
    # Crear DataFrame vacío si no existe
    return pd.DataFrame(columns=["ticker", "last_action", "last_timestamp"])

# === Guardar estado ===
def save_positions(df: pd.DataFrame):
    df.to_csv(STATE_FILE, index=False)

# === Consultar última acción ===
def get_last_action(ticker: str, df: pd.DataFrame) -> str:
    row = df[df["ticker"] == ticker]
    if not row.empty:
        return row.iloc[0]["last_action"]
    return "NONE"

# === Actualizar acción ===
def update_action(ticker: str, action: str, df: pd.DataFrame) -> pd.DataFrame:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if ticker in df["ticker"].values:
        df.loc[df["ticker"] == ticker, ["last_action", "last_timestamp"]] = [action, now]
    else:
        df = pd.concat([df, pd.DataFrame([{
            "ticker": ticker,
            "last_action": action,
            "last_timestamp": now
        }])], ignore_index=True)
    return df
