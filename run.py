# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
import pytz
import pandas as pd
from config import TIMEZONE, MIN_HOLD_HOURS, MARKET_OPEN, MARKET_CLOSE, UNIVERSE_FILE
from config import DEFAULT_UNIVERSE as UNIVERSE_DEFAULT
from data import download_bars
from strategy import generate_signal
from notifier import send_telegram_message, format_alert

TEN_EUROS = 10.0
PAUSE_SEC = 0.35  # Pausa entre tickers para evitar rate limits


def within_market_hours(dt_local: datetime) -> bool:
    """Devuelve True si está dentro del horario de mercado."""
    if dt_local.weekday() > 4:
        return False
    h_open = datetime.strptime(MARKET_OPEN, '%H:%M').time()
    h_close = datetime.strptime(MARKET_CLOSE, '%H:%M').time()
    return h_open <= dt_local.time() <= h_close


def load_universe() -> list:
    """Carga el universo de tickers desde archivo o usa los valores por defecto."""
    try:
        with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if tickers:
                return tickers
    except FileNotFoundError:
        pass
    return UNIVERSE_DEFAULT


def scan_once():
    tz = pytz.timezone(TIMEZONE)
    now_local = datetime.now(tz)

    if not within_market_hours(now_local):
        print('[Info] Fuera de horario de mercado. Hora local:', now_local)
        return

    for ticker in load_universe():
        try:
            print(f"[Info] Escaneando {ticker} ...")
            df = download_bars(ticker)
            if df is None or df.empty:
                print(f"[Advertencia] {ticker}: sin datos.")
                time.sleep(PAUSE_SEC)
                continue

            last_close = float(df['close'].iloc[-1])
            print(f"[Debug] Último cierre de {ticker}: {last_close} €")

            if last_close >= TEN_EUROS:
                print(f"[Info] {ticker}: precio > 10 €, se omite.")
                time.sleep(PAUSE_SEC)
                continue

            # Llamar a la estrategia para generar señal
            signal = generate_signal(df)
            if signal:
                ts = pd.to_datetime(signal['timestamp'])
                if ts.tzinfo is None:
                    ts = ts.tz_localize('UTC')
                ts_local = ts.tz_convert(tz)
                min_exit = (ts_local + timedelta(hours=MIN_HOLD_HOURS)).strftime('%Y-%m-%d %H:%M:%S %Z')
                max_exit = (ts_local + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S %Z')
                signal['min_exit'] = min_exit
                signal['max_exit'] = max_exit

                msg = format_alert(ticker, signal)
                print(f"[ALERTA] {msg}")
                send_telegram_message(msg)
            else:
                print(f"[Info] {ticker}: sin señal.")
        except Exception as e:
            print(f"[Error] {ticker}: {e}")
        finally:
            time.sleep(PAUSE_SEC)


if __name__ == '__main__':
    scan_once()

