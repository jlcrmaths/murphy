# -*- coding: utf-8 -*-
"""
Selecciona estrategias con probabilidad proporcional a su rendimiento.
Si no hay histórico, rota de forma equitativa.
"""
import random
import importlib
import itertools
from strategy_performance import get_strategy_scores

STRATEGIES = [
    "strategies.murphy",
    "strategies.macd_momentum",
    "strategies.rsi_reversal",
    "strategies.bollinger_rebound",
    "strategies.ema_crossover"
]

_cycle = itertools.cycle(STRATEGIES)


def get_next_strategy():
    """Devuelve una estrategia ponderada por rendimiento."""
    scores = get_strategy_scores()

    if not scores:
        # Sin datos aún: rotación simple
        module_name = next(_cycle)
        module = importlib.import_module(module_name)
        return module.generate_signal, module_name.split(".")[-1]

    # Crea lista ponderada de estrategias según score
    weights = []
    for s in STRATEGIES:
        base_name = s.split(".")[-1]
        weights.append(scores.get(base_name, 0.5))  # valor neutro 0.5 si no hay datos

    # Selección ponderada
    module_name = random.choices(STRATEGIES, weights=weights, k=1)[0]
    module = importlib.import_module(module_name)
    print(f"[Adaptive] Seleccionada estrategia '{module_name.split('.')[-1]}' con peso {scores.get(module_name.split('.')[-1], 0.5):.2f}")
    return module.generate_signal, module_name.split(".")[-1]
