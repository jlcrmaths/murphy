# -*- coding: utf-8 -*-
import pandas as pd

def generate_signal(df: pd.DataFrame):
    """
    Estrategia de rebote/corrección usando Bandas de Bollinger:
        - BUY si precio toca la banda inferior
        - SELL si precio toca la banda superior
    """
    df['sma'] = df['close'].rolling(20).mean()
    df['std'] = df['close'].rolling(20).std()
    df['upper'] = df['sma'] + 2 * df['std']
    df['lower'] = df['sma'] - 2 * df['std']
    last = df.iloc[-1]

    if last['close'] < last['lower']:
        print("[Bollinger] Rebote en banda inferior ✅")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['sma'],
            'sl': last['close'] * 0.97,
            'reason': 'Rebote en banda inferior',
            'shares': 100,
            'color': 'green'
        }

    if last['close'] > last['upper']:
        print("[Bollinger] Corrección desde banda superior ⚠️")
        return {
            'timestamp': last['timestamp'],
            'entry': last['close'],
            'tp': last['sma'],
            'sl': last['close'] * 1.03,
            'reason': 'Corrección desde banda superior',
            'shares': 100,
            'color': 'red'
        }

    return None

