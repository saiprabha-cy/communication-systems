class SequenceCounter:
    def __init__(self, start=0):
        self.value = start % 65536

    def next(self):
        current = self.value
        self.value = (self.value + 1) % 65536
        return current