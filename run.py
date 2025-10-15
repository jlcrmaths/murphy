# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
import pytz
import pandas as pd
from config import (
    TIMEZONE, MIN_HOLD_HOURS, MARKET_OPEN, MARKET_CLOSE,
    UNIVERSE_FILE, DEFAULT_UNIVERSE as UNIVERSE_DEFAULT
)
from data import download_bars
from strategy_manager import get_next_strategy   # ✅ CORRECTO
from strategy_performance import log_result      # ✅ NUEVO
from notifier import send_telegram_message, format_alert


# Parámetros generales
TEN_EUROS = 100.0
PAUSE_SEC = 0.35  # Pausa entre tickers para evitar rate limits


# === Funciones auxiliares ===

def within_market_hours(dt_local: datetime) -> bool:
    """Comprueba si la hora local está dentro del horario de mercado."""
    if dt_local.weekday() > 4:
        return False
    h_open = datetime.strptime(MARKET_OPEN, '%H:%M').time()
    h_close = datetime.strptime(MARKET_CLOSE, '%H:%M').time()
    return h_open <= dt_local.time() <= h_close


def load_universe() -> list:
    """Carga el universo de tickers desde archivo o usa el de config."""
    try:
        with open(UNIVERSE_FILE, 'r', encoding='utf-8') as f:
            tickers = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if tickers:
                return tickers
    except FileNotFoundError:
        pass
    return UNIVERSE_DEFAULT


# === Núcleo principal ===

def scan_once():
    """Ejecuta un escaneo único sobre todos los tickers."""
    tz = pytz.timezone(TIMEZONE)
    now_local = datetime.now(tz)

    if not within_market_hours(now_local):
        print(f"[Info] Fuera de horario de mercado ({now_local.strftime('%H:%M:%S %Z')})")
        return

    for ticker in load_universe():
        try:
            print(f"\n[Info] Escaneando {ticker} ...")

            # Descarga de datos
            df = download_bars(ticker)
            if df is None or df.empty:
                print(f"[Advertencia] {ticker}: sin datos recientes.")
                time.sleep(PAUSE_SEC)
                continue

            last_close = float(df['close'].iloc[-1])
            if last_close >= TEN_EUROS:
                print(f"[Info] {ticker}: precio superior a 10 €, omitido.")
                time.sleep(PAUSE_SEC)
                continue

            # Selección adaptativa de estrategia
            generate_signal, strategy_name = get_next_strategy()
            print(f"[Estrategia] Usando: {strategy_name}")

            signal = generate_signal(df)

            if signal:
                # Procesamiento temporal
                ts = pd.to_datetime(signal['timestamp'])
                if ts.tzinfo is None:
                    ts = ts.tz_localize('UTC')
                ts_local = ts.tz_convert(tz)

                min_exit = (ts_local + timedelta(hours=MIN_HOLD_HOURS)).strftime('%Y-%m-%d %H:%M:%S %Z')
                max_exit = (ts_local + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S %Z')
                signal['min_exit'] = min_exit
                signal['max_exit'] = max_exit

                # Generación del mensaje
                msg = format_alert(ticker, signal)
                send_telegram_message(msg)

                # Simulación de rendimiento teórico
                pnl = (signal['tp'] - signal['entry']) / signal['entry']
                log_result(strategy_name, success=True, pnl=pnl)
            else:
                log_result(strategy_name, success=False, pnl=0)

        except Exception as e:
            print(f"[Error] {ticker}: {e}")
        finally:
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


