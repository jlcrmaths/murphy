# run.py
from data import download_bars
import pandas as pd

# Ejemplo de lista de tickers
lista_tickers = [
    "AAPL", "MSFT", "GOOG", "CABK.MC", "SAB.MC", 
    "CLEOP.MC", "OLE.MC", "MDF.MC", "ECOENER.MC", "EDR.MC"
]

# Para registrar tickers omitidos
tickers_omitidos = []

# --- Funciones de indicadores ---
def calc_ema(df, period=10, col="close"):
    return df[col].ewm(span=period, adjust=False).mean()

def calc_rsi(df, period=14, col="close"):
    delta = df[col].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period, min_periods=1).mean()
    avg_loss = loss.rolling(period, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-10)  # evitar división por cero
    rsi = 100 - (100 / (1 + rs))
    return rsi

# --- Función de evaluación de señales ---
def evaluar_señal(df, ticker):
    df["EMA_fast"] = calc_ema(df, period=5)
    df["EMA_slow"] = calc_ema(df, period=20)
    df["RSI"] = calc_rsi(df, period=14)
    df["Vol_avg"] = df["volume"].rolling(20, min_periods=1).mean()

    # Última fila para evaluar señales
    last = df.iloc[-1]

    trend_up = last.EMA_fast > last.EMA_slow
    breakout = last.high > df["high"].iloc[-2]  # high > máximo anterior
    vol_ok = last.volume > 0.7 * last.Vol_avg
    rsi_ok = 30 < last.RSI < 70

    print(f"[DEBUG] Evaluando {last.timestamp}")
    print(f"EMA_fast={last.EMA_fast:.3f}, EMA_slow={last.EMA_slow:.3f} → trend_up={trend_up}")
    print(f"High={last.high:.3f}, Máx_prev={df['high'].iloc[-2]:.3f} → breakout={breakout}")
    print(f"Vol={last.volume}, Vol_avg={last.Vol_avg:.0f} → vol_ok={vol_ok}")
    print(f"RSI={last.RSI:.2f} → rsi_ok={rsi_ok}")

    if trend_up and breakout and vol_ok and rsi_ok:
        print(f"[Señal] {ticker}: condiciones OK para posible compra ✅")
    else:
        print(f"[Debug] {ticker}: sin señal.")

# --- Loop principal ---
for ticker in lista_tickers:
    df = download_bars(ticker)
    if df is None:
        tickers_omitidos.append(ticker)
        print(f"[Info] {ticker} omitido por falta de datos.")
        continue

    # Lógica de señales
    evaluar_señal(df, ticker)

# --- Resumen de tickers omitidos ---
if tickers_omitidos:
    print("\n[Resumen] Tickers que fallaron o se omitieron:")
    for t in tickers_omitidos:
        print(f" - {t}")











