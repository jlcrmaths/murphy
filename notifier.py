# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict

API_URL = "https://api.telegram.org/bot{token}/{method}"

# Leer de variables de entorno (provenientes del workflow)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_THREAD_ID = os.getenv("TELEGRAM_THREAD_ID", None)


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
    # Publicar en un tema (topic) de supergrupo (opcional)
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
    """
    Construye el texto de la alerta:
    - ticker, hora
    - entrada, TP (arriba), SL (abajo)
    - nº de acciones y riesgo/acción
    - ventana temporal (min_exit, max_exit) si viene en signal
    """
    min_exit = signal.get('min_exit')
    max_exit = signal.get('max_exit')
    min_exit_txt = '' if not min_exit else '\nNo cerrar antes de: `{}`'.format(min_exit)
    max_exit_txt = '' if not max_exit else '\nCerrar como tarde: `{}`'.format(max_exit)

    return (
        '*Señal LONG* en *{}*\n'.format(ticker) +
        'Hora: `{}`\n'.format(signal['timestamp']) +
        'Entrada: `{}`\n'.format(signal['entry']) +
        'TP (arriba): `{}`\n'.format(signal['tp']) +
        'SL (abajo): `{}`\n'.format(signal['sl']) +
        'Nº acciones (presupuesto): `{}`\n'.format(signal['shares']) +
        'Riesgo/acción: `{}`'.format(signal['risk_per_share']) +
        min_exit_txt + max_exit_txt + '\n'
    )
