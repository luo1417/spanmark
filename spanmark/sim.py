"""Single-cable SSTDR locator.

A bipolar m-sequence goes down one cable. The echo is a delayed, scaled copy.
Correlation against the transmitted chips puts the incident energy at lag 0
and the fault at the round-trip lag. Distance is that lag times velocity / 2.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Degree 7, polynomial x^7 + x + 1. Oldest bit is state[0].
_DEGREE = 7


def m_sequence(degree: int = _DEGREE) -> np.ndarray:
    """Bipolar m-sequence, length 2**degree - 1, values +1 and -1.

    The next bit is the XOR of the oldest bit and the one beside it,
    which is the recurrence for x^7 + x + 1.
    """
    if degree != _DEGREE:
        raise ValueError("only degree 7 is implemented")
    state = [1] * degree
    out = np.empty((1 << degree) - 1, dtype=np.float64)
    for i in range(out.size):
        out[i] = 1.0 if state[-1] else -1.0
        nxt = state[0] ^ state[1]
        state = state[1:] + [nxt]
    return out


@dataclass(frozen=True)
class LocateResult:
    distance_m: float
    lag_samples: int
    peak: float


def locate_fault(
    distance_m: float,
    reflection: float = -1.0,
    *,
    velocity_m_s: float = 2.0e8,
    chip_rate_hz: float = 2.5e6,
    samples_per_chip: int = 4,
    noise_std: float = 0.0,
    seed: int = 0,
    guard_samples: int = 2,
) -> LocateResult:
    """Simulate one cable and return the fault distance estimated from the echo peak.

    The incident peak at lag 0 is skipped. Search stops at one code period so a
    later wrap of the periodic code is not reported as a second fault.
    """
    if distance_m < 0:
        raise ValueError("distance_m must be >= 0")
    if samples_per_chip < 1:
        raise ValueError("samples_per_chip must be >= 1")
    if velocity_m_s <= 0 or chip_rate_hz <= 0:
        raise ValueError("velocity_m_s and chip_rate_hz must be > 0")

    code = m_sequence()
    reference = np.repeat(code, samples_per_chip)
    sample_rate = chip_rate_hz * samples_per_chip
    delay = int(round(2.0 * distance_m / velocity_m_s * sample_rate))
    if delay >= reference.size:
        raise ValueError("fault is farther than one code period at this chip rate")

    received = np.zeros(reference.size + delay, dtype=np.float64)
    received[: reference.size] += reference
    received[delay : delay + reference.size] += reflection * reference
    if noise_std > 0:
        rng = np.random.default_rng(seed)
        received += rng.normal(0.0, noise_std, size=received.shape)

    corr = np.correlate(received, reference, mode="full")
    zero = reference.size - 1
    # One period ahead of the incident peak, exclusive of the guard.
    start = zero + guard_samples
    stop = zero + reference.size
    window = corr[start:stop]
    if window.size == 0:
        raise ValueError("guard leaves no lags to search")
    offset = int(np.argmax(np.abs(window)))
    lag = guard_samples + offset
    peak = float(window[offset])
    estimated = lag / sample_rate * velocity_m_s / 2.0
    return LocateResult(distance_m=float(estimated), lag_samples=lag, peak=peak)
