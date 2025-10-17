# positions_state.py
# -*- coding: utf-8 -*-
"""
📊 Control de estado de posiciones y notificaciones
Guarda, consulta y actualiza la última acción de cada ticker.
Evita avisos repetidos en ejecuciones sucesivas del workflow de GitHub.
"""

import os
import pandas as pd
from datetime import datetime

STATE_FILE = "positions_state.csv"


def load_positions() -> pd.DataFrame:
    """Carga el CSV de posiciones si existe, o crea uno vacío."""
    if os.path.exists(STATE_FILE):
        try:
            df = pd.read_csv(STATE_FILE)
            if "ticker" not in df.columns:
                df = pd.DataFrame(columns=["ticker", "last_action", "last_signal", "last_update"])
        except Exception:
            df = pd.DataFrame(columns=["ticker", "last_action", "last_signal", "last_update"])
    else:
        df = pd.DataFrame(columns=["ticker", "last_action", "last_signal", "last_update"])
    return df


def save_positions(df: pd.DataFrame):
    """Guarda el DataFrame actualizado en CSV."""
    df.to_csv(STATE_FILE, index=False)


def get_last_action(ticker: str, df: pd.DataFrame) -> str:
    """Devuelve la última acción registrada para un ticker."""
    row = df[df["ticker"] == ticker]
    if not row.empty:
        return row.iloc[0]["last_action"]
    return "NONE"


def get_last_signal(ticker: str, df: pd.DataFrame) -> str:
    """Devuelve el último tipo de señal enviada (BUY, SELL, etc.) para el ticker."""
    row = df[df["ticker"] == ticker]
    if not row.empty:
        return row.iloc[0]["last_signal"]
    return None


def update_action(ticker: str, action: str, df: pd.DataFrame) -> pd.DataFrame:
    """Actualiza o crea una nueva entrada para un ticker."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if ticker in df["ticker"].values:
        df.loc[df["ticker"] == ticker, ["last_action", "last_signal", "last_update"]] = [action, action, now]
    else:
        df = pd.concat([df, pd.DataFrame([{
            "ticker": ticker,
            "last_action": action,
            "last_signal": action,
            "last_update": now
        }])], ignore_index=True)

    save_positions(df)
    return df


def should_notify(ticker: str, action: str, df: pd.DataFrame) -> bool:
    """
    Evita enviar notificaciones repetidas si ya se ha notificado la misma acción.
    Devuelve True solo si la acción ha cambiado.
    """
    last_signal = get_last_signal(ticker, df)
    return last_signal != action


# ============================================================
# Uso conjunto con recommender.py (flujo principal)
# ============================================================

def process_signal_and_notify(ticker: str, action: str, notifier_func):
    """
    Controla si debe notificarse una acción y actualiza el estado.
    - ticker: símbolo del activo
    - action: BUY, SELL, HOLD, SHORT, COVER o NONE
    - notifier_func: función externa que envía el mensaje (Telegram, etc.)
    """
    df = load_positions()

    if action == "NONE":
        return  # no notificar acciones neutras

    if should_notify(ticker, action, df):
        notifier_func(ticker, action)  # envía mensaje a Telegram u otro canal
        df = update_action(ticker, action, df)
        print(f"[State] {ticker}: acción '{action}' registrada y notificada ✅")
    else:
        print(f"[State] {ticker}: acción '{action}' ya notificada recientemente, se omite ⚪")


# ============================================================
# Inicialización (solo para uso manual/debug)
# ============================================================

if __name__ == "__main__":
    df = load_positions()
    print(df.head())

