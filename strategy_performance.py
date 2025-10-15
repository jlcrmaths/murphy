# -*- coding: utf-8 -*-
"""
Registro y análisis del rendimiento de estrategias.
Guarda los resultados de cada operación en logs/strategy_stats.csv
y calcula su efectividad.
"""
import os
import pandas as pd
from datetime import datetime

LOG_FILE = "logs/strategy_stats.csv"

os.makedirs("logs", exist_ok=True)


def log_result(strategy_name, success, pnl):
    """Registra el resultado de una operación."""
    df = pd.DataFrame([{
        "timestamp": datetime.now(),
        "strategy": strategy_name,
        "success": success,
        "pnl": pnl
    }])
    header = not os.path.exists(LOG_FILE)
    df.to_csv(LOG_FILE, mode='a', index=False, header=header)


def get_strategy_scores():
    """Calcula la tasa de éxito y el PnL promedio de cada estrategia."""
    if not os.path.exists(LOG_FILE):
        return {}

    df = pd.read_csv(LOG_FILE)
    if df.empty:
        return {}

    summary = df.groupby("strategy").agg({
        "success": "mean",
        "pnl": "mean",
        "timestamp": "count"
    }).rename(columns={"timestamp": "n_ops"})

    scores = {}
    for name, row in summary.iterrows():
        # Fórmula de puntuación ponderada
        # (éxito * 0.7 + pnl_norm * 0.3)
        pnl_norm = (row["pnl"] + 1) / 2  # normaliza -1→0, +1→1
        score = (row["success"] * 0.7 + pnl_norm * 0.3)
        scores[name] = round(score, 3)

    return scores
