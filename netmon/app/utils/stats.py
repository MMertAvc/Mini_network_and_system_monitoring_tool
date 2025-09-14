def ewma(values: list[float], alpha: float=0.3) -> float:
    if not values: return 0.0
    s = values[0]
    for v in values[1:]:
        s = alpha*v + (1-alpha)*s
    return s