import os
import requests
from typing import Dict, List
import re

API_URL = "https://api.telegram.org/bot{token}/{method}"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_THREAD_ID = os.getenv("TELEGRAM_THREAD_ID", None)
MAX_MESSAGE_LENGTH = 4000  # Telegram max ~4096

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales de Markdown."""
    escape_chars = r"_*[]()~`>#+-=|{}.!":  
    return re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", text)

def send_telegram_message(text: str) -> None:
    if TELEGRAM_BOT_TOKEN.startswith('PON_AQUI') or TELEGRAM_CHAT_ID.startswith('PON_AQUI'):
        print('[Aviso] Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID.')
        print(text)
        return

    text = escape_markdown(text)
    # Dividir en bloques si es muy largo
    messages = [text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]

    for msg in messages:
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': msg,
            'parse_mode': 'Markdown'
        }
        if TELEGRAM_THREAD_ID is not None:
            payload['message_thread_id'] = TELEGRAM_THREAD_ID

        try:
            r = requests.post(
                API_URL.format(token=TELEGRAM_BOT_TOKEN, method='sendMessage'),
                data=payload,
                timeout=20
            )
            if r.status_code != 200:
                print('[Telegram] Error:', r.text)
        except Exception as e:
            print('[Telegram] Excepción:', e)

def format_alert(ticker: str, signal: Dict) -> str:
    """Construye texto de alerta para un ticker."""
    min_exit = signal.get('min_exit')
    max_exit = signal.get('max_exit')
    min_exit_txt = '' if not min_exit else f'\nNo cerrar antes de: `{min_exit}`'
    max_exit_txt = '' if not max_exit else f'\nCerrar como tarde: `{max_exit}`'

    return (
        f'*Señal LONG* en *{ticker}*\n'
        f'Hora: `{signal["timestamp"]}`\n'
        f'Entrada: `{signal["entry"]}`\n'
        f'TP (arriba): `{signal["tp"]}`\n'
        f'SL (abajo): `{signal["sl"]}`\n'
        f'Nº acciones (presupuesto): `{signal["shares"]}`\n'
        f'Riesgo/acción: `{signal["risk_per_share"]}`'
        f'{min_exit_txt}{max_exit_txt}\n'
    )

def send_bulk_alerts(alerts: List[str]) -> None:
    """Envía una lista de alertas respetando el límite de Telegram."""
    if not alerts:
        print("[Info] Sin alertas que enviar.")
        return

    msg = "📊 *IBEX/NASDAQ Murphy Advisor — Recomendaciones actualizadas*\n\n" + "\n".join(alerts)
    send_telegram_message(msg)
