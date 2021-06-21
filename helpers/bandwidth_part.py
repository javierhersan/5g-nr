class BandwidthPart:

    def __init__(self, carrier, initial_RB, initial_subframe, n_REs, resource_mimo_quadrant):
        self.carrier = carrier  # Carrier number
        self.initial_RB = initial_RB  # Initial RB: 12 subcarriers
        self.initial_subframe = initial_subframe
        self.n_REs = n_REs  # 10 REs per RB (15khz subcarrier)
        self.resource_mimo_quadrant = resource_mimo_quadrant

    def get_carrier(self):
        return self.carrier

    def get_initial_RB(self):
        return self.initial_RB

    def set_initial_RB(self, initial_RB):
        self.initial_RB = initial_RB

    def get_initial_subframe(self):
        return self.initial_subframe

    def set_initial_subframe(self, initial_subframe):
        self.initial_subframe = initial_subframe

    def get_n_REs(self):
        return self.n_REs

    def set_n_REs(self, n_REs):
        self.n_REs = n_REs

    def get_resource_mimo_quadrant(self):
        return self.resource_mimo_quadrant
