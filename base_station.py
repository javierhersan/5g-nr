import math
import numpy

from helpers.random_helpers import random_number

from helpers.carrier import Carrier
from helpers.bandwidth_part import BandwidthPart

from channels.channel import Channel
from channels.cch import CCH
from channels.rach import RACH
from channels.agch import AGCH
from channels.psch import PSCH


class BaseStation:

    def __init__(self, x, y, z, base_id, frequency_band, initial_frequency, final_frequency, subcarrier_spacing, mimo,
                 power, antenna_gain, noise_spectral_density, step_simulation_time):
        # Position (km)
        self.x = x
        self.y = y
        self.z = z
        # Base Station id
        self.base_id = base_id
        # Power
        self.power = power
        self.power_per_subcarrier = None  # Calculated in configuration
        # Frequency (MHz)
        self.initial_frequency = initial_frequency
        self.final_frequency = final_frequency
        self.bandwidth = self.final_frequency - self.initial_frequency
        self.subcarrier_spacing = subcarrier_spacing
        self.n_subcarriers_per_carrier = None
        self.duplex = frequency_band.get_duplex()
        # MIMO Na x Nl
        self.mimo = mimo
        # Resource Grid
        self.is_configured = False  # Checks if the configuration() function have been executed
        self.carrier_grid = []
        # Time reference for the scheduler
        self.step_simulation_time = step_simulation_time
        # Beacon carrier
        self.n_CCH = 1  # Number of CCH Channel
        self.n_RACH_and_AGCH = 2  # Number of RACH and AGCH Channel
        # Connected mobiles
        self.connected_mobiles = []
        self.bandwidth_parts = []  # Bandwidth Parts of each user
        #
        self.max_allowed_REs = numpy.nan  # Only if carrier load is more than 80%
        #
        self.carrier_load = None
        #
        self.allowed_change_of_resources = True
        # Save info
        self.save = False
        self.info = []

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def get_base_id(self):
        return self.base_id

    def get_power(self):
        return self.power

    def get_power_per_subcarrier(self):
        return self.power_per_subcarrier

    def get_initial_frequency(self):
        return self.initial_frequency

    def get_final_frequency(self):
        return self.final_frequency

    def get_bandwidth(self):
        return self.bandwidth

    def get_subcarrier_spacing(self):
        return self.subcarrier_spacing

    def get_duplex(self):
        return self.duplex

    def get_mimo(self):
        return self.mimo

    def get_carrier_grid(self):
        return self.carrier_grid

    def set_carrier_grid(self, channel, carrier, resource, subframe):
        self.carrier_grid[carrier].set_resource_grid(resource, subframe, channel)

    def configuration(self):
        # TODO: Improve the configuration
        # In beacon carrier the subcarrier spacing numerology is 15 kHz and 30 KHz for FR1 -> PSS,SSS,PBCH
        # In beacon carrier the subcarrier spacing numerology is 60 kHz and 120 KHz for FR1 -> PSS,SSS,PBCH
        beacon_carrier = self.initial_frequency  # Initial frequency of Beacon carrier (baliza)
        subcarrier_spacing = self.subcarrier_spacing  # f(MHz)  TODO: Add if-statement because if the subcarrier spacing changes, the slots change as well
        n_symbols_per_slot = 14  # 15 kHz (14 OFDM symbols)
        n_slots_per_subframe = 1  # 15 kHz (14 OFDM symbols)
        n_subframes_per_frame = 10  # Every 10 ms
        n_symbols_per_subframe = n_symbols_per_slot * n_slots_per_subframe  # Every 1 ms
        n_slots_per_frame = n_slots_per_subframe * n_subframes_per_frame  # Every 10 ms
        n_symbols_per_frame = n_symbols_per_subframe * n_subframes_per_frame  # Every 10 ms
        resource_block = 12  # RB = 12 subcarriers
        max_resources = 275  # Max Resources = 275 RB / carrier - It changes depending on the subcarrier spacing
        n_subcarriers_per_carrier = max_resources * resource_block  # Subcarriers per carrier
        self.n_subcarriers_per_carrier = n_subcarriers_per_carrier
        self.power_per_subcarrier = self.power / self.n_subcarriers_per_carrier
        carrier_bandwidth = n_subcarriers_per_carrier * subcarrier_spacing
        n_carriers = math.floor(self.bandwidth / carrier_bandwidth)

        # Creating the resource grid (Only if this function is executed for the first time)
        if not self.is_configured:
            self.carrier_grid = [
                Carrier(self.initial_frequency + c * carrier_bandwidth, carrier_bandwidth, subcarrier_spacing,
                        max_resources, [[None for s in range(n_subframes_per_frame)] for r in range(max_resources)]) for
                c in range(n_carriers)]

        # Resource Blocks for each channel TODO: Add them to CONSTANTs
        CCH_RB = 20
        CCH_subframes = 10
        RACH_RB = 12
        RACH_subframes = 5
        AGCH_RB = 12
        AGCH_subframes = 5

        # Adding common control channels (CCH) to the resource grid (PSS,SSS,PBCH) -> Every 5 ms
        # TODO: The minimum resource can be 1 slot (14 OFDM symbols) or Mini-slot (7,4 or 2 OFDM symbols) - The slot can be all downlink, all uplink or mixed - Slot aggregation is supported to span multiple slots
        for RB in range(0,
                        self.n_CCH * CCH_RB):  # This control signals occupy 20 RB and 10 subframes (assumption in the occupied subframes)
            for s in range(0, CCH_subframes):  # Frame (10 Subframes (10 ms))
                self.carrier_grid[0].set_resource_grid(RB, s, Channel(
                    CCH(self.base_id, beacon_carrier, self.duplex, self.n_CCH * CCH_RB,
                        self.n_CCH * CCH_RB + self.n_RACH_and_AGCH * RACH_RB, self.n_RACH_and_AGCH), "CCH"))

        # Adding RACH and AGCH channels
        # Supposition: RACH and AGCH resources always in beacon carrier
        # Supposition: Half of the resources are for each of the channels
        for RB in range(self.n_CCH * CCH_RB,
                        self.n_CCH * CCH_RB + self.n_RACH_and_AGCH * RACH_RB):  # This control signals occupy 12 RB and 5 subframes (assumption in the occupied subframes)
            for s in range(0, RACH_subframes):  # Frame (5 Subframes (5 ms))
                self.carrier_grid[0].set_resource_grid(RB, s, Channel(RACH([], [], [], [], [], [], []), "RACH"))
        for RB in range(self.n_CCH * CCH_RB,
                        self.n_CCH * CCH_RB + self.n_RACH_and_AGCH * AGCH_RB):  # This control signals occupy 12 RB and 5 subframes (assumption in the occupied subframes)
            for s in range(RACH_subframes, RACH_subframes + AGCH_subframes):  # Frame (5 Subframes (5 ms))
                self.carrier_grid[0].set_resource_grid(RB, s, Channel(AGCH(), "AGCH"))

        # Creating the PSCH (Only if this function is executed for the first time)
        if not self.is_configured:
            self.is_configured = True
            # Adding PSCH: PUSCH, PDSCH (Downlink Information, Control Signal {PUCCH, PDCCH})
            for RB in range(self.n_CCH * CCH_RB + self.n_RACH_and_AGCH * RACH_RB, max_resources, 1):
                for s in range(0, 10, 1):  # (5 Even Subframes  (5 ms))
                    self.carrier_grid[0].set_resource_grid(RB, s, Channel(PSCH(self.mimo),
                                                                          "PSCH"))  # TODO: Unique Carrier (Beacon carrier) we have to add for more carriers

    # Every symbol
    def scheduler(self, subframe):
        # Read RACH -> If there is one request: answer it in AGCH channel and give resources | If there is two requests: ignore it
        carrier = 0  # Assumption: The RACH Channel is always is in the beacon carrier
        carrier_resources = self.carrier_grid[carrier].get_resource_grid()
        for r in range(20, 20 + 12 * self.n_RACH_and_AGCH, 12):
            if carrier_resources[r][subframe].get_channel_type() == "RACH":
                mobiles = carrier_resources[r][
                    subframe].get_channel().get_mobiles()  # Get mobiles accessing to that RACH
                if (len(mobiles) == 1) and (not (mobiles[0] in self.connected_mobiles)):
                    mobile = mobiles[0]
                    mimo_quadrant = carrier_resources[r][subframe].get_channel().get_mimo_quadrant()[0]
                    uplink_modulation = carrier_resources[r][subframe].get_channel().get_uplink_modulation()[0]
                    downlink_modulation = carrier_resources[r][subframe].get_channel().get_downlink_modulation()[0]
                    uplink_datarate_needed = carrier_resources[r][subframe].get_channel().get_uplink_datarate_needed()[0]
                    downlink_datarate_needed = carrier_resources[r][subframe].get_channel().get_downlink_datarate_needed()[0]
                    latency = carrier_resources[r][subframe].get_channel().get_latency()[0]
                    T_sym = 1 / (self.subcarrier_spacing * (10 ** 6))  # T(s)
                    V_sym = 1 / T_sym  # V_sym(symbols/s)
                    resource_block = 12
                    uplink_subcarrier_datarate = uplink_modulation * V_sym  # bps
                    downlink_subcarrier_datarate = downlink_modulation * V_sym  # bps
                    uplink_RB_datarate = uplink_subcarrier_datarate * resource_block
                    downlink_RB_datarate = downlink_subcarrier_datarate * resource_block
                    uplink_RE_datarate = uplink_RB_datarate / 10  # 10 Subframes (Slots)
                    downlink_RE_datarate = downlink_RB_datarate / 10  # 10 Subframes (Slots)
                    uplink_REs = math.ceil(uplink_datarate_needed / uplink_RE_datarate)
                    downlink_REs = math.ceil(downlink_datarate_needed / downlink_RE_datarate)
                    n_needed_REs = uplink_REs + downlink_REs
                    if self.max_allowed_REs != numpy.nan and n_needed_REs > self.max_allowed_REs:
                        n_needed_REs = self.max_allowed_REs
                    else:
                        if self.carrier_load is None or self.carrier_load < 80:
                            if uplink_REs < 10:
                                uplink_REs = 10
                            if downlink_REs < 10:
                                downlink_REs = 10
                            n_needed_REs = uplink_REs + downlink_REs

                    n_needed_RBs = math.ceil(n_needed_REs / 10)
                    # Search for empty resource
                    n_empty_RE_followed = 0

                    # Searching followed empty Resource Elements (REs)
                    initial_RB = None
                    initial_subframe = None
                    final_RB = None
                    final_subframe = None
                    for RE in range(n_needed_REs, 0, -1):
                        [was_it_found, initial_RB, initial_subframe, final_RB,
                         final_subframe] = self.searching_followed_empty_REs(RE, mimo_quadrant)
                        if was_it_found:
                            # Filling the followed empty Resource Elements (REs) if the empty resources were found
                            self.filling_REs(initial_RB, initial_subframe, final_RB, final_subframe, uplink_REs,
                                             downlink_REs, mimo_quadrant, mobile, uplink_modulation,
                                             downlink_modulation)
                            # Send AGCH
                            BP = BandwidthPart(0, initial_RB, initial_subframe, RE, mimo_quadrant)
                            carrier_resources[r][subframe + 5].get_channel().set_agch(mobiles[0], [BP])
                            self.connected_mobiles.append(mobile)
                            self.bandwidth_parts.append([BP])
                            break

    # Every second
    def long_scheduler(self):
        carrier = 0  # Assumption: The RACH Channel is always is in the beacon carrier
        carrier_resources = self.carrier_grid[carrier].get_resource_grid()
        total_REs = [0 for mimo in range(self.mimo)]
        used_REs = [0 for mimo in range(self.mimo)]
        for RB in range(0, 275, 1):
            for subframe in range(0, 10, 1):
                channel_type = carrier_resources[RB][subframe].get_channel_type()
                channel = carrier_resources[RB][subframe].get_channel()
                if channel_type == "PSCH":
                    for mimo in range(self.mimo):
                        if channel.is_PSCH_occupied(mimo):
                            used_REs[mimo] = used_REs[mimo] + 1
                            total_REs[mimo] = total_REs[mimo] + 1
                        else:
                            total_REs[mimo] = total_REs[mimo] + 1
                else:
                    for mimo in range(self.mimo):
                        used_REs[mimo] = used_REs[mimo] + 1
                        total_REs[mimo] = total_REs[mimo] + 1

        carrier_load = [100 * (used_REs[mimo] / total_REs[mimo]) for mimo in range(self.mimo)]
        total_carrier_load = (carrier_load[0] + carrier_load[1] + carrier_load[2] + carrier_load[3]) / 4
        self.carrier_load = total_carrier_load

        # Print Resources
        print(
            f'Base Station {self.base_id} -> Carriers: {1}, Subcarrier-spacing: {15} kHz, | Carrier 1: RBs: {275}, CCH RBs: {20}, RACH and AGCH RBs: {24}, PSCH RBs: {275 - (20 + 24)}, Carrier load: {round(total_carrier_load, 2)} %, Max allowed REs: {self.max_allowed_REs}')
        # print(f'Carrier load per quadrant: {carrier_load[0]},{carrier_load[1]},{carrier_load[2]},{carrier_load[3]}')
        if self.save:
            self.info.append({
                "carriers": 1,
                "subcarrier-spacing": 15000,
                "RBs": 275,
                "CCH_RBs": 20,
                "RACH_AGCH_RBs": 24,
                "PSCH_RBs": 275 - (20 + 24),
                "carrier_load": total_carrier_load,
                "carrier_load_s1": carrier_load[0],
                "carrier_load_s2": carrier_load[1],
                "carrier_load_s3": carrier_load[2],
                "carrier_load_s4": carrier_load[3],
                "max_allowed_REs_per_device": self.max_allowed_REs,
            })

        # Quit resources from the users that are using more (only if 80% of resources are used)
        if total_carrier_load > 80:
            max_REs = 0
            for n in self.bandwidth_parts:
                n_REs = n[0].get_n_REs()
                if n_REs > max_REs:
                    max_REs = n_REs
                    if max_REs > 1:
                        self.max_allowed_REs = n_REs - 1
                    else:
                        self.max_allowed_REs = 1

            if self.max_allowed_REs > 100:
                self.max_allowed_REs = 100
                for i in range(max_REs, 100, -1):
                    if i > 1:
                        number = 0
                        for n in self.bandwidth_parts:
                            if n[0].get_n_REs() == i:
                                n_REs = 0
                                for RB in range(n[0].get_initial_RB(), 275, 1):
                                    for subframe in range(0, 10, 1):
                                        channel_type = carrier_resources[RB][subframe].get_channel_type()
                                        channel = carrier_resources[RB][subframe].get_channel()
                                        if channel_type == "PSCH":
                                            if channel.get_mobile(n[0].get_resource_mimo_quadrant()) == \
                                                    self.connected_mobiles[number]:
                                                n_REs = n_REs + 1
                                                if n_REs == i:
                                                    self.empty_RE(n[0].get_initial_RB(), n[0].get_initial_subframe(),
                                                                  n[0].get_resource_mimo_quadrant())
                                                    if n[0].get_initial_subframe() < 9:
                                                        n[0].set_initial_subframe(n[0].get_initial_subframe() + 1)
                                                    else:
                                                        n[0].set_initial_RB(n[0].get_initial_RB() + 1)
                                                        n[0].set_initial_subframe(0)
                                                    n[0].set_n_REs(i - 1)
                            number = number + 1
            elif self.max_allowed_REs > 50:
                self.max_allowed_REs = 50
                for i in range(max_REs, 50, -1):
                    if i > 1:
                        number = 0
                        for n in self.bandwidth_parts:
                            if n[0].get_n_REs() == i:
                                n_REs = 0
                                for RB in range(n[0].get_initial_RB(), 275, 1):
                                    for subframe in range(0, 10, 1):
                                        channel_type = carrier_resources[RB][subframe].get_channel_type()
                                        channel = carrier_resources[RB][subframe].get_channel()
                                        if channel_type == "PSCH":
                                            if channel.get_mobile(n[0].get_resource_mimo_quadrant()) == \
                                                    self.connected_mobiles[number]:
                                                n_REs = n_REs + 1
                                                if n_REs == i:
                                                    self.empty_RE(n[0].get_initial_RB(), n[0].get_initial_subframe(),
                                                                  n[0].get_resource_mimo_quadrant())
                                                    if n[0].get_initial_subframe() < 9:
                                                        n[0].set_initial_subframe(n[0].get_initial_subframe() + 1)
                                                    else:
                                                        n[0].set_initial_RB(n[0].get_initial_RB() + 1)
                                                        n[0].set_initial_subframe(0)
                                                    n[0].set_n_REs(i - 1)
                            number = number + 1
            elif self.max_allowed_REs > 20:
                self.max_allowed_REs = 20
                for i in range(max_REs, 20, -1):
                    if i > 1:
                        number = 0
                        for n in self.bandwidth_parts:
                            if n[0].get_n_REs() == i:
                                n_REs = 0
                                for RB in range(n[0].get_initial_RB(), 275, 1):
                                    for subframe in range(0, 10, 1):
                                        channel_type = carrier_resources[RB][subframe].get_channel_type()
                                        channel = carrier_resources[RB][subframe].get_channel()
                                        if channel_type == "PSCH":
                                            if channel.get_mobile(n[0].get_resource_mimo_quadrant()) == \
                                                    self.connected_mobiles[number]:
                                                n_REs = n_REs + 1
                                                if n_REs == i:
                                                    self.empty_RE(n[0].get_initial_RB(), n[0].get_initial_subframe(),
                                                                  n[0].get_resource_mimo_quadrant())
                                                    if n[0].get_initial_subframe() < 9:
                                                        n[0].set_initial_subframe(n[0].get_initial_subframe() + 1)
                                                    else:
                                                        n[0].set_initial_RB(n[0].get_initial_RB() + 1)
                                                        n[0].set_initial_subframe(0)
                                                    n[0].set_n_REs(i - 1)
                            number = number + 1
            else:
                # 19, 18, 17,....
                if max_REs > 1:
                    number = 0
                    for n in self.bandwidth_parts:
                        if n[0].get_n_REs() == max_REs:
                            n_REs = 0
                            for RB in range(n[0].get_initial_RB(), 275, 1):
                                for subframe in range(0, 10, 1):
                                    channel_type = carrier_resources[RB][subframe].get_channel_type()
                                    channel = carrier_resources[RB][subframe].get_channel()
                                    if channel_type == "PSCH":
                                        if channel.get_mobile(n[0].get_resource_mimo_quadrant()) == \
                                                self.connected_mobiles[number]:
                                            n_REs = n_REs + 1
                                            if n_REs == max_REs:
                                                self.empty_RE(n[0].get_initial_RB(), n[0].get_initial_subframe(),
                                                              n[0].get_resource_mimo_quadrant())
                                                if n[0].get_initial_subframe() < 9:
                                                    n[0].set_initial_subframe(n[0].get_initial_subframe() + 1)
                                                else:
                                                    n[0].set_initial_RB(n[0].get_initial_RB() + 1)
                                                    n[0].set_initial_subframe(0)
                                                n[0].set_n_REs(max_REs - 1)
                        number = number + 1
        elif total_carrier_load > 40:
            # Check if it works
            if self.max_allowed_REs != numpy.nan:
                self.max_allowed_REs = self.max_allowed_REs + 1
        else:
            self.max_allowed_REs = numpy.nan

        self.allowed_change_of_resources = True

    # Searching followed empty Resource Elements (REs): PSCH Resource Elements
    def searching_followed_empty_REs(self, n_followed_REs, mimo_quadrant):
        initial_RB = None
        initial_subframe = None
        final_RB = None
        final_subframe = None
        n_empty_followed_REs = 0
        carrier_grid = self.carrier_grid[0].get_resource_grid()  # TODO: Search in all carriers
        for resource_block in range(0, 275):
            for subframe in range(0, 10):
                channel_type = carrier_grid[resource_block][subframe].get_channel_type()
                if channel_type == "PSCH":
                    channel = carrier_grid[resource_block][subframe].get_channel()
                    if not channel.is_PSCH_occupied(mimo_quadrant):
                        if n_empty_followed_REs == 0:
                            initial_RB = resource_block
                            initial_subframe = subframe
                            n_empty_followed_REs = n_empty_followed_REs + 1
                            if n_empty_followed_REs == n_followed_REs:
                                final_RB = resource_block
                                final_subframe = subframe
                                return [True, initial_RB, initial_subframe, final_RB, final_subframe]
                        elif n_empty_followed_REs < n_followed_REs:
                            n_empty_followed_REs = n_empty_followed_REs + 1
                            if n_empty_followed_REs == n_followed_REs:
                                final_RB = resource_block
                                final_subframe = subframe
                                return [True, initial_RB, initial_subframe, final_RB, final_subframe]
                    else:
                        initial_RB = None
                        initial_subframe = None
                        final_RB = None
                        final_subframe = None
                        n_empty_followed_REs = 0
        return [False, initial_RB, initial_subframe, final_RB, final_subframe]

    def filling_REs(self, initial_RB, initial_subframe, final_RB, final_subframe, uplink_REs, downlink_REs,
                    mimo_quadrant, mobile, uplink_modulation, downlink_modulation):
        n_filled_uplink_REs = 0
        n_filled_downlink_REs = 0
        carrier_grid = self.carrier_grid[0].get_resource_grid()  # TODO: Search in all carriers
        for resource_block in range(initial_RB, final_RB + 1):
            if resource_block == initial_RB and resource_block == final_RB:
                initial = initial_subframe
                final = final_subframe
            elif resource_block == initial_RB:
                initial = initial_subframe
                final = 9
            elif resource_block == final_RB:
                initial = 0
                final = final_subframe
                for subframe in range(0, final_RB): pass
            else:
                initial = 0
                final = 9
            # Filling alternate
            for subframe in range(initial, final + 1):
                if n_filled_downlink_REs < downlink_REs and subframe % 2 == 0:
                    carrier_grid[resource_block][subframe].get_channel().set_PSCH(mimo_quadrant, mobile, "PDSCH")
                    n_filled_downlink_REs = n_filled_downlink_REs + 1
                elif n_filled_uplink_REs < uplink_REs and subframe % 2 != 0:
                    carrier_grid[resource_block][subframe].get_channel().set_PSCH(mimo_quadrant, mobile, "PUSCH")
                    n_filled_uplink_REs = n_filled_uplink_REs + 1
                elif n_filled_downlink_REs < downlink_REs:
                    carrier_grid[resource_block][subframe].get_channel().set_PSCH(mimo_quadrant, mobile, "PDSCH")
                    n_filled_downlink_REs = n_filled_downlink_REs + 1
                elif n_filled_uplink_REs < uplink_REs:
                    carrier_grid[resource_block][subframe].get_channel().set_PSCH(mimo_quadrant, mobile, "PUSCH")
                    n_filled_uplink_REs = n_filled_uplink_REs + 1

    def empty_RE(self, RB, subframe, mimo_quadrant):
        carrier_grid = self.carrier_grid[0].get_resource_grid()
        carrier_grid[RB][subframe].get_channel().set_PSCH(mimo_quadrant, None, None)

    def change_resources(self, mobile):
        mobile_id = mobile.mobile_id
        mobile_index = self.connected_mobiles.index(mobile_id)
        bandwidth_part = self.bandwidth_parts[mobile_index][0]
        # REs calculation
        mimo_quadrant = bandwidth_part.get_resource_mimo_quadrant()
        uplink_modulation = mobile.uplink_modulation
        downlink_modulation = mobile.downlink_modulation
        uplink_datarate_needed = mobile.uplink_data_rate
        downlink_datarate_needed = mobile.downlink_data_rate
        T_sym = 1 / (self.subcarrier_spacing * (10 ** 6))  # T(s)
        V_sym = 1 / T_sym  # V_sym(symbols/s)
        resource_block = 12
        uplink_subcarrier_datarate = uplink_modulation * V_sym  # bps
        downlink_subcarrier_datarate = downlink_modulation * V_sym  # bps
        uplink_RB_datarate = uplink_subcarrier_datarate * resource_block
        downlink_RB_datarate = downlink_subcarrier_datarate * resource_block
        uplink_RE_datarate = uplink_RB_datarate / 10  # 10 Subframes (Slots)
        downlink_RE_datarate = downlink_RB_datarate / 10  # 10 Subframes (Slots)
        uplink_REs = math.ceil(uplink_datarate_needed / uplink_RE_datarate)
        downlink_REs = math.ceil(downlink_datarate_needed / downlink_RE_datarate)
        n_needed_REs = uplink_REs + downlink_REs
        if self.max_allowed_REs != numpy.nan and n_needed_REs > self.max_allowed_REs:
            n_needed_REs = self.max_allowed_REs
        else:
            if self.carrier_load is None or self.carrier_load < 80:
                if uplink_REs < 10:
                    uplink_REs = 10
                if downlink_REs < 10:
                    downlink_REs = 10
                n_needed_REs = uplink_REs + downlink_REs
        n_needed_RBs = math.ceil(n_needed_REs / 10)
        if (self.allowed_change_of_resources is True) or (
                self.allowed_change_of_resources is False and n_needed_REs <= self.max_allowed_REs):
            # Empty REs first
            initial_RB = bandwidth_part.get_initial_RB()
            initial_subframe = bandwidth_part.get_initial_subframe()
            n_REs = bandwidth_part.get_n_REs()
            for n in range(n_REs):
                self.empty_RE(initial_RB, initial_subframe, bandwidth_part.get_resource_mimo_quadrant())
                if initial_subframe == 9:
                    initial_subframe = 0
                    initial_RB = initial_RB + 1
                else:
                    initial_subframe = initial_subframe + 1

            # Searching followed empty Resource Elements (REs)
            initial_RB = None
            initial_subframe = None
            final_RB = None
            final_subframe = None
            for RE in range(n_needed_REs, 0, -1):
                [was_it_found, initial_RB, initial_subframe, final_RB,
                 final_subframe] = self.searching_followed_empty_REs(RE, mimo_quadrant)
                if was_it_found:
                    # Filling the followed empty Resource Elements (REs) if the empty resources were found
                    self.filling_REs(initial_RB, initial_subframe, final_RB, final_subframe, uplink_REs, downlink_REs,
                                     mimo_quadrant, mobile_id, uplink_modulation, downlink_modulation)
                    # Send AGCH
                    BP = BandwidthPart(0, initial_RB, initial_subframe, RE, mimo_quadrant)
                    mobile.bandwidth_parts[0] = BP
                    self.bandwidth_parts[mobile_index][0] = BP
                    break
                else:
                    if RE == self.max_allowed_REs:
                        self.allowed_change_of_resources = False

    def save_info(self):
        self.save = True

    def get_info(self):
        return self.info

    def get_save(self):
        return self.save
