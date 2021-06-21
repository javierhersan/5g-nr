class RACH:

    # All the params are lists
    def __init__(self, mobiles, mimo_quadrant, uplink_modulation, downlink_modulation, uplink_datarate_needed, downlink_datarate_needed, latency):
        self.mobiles = mobiles  # Number of mobiles trying to access the same resource
        self.mimo_quadrant = mimo_quadrant
        self.uplink_modulation = uplink_modulation
        self.downlink_modulation = downlink_modulation
        self.uplink_datarate_needed = uplink_datarate_needed
        self.downlink_datarate_needed = downlink_datarate_needed
        self.latency = latency

    def get_mobiles(self):
        return self.mobiles

    def get_mimo_quadrant(self):
        return self.mimo_quadrant

    def get_uplink_modulation(self):
        return self.uplink_modulation

    def get_downlink_modulation(self):
        return self.downlink_modulation

    def get_uplink_datarate_needed(self):
        return self.uplink_datarate_needed

    def get_downlink_datarate_needed(self):
        return self.downlink_datarate_needed

    def get_latency(self):
        return self.latency

    def add_mobile(self, mobile):
        self.mobiles.append(mobile)

    def add_mimo_quadrant(self, mimo_quadrant):
        self.mimo_quadrant.append(mimo_quadrant)

    def add_uplink_modulation(self, mobile):
        self.uplink_modulation.append(mobile)

    def add_downlink_modulation(self, mimo_quadrant):
        self.downlink_modulation.append(mimo_quadrant)

    def add_uplink_datarate_needed(self, mobile):
        self.uplink_datarate_needed.append(mobile)

    def add_downlink_datarate_needed(self, mimo_quadrant):
        self.downlink_datarate_needed.append(mimo_quadrant)

    def add_latency(self, latency):
        self.latency.append(latency)
