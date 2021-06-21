class PSCH:

    # PSCH (Physical Shared Channel) -> For PUSCH, PDSCH and Control Signaling (PUCCH, PDCCH)
    def __init__(self, mimo):
        # All the params are list of BASE_MIMO dimension
        self.mobiles = [None for i in range(mimo)]
        self.channels = [None for i in range(mimo)]

    def set_PSCH(self, mimo_quadrant, mobile, channel):
        self.mobiles[mimo_quadrant] = mobile
        self.channels[mimo_quadrant] = channel

    def is_PSCH_occupied(self, mimo_quadrant):
        if self.mobiles[mimo_quadrant] is None:
            return False
        else:
            return True

    def get_mobile(self, mimo_quadrant):
        return self.mobiles[mimo_quadrant]

    def get_channel(self, mimo_quadrant):
        return self.channels[mimo_quadrant]
