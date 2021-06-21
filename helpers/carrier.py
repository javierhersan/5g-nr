class Carrier:

    def __init__(self, initial_frequency, bandwidth, subcarrier_spacing, max_resources, grid):
        self.initial_frequency = initial_frequency  # f(MHz)
        self.bandwidth = bandwidth  # f(MHz)
        self.subcarrier_spacing = subcarrier_spacing  # f(MHz)
        self.max_resources = max_resources
        self.grid = grid

    def get_initial_frequency(self):
        return self.initial_frequency

    def get_bandwidth(self):
        return self.bandwidth

    def get_subcarrier_spacing(self):
        return self.subcarrier_spacing

    def get_max_resources(self):
        return self.max_resources

    def get_resource_grid(self):
        return self.grid

    def set_resource_grid(self, subcarrier, symbol, channel):
        self.grid[subcarrier][symbol] = channel
