# IBEX Murphy Bot (gratis) – Alertas por Telegram (30m, 2h–2d)

> **Uso educativo/paper trading**. No ejecuta órdenes reales.

Escanea **IBEX‑35 (.MC)** en velas **30 m**, filtra **precio < 10 €**, y cuando la señal *long* (inspirada en Murphy) se cumple, envía alerta con **entrada**, **TP**, **SL**, **nº de acciones (presupuesto=10k)** y **ventana temporal** (no cerrar antes de 2 h; cerrar como tarde a 2 d).

## Novedades v3
- **Más robusto en datos**: reintentos simples y *fallback* a Yahoo Chart API.
- **Telegram en grupos con temas**: soporte opcional `TELEGRAM_THREAD_ID`.
- **Control horario** reforzado (UTC→Europe/Madrid) y pausas entre tickers.
- **Validaciones**: mínimo de velas suficientes antes de calcular indicadores.

## Uso rápido
```bash
pip install -r requirements.txt
python diagnostics.py SAN.MC
python run.py
```

## Secrets/Vars en GitHub
- Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Variables (opcional): `TIMEZONE`, `BUDGET`, `TELEGRAM_THREAD_ID`, `UNIVERSE_FILE`

## Licencia
MIT (educativo).
