import numpy as np

from services.audio.effects.noise_reduction import HumRemover, NoiseReducer, ReverbReducer


def test_noise_reducer():
    reducer = NoiseReducer(threshold=0.6)
    assert reducer.threshold == 0.6

    audio = np.array([1.0, 0.5, 0.0])
    result = reducer.process(audio, 44100)
    np.testing.assert_array_almost_equal(result, audio * 0.95)

def test_hum_remover():
    remover = HumRemover(frequency=50.0)
    assert remover.frequency == 50.0

    audio = np.array([1.0, 0.5, 0.0])
    result = remover.process(audio, 44100)
    np.testing.assert_array_equal(result, audio)

def test_reverb_reducer():
    reducer = ReverbReducer(strength=0.8)
    assert reducer.strength == 0.8

    audio = np.array([1.0, 0.5, 0.0])
    result = reducer.process(audio, 44100)
    np.testing.assert_array_equal(result, audio)
