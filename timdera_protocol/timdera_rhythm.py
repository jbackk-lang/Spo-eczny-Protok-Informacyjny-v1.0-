import numpy as np

class TIMDERRhythm:
    """
    Rytm — kodowanie czasowe komunikatu.
    """

    def __init__(self, history_length=32):
        self.history_length = history_length
        self.history = []

    def push(self, value):
        self.history.append(value)
        if len(self.history) > self.history_length:
            self.history.pop(0)

    def period(self):
        if len(self.history) < 4:
            return None
        fft = np.abs(np.fft.rfft(self.history))
        peak = np.argmax(fft[1:]) + 1
        return peak

    def modulate(self, data):
        p = self.period() or 1
        return [(x + (i % p)) for i, x in enumerate(data)]
