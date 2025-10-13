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
    # Publicar dentro de un tema (topic) de un supergrupo (opcional)
    if TELEGRAM_THREAD_ID is not None:
        payload['message_thread_id'] = TELEGRAM_THREAD_ID

    try:
        r = requests.post(
            API_URL.format(token=TELEGRAM_BOT_TOKEN, method='sendMessage'),
            data=payload, timeout=20
        )
        if r.status_code != 200:
            print('[Telegram] Error:', r.text)
    except Exception as e:
        print('[Telegram] Excepción:', e)

def format_alert(ticker: str, signal: Dict) -> str:
    """
    Construye el texto de la alerta con:
    - ticker
    - timestamp
    - entrada, TP (arriba), SL (abajo)
    - nº acciones y riesgo/acción
    - ventana temporal: no cerrar antes de (2h) / cerrar como tarde (2d) si viene en signal
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
