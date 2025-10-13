# -*- coding: utf-8 -*-
import requests
from typing import Dict
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_THREAD_ID

API_URL = "https://api.telegram.org/bot{token}/{method}"


def send_telegram_message(text: str) -> None:
    if TELEGRAM_BOT_TOKEN.startswith('PON_AQUI') or TELEGRAM_CHAT_ID.startswith('PON_AQUI'):
        print('[Aviso] Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID (secrets/entorno).')
        print(text)
        return
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    if TELEGRAM_THREAD_ID is not None:
        payload['message_thread_id'] = TELEGRAM_THREAD_ID
    try:
        r = requests.post(API_URL.format(token=TELEGRAM_BOT_TOKEN, method='sendMessage'), data=payload, timeout=20)
        if r.status_code != 200:
            print('[Telegram] Error:', r.text)
    except Exception as e:
        print('[Telegram] Excepción:', e)


def format_alert(ticker: str, signal: Dict) -> str:
    min_exit = signal.get('min_exit')
    max_exit = signal.get('max_exit')
    min_exit_txt = f"
No cerrar antes de: `{min_exit}`" if min_exit else ''
    max_exit_txt = f"
Cerrar como tarde: `{max_exit}`" if max_exit else ''
    return (
        f"*Señal LONG* en *{ticker}*
"
        f"Hora: `{signal['timestamp']}`
"
        f"Entrada: `{signal['entry']}`
"
        f"TP (arriba): `{signal['tp']}`
"
        f"SL (abajo): `{signal['sl']}`
"
        f"Nº acciones (presupuesto): `{signal['shares']}`
"
        f"Riesgo/acción: `{signal['risk_per_share']}`" + min_exit_txt + max_exit_txt + "
"
    )
