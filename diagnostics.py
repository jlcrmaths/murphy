# -*- coding: utf-8 -*-
import sys
from data import download_bars

def main(t='SAN.MC'):
    df = download_bars(t)
    if df is None or df.empty:
        print('[X] No datos para', t)
    else:
        print('[OK] Datos para', t, '| filas:', len(df))
        print(df.tail())

if __name__ == '__main__':
    t = sys.argv[1] if len(sys.argv)>1 else 'SAN.MC'
    main(t)
