# -*- coding: utf-8 -*-
import os
from datetime import timedelta

# ===== Telegram =====
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'PON_AQUI_TU_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'PON_AQUI_TU_CHAT_ID')
# Si publicas en un tema concreto de un supergrupo, pon el thread/topic id (entero)
TELEGRAM_THREAD_ID = os.getenv('TELEGRAM_THREAD_ID')
TELEGRAM_THREAD_ID = int(TELEGRAM_THREAD_ID) if TELEGRAM_THREAD_ID and TELEGRAM_THREAD_ID.isdigit() else None

# ===== Universo =====
DEFAULT_UNIVERSE = [
    "ACS.MC","ACX.MC","AENA.MC","AMS.MC","ANA.MC","ANE.MC","BBVA.MC","BKT.MC","CABK.MC","CLNX.MC",
    "COL.MC","ELE.MC","ENG.MC","FDR.MC","FER.MC","GRF.MC","IAG.MC","IBE.MC","IDR.MC","ITX.MC",
    "LOG.MC","MAP.MC","MRL.MC","MTS.MC","NTGY.MC","PUIG.MC","RED.MC","REP.MC","ROVI.MC","SAB.MC",
    "SAN.MC","SCYR.MC","SLR.MC","TEF.MC","UNI.MC"
]
UNIVERSE_FILE = os.getenv('UNIVERSE_FILE', 'tickers_ibex.txt')

# ===== Presupuesto y riesgo =====
BUDGET = float(os.getenv('BUDGET', '10000'))
MAX_RISK_FRACTION = float(os.getenv('MAX_RISK_FRACTION', '0.01'))

# ===== Estrategia =====
INTERVAL = os.getenv('INTERVAL', '30m')
LOOKBACK_DAYS = int(os.getenv('LOOKBACK_DAYS', '20'))
EMA_FAST = int(os.getenv('EMA_FAST', '20'))
EMA_SLOW = int(os.getenv('EMA_SLOW', '50'))
RSI_LEN = int(os.getenv('RSI_LEN', '14'))
RSI_MIN = int(os.getenv('RSI_MIN', '50'))
RSI_MAX = int(os.getenv('RSI_MAX', '70'))
HIGH_BREAK_LEN = int(os.getenv('HIGH_BREAK_LEN', '50'))
VOL_AVG_LEN = int(os.getenv('VOL_AVG_LEN', '20'))
ATR_LEN = int(os.getenv('ATR_LEN', '14'))
ATR_MULT_SL = float(os.getenv('ATR_MULT_SL', '1.5'))
RR = float(os.getenv('RR', '2.0'))

# ===== Tiempo de la operación =====
MAX_HOLD = timedelta(days=int(os.getenv('MAX_HOLD_DAYS', '2')))
MIN_HOLD_HOURS = int(os.getenv('MIN_HOLD_HOURS', '2'))

# ===== Zona horaria y control horario =====
TIMEZONE = os.getenv('TIMEZONE') or 'Europe/Madrid'
MARKET_OPEN = "00:00"
MARKET_CLOSE = os.getenv('MARKET_CLOSE', '23:59')

DRY_RUN = os.getenv('DRY_RUN', 'True').lower() == 'true'
