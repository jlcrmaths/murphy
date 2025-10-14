import yfinance as yf
import pandas as pd

print("[Info] Probando descarga de CABK.MC...")

# Descargamos los datos directamente
df = yf.download("CABK.MC", period="1mo", interval="1d", progress=True)

print("\n[Debug] Columnas del DataFrame:")
print(df.columns)

print("\n[Debug] Primeras filas:")
print(df.head())

# Aplanamos columnas si es MultiIndex
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [f"{a}_{b}".strip().lower() for a, b in df.columns]
else:
    df.columns = [c.lower() for c in df.columns]

print("\n[Debug] Columnas después de aplanar:")
print(df.columns)

df["timestamp"] = df.index
df = df.reset_index(drop=True)
cols = ["timestamp", "open", "high", "low", "close", "volume"]
df = df[[c for c in cols if c in df.columns]]

print("\n[Resultado final]:")
print(df.tail(5))
