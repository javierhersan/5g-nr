class FrequencyBand:

    # Frequency (MHz)
    def __init__(self, nr_id, initial_frequency, final_frequency, bandwidth_parts_supported, duplex):
        self.nr_id = nr_id  # NR Band ID
        self.initial_frequency = initial_frequency  # f(MHz)
        self.final_frequency = final_frequency  # f(MHz)
        self.bandwidth_parts_supported = bandwidth_parts_supported  # f(MHz) - Bandwidth Parts Supported
        self.duplex = duplex  # Duplex: TDD, FDD, SUL, SDL

    def get_nr_id(self):
        return self.nr_id

    def get_initial_frequency(self):
        return self.initial_frequency

    def get_final_frequency(self):
        return self.final_frequency

    def get_bandwidth_parts_supported(self):
        return self.bandwidth_parts_supported

    def get_duplex(self):
        return self.duplex

