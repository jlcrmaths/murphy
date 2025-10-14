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
    """Comprueba si estamos dentro del horario de mercado."""
    if dt_local.weekday() > 4:  # sábado o domingo
        return False
    h_open = datetime.strptime(MARKET_OPEN, '%H:%M').time()
    h_close = datetime.strptime(MARKET_CLOSE, '%H:%M').time()
    return h_open <= dt_local.time() <= h_close


def load_universe() -> list:
    """Carga la lista de tickers desde el archivo o usa los valores por defecto."""
    try:
        with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if tickers:
                return tickers
    except FileNotFoundError:
        pass
    return UNIVERSE_DEFAULT


def scan_once():
    """Escanea una vez todos los tickers y envía señales si las hay."""
    try:
        tz = pytz.timezone(TIMEZONE)
    except Exception:
        print(f"[Error] Zona horaria inválida: '{TIMEZONE}', usando Europe/Madrid")
        tz = pytz.timezone('Europe/Madrid')

    now_local = datetime.now(tz)
    if not within_market_hours(now_local):
        print('[Info] Fuera de horario de mercado. Hora local:', now_local.strftime('%Y-%m-%d %H:%M:%S'))
        return

    print(f"[Info] Escaneo iniciado a las {now_local.strftime('%H:%M:%S')} ({TIMEZONE})")

    for ticker in load_universe():
        try:
            print(f"[Info] Escaneando {ticker} ...")
            df = download_bars(ticker)
            if df is None or df.empty:
                print(f"[Advertencia] {ticker}: sin datos recientes.")
                time.sleep(PAUSE_SEC)
                continue

            last_close = float(df['close'].iloc[-1])
            if last_close >= TEN_EUROS:
                print(f"[Info] {ticker}: último cierre {last_close:.2f} €, omitido (>=10€).")
                time.sleep(PAUSE_SEC)
                continue

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
                send_telegram_message(msg)
                print(f"[ALERTA] Señal detectada en {ticker}: {signal}")

        except Exception as e:
            print(f"[Error] {ticker}: {e}")

        finally:
            time.sleep(PAUSE_SEC)

    print("[Info] Escaneo completado.\n")


def main_loop(interval_minutes=10):
    """Ejecuta el escaneo cada cierto tiempo mientras el mercado esté abierto."""
    print(f"[Info] Modo continuo iniciado. Intervalo: {interval_minutes} minutos.\n")
    while True:
        scan_once()
        print(f"[Info] Esperando {interval_minutes} minutos antes del próximo escaneo...\n")
        time.sleep(interval_minutes * 60)


if __name__ == '__main__':
    # Puedes elegir entre ejecutar una sola vez o en bucle
    # scan_once()
    main_loop(interval_minutes=10)
