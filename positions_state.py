# -*- coding: utf-8 -*-
"""
📊 positions_state.py
Gestiona el estado de las posiciones abiertas o vigiladas entre ejecuciones.
Evita duplicar señales (por ejemplo, repetir un BUY o una alerta ya avisada).
"""

import os
import pandas as pd
from datetime import datetime

FILE_PATH = "positions_state.csv"

# ================================================
# 🔹 Cargar estado previo
# ================================================
def load_positions() -> pd.DataFrame:
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["ticker", "last_action", "timestamp"])
        df.to_csv(FILE_PATH, index=False)
        return df

    try:
        df = pd.read_csv(FILE_PATH)
        if df.empty or "ticker" not in df.columns:
            df = pd.DataFrame(columns=["ticker", "last_action", "timestamp"])
    except Exception:
        df = pd.DataFrame(columns=["ticker", "last_action", "timestamp"])
    return df


# ================================================
# 🔹 Obtener última acción registrada de un ticker
# ================================================
def get_last_action(ticker: str, df: pd.DataFrame = None) -> str:
    if df is None:
        df = load_positions()
    if df.empty:
        return "NONE"

    row = df[df["ticker"] == ticker]
    if row.empty:
        return "NONE"

    return str(row.iloc[-1]["last_action"]).upper()


# ================================================
# 🔹 Actualizar acción de un ticker
# ================================================
def update_action(ticker: str, action: str, df: pd.DataFrame = None) -> pd.DataFrame:
    if df is None:
        df = load_positions()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Si ya existe el ticker, se actualiza su última acción
    if ticker in df["ticker"].values:
        df.loc[df["ticker"] == ticker, ["last_action", "timestamp"]] = [action, now]
    else:
        df = pd.concat([df, pd.DataFrame([[ticker, action, now]], columns=["ticker", "last_action", "timestamp"])], ignore_index=True)

    df.to_csv(FILE_PATH, index=False)
    return df


# ================================================
# 🔹 Guardar DataFrame completo (si ya lo tienes modificado)
# ================================================
def save_positions(df: pd.DataFrame):
    df.to_csv(FILE_PATH, index=False)


# ================================================
# 🔹 Verificar si se debe notificar (evita avisos repetidos)
# ================================================
def should_notify(ticker: str, new_action: str, df: pd.DataFrame = None) -> bool:
    """
    Devuelve True si hay un cambio relevante en la acción
    y por tanto debe enviarse una nueva notificación.
    """
    last_action = get_last_action(ticker, df)

    # Evita repetir la misma señal (ej. BUY → BUY)
    if new_action == last_action:
        return False

    # Si pasa de NONE a cualquier acción → notificar
    if last_action == "NONE" and new_action != "NONE":
        return True

    # Si cambia de BUY a SELL o viceversa → notificar
    if (last_action in ["BUY", "HOLD"] and new_action == "SELL") or \
       (last_action == "SELL" and new_action == "BUY"):
        return True

    # Si cambia de LONG a SHORT o COVER → notificar
    if (last_action == "SHORT" and new_action == "COVER") or \
       (last_action == "COVER" and new_action == "SHORT"):
        return True

    # Para otros cambios menores (ej. BUY → HOLD), puedes decidir si avisar
    if new_action in ["HOLD", "COVER"] and last_action not in ["HOLD", new_action]:
        return True

    return False
