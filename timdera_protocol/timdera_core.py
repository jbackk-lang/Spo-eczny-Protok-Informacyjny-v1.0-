class TIMDERCore:
    """
    Rdzeń protokołu TIMDERA.
    Operuje na skręcie, warstwach i modulacji.
    """

    def __init__(self):
        self.layers = None
        self.key = None

    def attach_layers(self, layers):
        self.layers = layers

    def attach_key(self, key):
        self.key = key

    def encode(self, data):
        twist = self.layers.apply_structure(data)
        modulated = self.layers.apply_transform(twist)
        defected = self.layers.apply_defect(modulated)
        return self.key.compress(defected)

    def decode(self, encoded):
        decompressed = self.key.decompress(encoded)
        restored = self.layers.reverse_defect(decompressed)
        demodulated = self.layers.reverse_transform(restored)
        return self.layers.reverse_structure(demodulated)
