def clamp(v: float | int, mini: float | int, maxi: float | int) -> float | int:
    return min(maxi, max(v, mini))
