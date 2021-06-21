class AGCH:

    def __init__(self):
        self.mobile = None
        self.bandwidth_parts = None  # List [] with the bandwidth parts assigned

    def set_agch(self, mobile, bandwidth_parts):
        self.mobile = mobile
        self.bandwidth_parts = bandwidth_parts

    def get_mobile(self):
        return self.mobile

    def get_bandwidth_parts(self):
        return self.bandwidth_parts
