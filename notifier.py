# notifier.py
# -*- coding: utf-8 -*-
"""
📢 Envío de alertas por Telegram (modo HTML seguro)
Evita errores de parseo de Markdown (como el caracter '.').
"""

import requests
from typing import Dict
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_THREAD_ID

API_URL = "https://api.telegram.org/bot{token}/{method}"

def send_telegram_message(text: str) -> None:
    """
    Envía un mensaje al canal o grupo configurado en Telegram.
    Usa formato HTML para evitar errores de parseo con caracteres especiales.
    """
    if TELEGRAM_BOT_TOKEN.startswith('PON_AQUI') or TELEGRAM_CHAT_ID.startswith('PON_AQUI'):
        print('[Aviso] Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en los secrets o entorno.')
        print(text)
        return

    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'  # ✅ Modo HTML seguro
    }

    # Publicar en un tema (topic) de supergrupo (opcional)
    if TELEGRAM_THREAD_ID not in [None, '', '0']:
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
    Construye el texto de la alerta en formato HTML:
    - ticker, hora
    - entrada, TP (arriba), SL (abajo)
    - nº de acciones y riesgo/acción
    - ventana temporal (min_exit, max_exit) si viene en signal
    """

    def safe(x):  # Evita fallos si faltan datos
        return x if x is not None else 'N/A'

    min_exit = signal.get('min_exit')
    max_exit = signal.get('max_exit')
    min_exit_txt = f"<br>No cerrar antes de: <code>{min_exit}</code>" if min_exit else ""
    max_exit_txt = f"<br>Cerrar como tarde: <code>{max_exit}</code>" if max_exit else ""

    entry = safe(signal.get('entry'))
    tp = safe(signal.get('tp'))
    sl = safe(signal.get('sl'))
    shares = safe(signal.get('shares'))
    risk = safe(signal.get('risk_per_share'))

    text = (
        f"<b>Señal LONG</b> en <b>{ticker}</b><br>"
        f"Hora: <code>{safe(signal.get('timestamp'))}</code><br>"
        f"Entrada: <code>{entry}</code><br>"
        f"TP (arriba): <code>{tp}</code><br>"
        f"SL (abajo): <code>{sl}</code><br>"
        f"Nº acciones (presupuesto): <code>{shares}</code><br>"
        f"Riesgo/acción: <code>{risk}</code>"
        f"{min_exit_txt}{max_exit_txt}<br>"
    )

    return text

