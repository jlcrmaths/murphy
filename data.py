# -*- coding: utf-8 -*-
"""Fuente gratuita con tolerancia a fallos.
1) yfinance (Yahoo Finance)
2) Yahoo Chart API (JSON) con User-Agent
Incluye reintentos simples.
"""
import time
import pandas as pd
import requests
import yfinance as yf

from typing import Optional
from config import INTERVAL, LOOKBACK_DAYS

UA_HDRS = {"User-Agent": "Mozilla/5.0 (compatible; IBEXMurphyBot/1.0)"}


def _yfinance_download(ticker: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(
        tickers=ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'})
    return df[['open','high','low','close','volume']].dropna()


def _yahoo_chart_api(ticker: str, period: str, interval: str) -> pd.DataFrame:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?interval={interval}&range={period}&includePrePost=false&events=div,splits"
    )
    r = requests.get(url, headers=UA_HDRS, timeout=15)
    r.raise_for_status()
    data = r.json()
    result = data.get('chart', {}).get('result', [None])[0]
    if not result:
        return pd.DataFrame()
    ts = result.get('timestamp') or []
    quote = (result.get('indicators') or {}).get('quote', [{}])[0]
    if not ts or 'close' not in quote:
        return pd.DataFrame()
    df = pd.DataFrame({
        'open': quote.get('open', []),
        'high': quote.get('high', []),
        'low': quote.get('low', []),
        'close': quote.get('close', []),
        'volume': quote.get('volume', []),
    }, index=pd.to_datetime(ts, unit='s', utc=True))
    return df.dropna()


def _retry(func, tries=2, wait=1.0):
    last = None
    for i in range(tries):
        try:
            return func()
        except Exception as e:
            last = e
            time.sleep(wait)
    if last:
        raise last
    return None


def download_bars(ticker: str) -> pd.DataFrame:
    period = f"{LOOKBACK_DAYS}d"
    interval = INTERVAL

    # 1) yfinance con reintento
    try:
        df = _retry(lambda: _yfinance_download(ticker, period, interval), tries=2, wait=0.8)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass

    # 2) Yahoo Chart API con reintento
    try:
        df = _retry(lambda: _yahoo_chart_api(ticker, period, interval), tries=2, wait=0.8)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except Exception:
        pass

    return pd.DataFrame()
