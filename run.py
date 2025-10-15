# -*- coding: utf-8 -*-
"""
🤖 IBEX Murphy Adaptive Bot — Escaneo robusto con manejo de errores
"""

from datetime import datetime, timedelta
import time
import pytz
import pandas as pd
import importlib
import os
import yfinance as yf

from config import (
    TIMEZONE, MIN_HOLD_HOURS, MARKET_OPEN, MARKET_CLOSE,
    UNIVERSE_FILE, DEFAULT_UNIVERSE as UNIVERSE_DEFAULT
)
from strategy_manager import STRATEGIES
from strategy_performance import log_result
from notifier import send_telegram_message, format_alert

# Parámetros generales
TEN_EUROS = 100.0
PAUSE_SEC = 0.35  # Pausa entre tickers para evitar rate limits

os.makedirs("logs", exist_ok=True)

# === Funciones auxiliares ===

def within_market_hours(dt_local: datetime) -> bool:
    if dt_local.weekday() > 4:
        return False
    h_open = datetime.strptime(MARKET_OPEN, '%H:%M').time()
    h_close = datetime.strptime(MARKET_CLOSE, '%H:%M').time()
    return h_open <= dt_local.time() <= h_close

def load_universe() -> list:
    try:
        with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if tickers:
                return tickers
    except FileNotFoundError:
        pass
    return UNIVERSE_DEFAULT

def download_bars(ticker: str, retries=3):
    for attempt in range(retries):
        try:
            df = yf.download(ticker, period='3mo', interval='1d', progress=False)
            if not df.empty:
                return df
        except Exception as e:
            print(f"[Intento {attempt+1}] Error {ticker}: {e}")
            time.sleep(1)
    print(f"[Error en download_bars] {ticker}: sin datos.")
    return None

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Aplana MultiIndex y normaliza nombres de columnas."""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{c[0].lower()}_{c[1].lower()}" for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]
    return df

def combine_signals(signals: list) -> dict:
    count_green = sum(1 for s in signals if s.get('color') == 'green')
    count_yellow = sum(1 for s in signals if s.get('color') == 'yellow')
    final_color = 'red'
    if count_green >= 2:
        final_color = 'green'
    elif count_green == 1 or count_yellow >= 1:
        final_color = 'yellow'
    if signals:
        latest_signal = max(signals, key=lambda x: x.get('timestamp', '1970-01-01'))
        latest_signal['color'] = final_color
        return latest_signal
    return None

# === Núcleo principal ===

def scan_once():
    tz = pytz.timezone(TIMEZONE)
    now_local = datetime.now(tz)
    if not within_market_hours(now_local):
        print(f"[Info] Fuera de horario de mercado ({now_local.strftime('%H:%M:%S %Z')})")
        return

    for ticker in load_universe():
        try:
            print(f"\n[Info] Escaneando {ticker} ...")
            df = download_bars(ticker)
            if df is None or df.empty:
                print(f"[Advertencia] {ticker}: sin datos recientes.")
                continue

            df = normalize_df(df)

            # Último cierre
            close_cols = [c for c in df.columns if 'close' in c]
            if not close_cols:
                print(f"[Error] {ticker}: columna 'close' no encontrada.")
                continue
            last_close = float(df[close_cols[0]].iloc[-1])

            if last_close >= TEN_EUROS:
                print(f"[Info] {ticker}: precio > {TEN_EUROS} €, omitido.")
                continue

            ticker_signals = []
            for strategy_module_name in STRATEGIES:
                module = importlib.import_module(strategy_module_name)
                strategy_name = strategy_module_name.split('.')[-1]
                try:
                    signal = module.generate_signal(df)
                    if signal:
                        signal['strategy_name'] = strategy_name
                        ticker_signals.append(signal)
                        pnl = (signal.get('tp', 0) - signal.get('entry', 0)) / max(signal.get('entry', 1), 1e-6)
                        log_result(strategy_name, success=True, pnl=pnl)
                    else:
                        log_result(strategy_name, success=False, pnl=0)
                except Exception as e:
                    print(f"[Error] {ticker} - {strategy_name}: {e}")
                time.sleep(PAUSE_SEC)

            # Combinar señales
            final_signal = combine_signals(ticker_signals)
            if final_signal and final_signal['color'] in ['green', 'yellow']:
                ts = pd.to_datetime(final_signal['timestamp'])
                if ts.tzinfo is None:
                    ts = ts.tz_localize('UTC')
                ts_local = ts.tz_convert(tz)
                final_signal['min_exit'] = (ts_local + timedelta(hours=MIN_HOLD_HOURS)).strftime('%Y-%m-%d %H:%M:%S %Z')
                final_signal['max_exit'] = (ts_local + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S %Z')
                msg = format_alert(ticker, final_signal, strategy_name='combined')
                send_telegram_message(msg)
                print(f"[ALERTA] {ticker} → {final_signal['color'].upper()} enviada a Telegram ✅")

        except Exception as e:
            print(f"[Error] {ticker}: {e}")
        time.sleep(PAUSE_SEC)

# === Ejecución directa ===
if __name__ == '__main__':
    print("=" * 60)
    print(" 🤖 IBEX Murphy Adaptive Bot — Inicio de escaneo ")
    print("=" * 60)
    scan_once()
    print("=" * 60)
    print(" 🔚 Escaneo finalizado ")
    print("=" * 60)










