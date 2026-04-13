"""Resilience-specific errors (not HTTP)."""


class CircuitOpenError(Exception):
    """Circuit breaker is open; fast-fail without calling downstream."""

    def __init__(self, breaker_name: str) -> None:
        self.breaker_name = breaker_name
        super().__init__(f"circuit_open:{breaker_name}")
