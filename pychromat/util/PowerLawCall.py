class PowerLawCall:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __call__(self, x):
        return (self.a * (x**self.b)) + self.c

    def describe(self):
        return str(self.a) + "*X^" + str(self.b) + "+" + str(self.c)
