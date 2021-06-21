class CCH:
    # CCH Channel: PSS, SSS and BCH channels
    def __init__(self, base_id, beacon_carrier, duplex, RACH_and_AGCH_initial_RB, RACH_and_AGCH_final_RB, n_RACH_and_AGCH):
        self.base_id = base_id
        self.beacon_carrier = beacon_carrier
        self.duplex = duplex  # TDD, FDD, SUL, SDL
        # Resources for RACH and AGCH
        # Supposition: RACH and AGCH resources always in beacon carrier
        # Supposition: Half of the resources are for each of the channels
        self.RACH_and_AGCH_initial_RB = RACH_and_AGCH_initial_RB
        self.RACH_and_AGCH_final_RB = RACH_and_AGCH_final_RB
        self.n_RACH_and_AGCH = n_RACH_and_AGCH  # Number of channels

    def get_base_id(self):
        return self.base_id

    def get_beacon_carrier(self):
        return self.beacon_carrier

    def get_duplex(self):
        return self.duplex

    def get_RACH_and_AGCH_initial_RB(self):
        return self.RACH_and_AGCH_initial_RB

    def get_RACH_and_AGCH_final_RB(self):
        return self.RACH_and_AGCH_final_RB

    def get_n_RACH_and_AGCH(self):
        return self.n_RACH_and_AGCH
