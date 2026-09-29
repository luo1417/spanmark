import numpy as np

from spanmark import locate_fault, m_sequence


def test_m_sequence_is_balanced_and_two_level():
    code = m_sequence()
    assert code.size == 127
    assert set(np.unique(code)) == {-1.0, 1.0}
    assert abs(code.sum()) == 1
    circ = np.array([np.dot(code, np.roll(code, k)) for k in range(code.size)])
    assert circ[0] == code.size
    assert np.all(circ[1:] == -1)


def test_open_and_short_peaks_have_opposite_sign():
    opened = locate_fault(50.0, reflection=1.0, noise_std=0.0)
    shorted = locate_fault(50.0, reflection=-1.0, noise_std=0.0)
    assert opened.lag_samples == shorted.lag_samples
    assert opened.peak > 0
    assert shorted.peak < 0


def test_distance_lands_on_the_planted_fault():
    found = locate_fault(50.0, reflection=-1.0, noise_std=0.0)
    assert abs(found.distance_m - 50.0) < 1e-6


def test_mild_noise_stays_within_one_sample():
    velocity = 2.0e8
    chip_rate = 2.5e6
    samples_per_chip = 4
    sample_rate = chip_rate * samples_per_chip
    step_m = velocity / (2.0 * sample_rate)
    found = locate_fault(80.0, reflection=-0.6, noise_std=0.05, seed=3)
    assert abs(found.distance_m - 80.0) <= step_m + 1e-9
