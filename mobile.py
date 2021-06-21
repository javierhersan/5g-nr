import math
import numpy

from helpers.random_helpers import random_number

from helpers.bandwidth_part import BandwidthPart
from helpers.carrier import Carrier
from helpers.frequency_band import FrequencyBand
from helpers.random_helpers import random_number, q_function
from helpers.radio_helpers import distance, modulation, propagation_delay
from helpers.radio_helpers import free_space_attenuation
from helpers.radio_helpers import model_attenuation

from channels.channel import Channel
from channels.cch import CCH
from channels.rach import RACH
from channels.agch import AGCH
from channels.psch import PSCH


class Mobile:

    def __init__(self, x, y, z, mobile_id, power, antenna_gain, noise_spectral_density, traffic_type, latency, subcarrier_spacing, step_simulation_time):
        self.x = x
        self.y = y
        self.z = z
        self.quadrant = self.get_quadrant()
        # Power
        self.power = power  # P(mW)
        self.power_per_subcarrier = power / (4 * 12)  # Imagine we have 4 RB max with 12 subcarriers each
        self.noise_spectral_density = noise_spectral_density  # P(mW)/Hz
        # Mobile State
        self.mobile_id = mobile_id  # Mobile ID
        self.state = "Searching"  # (Searching (Search cell), Reading (CCH), Connecting (Send RACH), Waiting (Wait for RACH answer) , Connected)
        # Radio Params
        self.downlink_modulation = None
        self.uplink_modulation = None
        self.latency = latency  # Latency (Low, High)
        # Connected Base Station Params
        self.base_id = None  # Base id
        self.base_beacon_carrier = None  # Beacon carrier of the base
        self.base_frequency_band_duplex = None  # Operating frequency band (Duplex) of the base: TDD, FDD, SUL, SDL
        self.base_RACH_and_AGCH_initial_RB = None  # RACH location param
        self.base_RACH_and_AGCH_final_RB = None  # RACH location param
        self.base_n_RACH_and_AGCH = None  # Number of RACH and AGCH channels
        self.bandwidth_parts = None
        self.subcarrier_spacing = subcarrier_spacing
        # Time reference for the scheduler
        self.step_simulation_time = step_simulation_time
        # Timers
        self.steps_for_reading_cch = 0  # Steps for reading a complete cch resource (0 =< t(ms) =< 20)
        self.steps_for_random_access = 0  # Steps to send another RACH
        self.seconds_for_change_resources = 0  # Nº of second for change resources in case we have a bad assigment
        # Mobile power (W) and antenna gain (dBi)
        # Save info
        self.save = False
        self.info = []
        # Data rate: traffic type and traffic state
        self.traffic_type = traffic_type  # Traffic type
        self.counter_1 = 0
        self.counter_2 = 0
        if traffic_type == 0:
            # Traffic State 1 -> 120 Seconds
            self.counter_1_limit = 120
            self.downlink_data_rate_1 = 20000000  # bps
            self.uplink_data_rate_1 = 10000  # bps
            # Traffic State 2 -> 10 Seconds
            self.counter_2_limit = 10
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 1:
            # Traffic State 1 -> 10 Seconds
            self.counter_1_limit = 10
            self.downlink_data_rate_1 = 20000000  # bps
            self.uplink_data_rate_1 = 10000  # bps
            # Traffic State 2 -> 60 Seconds
            self.counter_2_limit = 60
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 2:
            # Traffic State 1 -> 5 Seconds
            self.counter_1_limit = 5
            self.downlink_data_rate_1 = 1000000  # bps
            self.uplink_data_rate_1 = 10000  # bps
            # Traffic State 2 -> 120 Seconds
            self.counter_2_limit = 120
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 3:
            # Traffic State 1 -> 2 Seconds
            self.counter_1_limit = 2
            self.downlink_data_rate_1 = 1000000  # bps
            self.uplink_data_rate_1 = 10000  # bps
            # Traffic State 2 -> 120 Seconds
            self.counter_2_limit = 120
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 4:
            # Traffic State 1 -> 120 Seconds
            self.counter_1_limit = 120
            self.downlink_data_rate_1 = 10000  # bps
            self.uplink_data_rate_1 = 20000000  # bps
            # Traffic State 2 -> 10 Seconds
            self.counter_2_limit = 10
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 5:
            # Traffic State 1 -> 10 Seconds
            self.counter_1_limit = 10
            self.downlink_data_rate_1 = 10000  # bps
            self.uplink_data_rate_1 = 20000000  # bps
            # Traffic State 2 -> 60 Seconds
            self.counter_2_limit = 60
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 6:
            # Traffic State 1 -> 5 Seconds
            self.counter_1_limit = 5
            self.downlink_data_rate_1 = 10000  # bps
            self.uplink_data_rate_1 = 1000000  # bps
            # Traffic State 2 -> 120 Seconds
            self.counter_2_limit = 120
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps
        if traffic_type == 7:
            # Traffic State 1 -> 2 Seconds
            self.counter_1_limit = 2
            self.downlink_data_rate_1 = 10000  # bps
            self.uplink_data_rate_1 = 1000000  # bps
            # Traffic State 2 -> 120 Seconds
            self.counter_2_limit = 120
            self.downlink_data_rate_2 = 5000  # bps
            self.uplink_data_rate_2 = 5000  # bps
            # Traffic Initialization
            self.traffic_state = 1
            self.downlink_data_rate = self.downlink_data_rate_1  # bps
            self.uplink_data_rate = self.uplink_data_rate_1  # bps

        # Graph state (for plotting)
        self.graph_state = 0  # 0 => Not connected, 1 => Connected without enough resources, 2 => Connected with enough resources, 3 => Connected with enough resources and low latency (1 ms aprox)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def move(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.quadrant = self.get_quadrant()

    def get_quadrant(self):
        if self.x > 0 and self.y > 0:
            return 0
        elif self.x > 0 and self.y < 0:
            return 1
        elif self.x < 0 and self.y < 0:
            return 2
        elif self.x < 0 and self.y > 0:
            return 3

    def get_state(self):
        return self.state

    def scheduler(self, base_station, subframe):
        d = distance(self, base_station) * (10 ** 3)  # d(m)
        f = base_station.get_initial_frequency() * (10 ** 6)  # f(Hz)
        T_sym = 1 / (self.subcarrier_spacing * (10 ** 6))  # t(s)
        # Uplink: Modulation in uplink (256-QAM, 64-QAM, 16-QAM, QPSK)
        power_received_base_mw = self.power_per_subcarrier * model_attenuation(d, f)  # P(mW)
        power_received_base_dbm = 10 * math.log(power_received_base_mw, 10)
        uplink_modulation = modulation(power_received_base_mw, self.noise_spectral_density, self.subcarrier_spacing)
        self.uplink_modulation = uplink_modulation
        # TODO: Add redundancy and decrease of datarate because of ber
        # Downlink: Modulation in uplink (256-QAM, 64-QAM, 16-QAM, QPSK)
        power_received_mobile_mw = base_station.get_power_per_subcarrier() * model_attenuation(d, f)  # P(mW)
        power_received_mobile_dbm = 10 * math.log(power_received_mobile_mw, 10)
        downlink_modulation = modulation(power_received_mobile_mw, self.noise_spectral_density, self.subcarrier_spacing)
        self.downlink_modulation = downlink_modulation
        # TODO: Add redundancy and decrease of datarate because of ber

        uplink_datarate = 0
        downlink_datarate = 0
        uplink_REs = 0
        downlink_REs = 0

        # Searching CCH
        if self.state == "Searching":
            stop_searching = False
            for carrier in range(len(base_station.get_carrier_grid())):
                if stop_searching:
                    break
                frequency_carrier = base_station.get_carrier_grid()[carrier].get_initial_frequency()
                carrier_resources = base_station.get_carrier_grid()[carrier].get_resource_grid()
                for resource in range(len(carrier_resources)):
                    if carrier_resources[resource][subframe].get_channel_type() == "CCH":
                        CCH_channel = carrier_resources[resource][subframe].get_channel()
                        self.base_id = CCH_channel.get_base_id()
                        self.base_beacon_carrier = CCH_channel.get_beacon_carrier()
                        self.base_frequency_band_duplex = CCH_channel.get_duplex()
                        self.base_RACH_and_AGCH_initial_RB = CCH_channel.get_RACH_and_AGCH_initial_RB()
                        self.base_RACH_and_AGCH_final_RB = CCH_channel.get_RACH_and_AGCH_final_RB()
                        self.base_n_RACH_and_AGCH = CCH_channel.get_n_RACH_and_AGCH()
                        self.state = "Reading"
                        self.steps_for_reading_cch = int(random_number(0, 0.020) / self.step_simulation_time)  # (0 =< t(ms) =< 20) / (steps x s) = steps
                        stop_searching = True
                        break

        # Reading CCH
        elif self.state == "Reading":
            if self.steps_for_reading_cch == 0:
                self.state = "Connecting"

        # Send RACH request
        elif self.state == "Connecting":
            carrier = 0  # Assumption: The RACH Channel is always is in the beacon carrier
            carrier_resources = base_station.get_carrier_grid()[carrier].get_resource_grid()
            n_RACH = round(random_number(0, self.base_n_RACH_and_AGCH - 1))  # Selecting which RACH Channel
            for r in range(self.base_RACH_and_AGCH_initial_RB + n_RACH * 12, self.base_RACH_and_AGCH_initial_RB + n_RACH * 12 + 12):  # TODO: Remind that each RACH Channel = 12 RB
                if carrier_resources[r][subframe].get_channel_type() == "RACH":
                    RACH = carrier_resources[r][subframe].get_channel()  # Add mobile to RACH resource
                    RACH.add_mobile(self.mobile_id)
                    RACH.add_mimo_quadrant(self.quadrant)
                    RACH.add_uplink_modulation(uplink_modulation)
                    RACH.add_downlink_modulation(downlink_modulation)
                    RACH.add_uplink_datarate_needed(self.uplink_data_rate)
                    RACH.add_downlink_datarate_needed(self.downlink_data_rate)
                    RACH.add_latency(self.latency)
                    # base_station.set_carrier_grid(Channel(RACH, "RACH"), carrier, r, subframe)  # Duplicated with the upper sentence
                    self.state = "Waiting"
                    # Set a random time to try another RACH access in case of collision
                    max_cell_size = 100 * (10**3)  # m
                    light_speed = 3 * (10**8)  # m/s
                    round_trip_time = (2 * max_cell_size) / light_speed
                    self.steps_for_random_access = int(random_number(0.020, 0.060) / self.step_simulation_time)  # (20 =< t(ms) =< 60) / (steps x s) = steps
                    break

        elif self.state == "Waiting":
            if self.steps_for_random_access == 0:
                self.state = "Connecting"
            else:
                carrier = 0  # Assumption: The AGCH Channel is always is in the beacon carrier
                carrier_resources = base_station.get_carrier_grid()[carrier].get_resource_grid()
                for r in range(20, 20 + 12 * self.base_n_RACH_and_AGCH, 12):  # TODO: Remind that each RACH Channel = 12 RB
                    if carrier_resources[r][subframe].get_channel_type() == "AGCH":
                        AGCH = carrier_resources[r][subframe].get_channel()  # Get AGCH
                        AGCH_mobile_id = AGCH.get_mobile()
                        if self.mobile_id == AGCH_mobile_id:
                            self.bandwidth_parts = AGCH.get_bandwidth_parts()
                            self.state = "Connected"
                            self.base_id = base_station.get_base_id()

        # Executed 1 per second (we defined this in main.py)
        elif self.state == "Connected":
            carrier = self.bandwidth_parts[0].get_carrier()
            initial_RB = self.bandwidth_parts[0].get_initial_RB()
            initial_subframe = self.bandwidth_parts[0].get_initial_subframe()
            n_REs = self.bandwidth_parts[0].get_n_REs()
            n_remaining_REs = n_REs
            mimo_quadrant = self.bandwidth_parts[0].get_resource_mimo_quadrant()
            # Calculate uplink and downlink datarate and latency
            stop = False
            carrier_resources = base_station.get_carrier_grid()[carrier].get_resource_grid()
            for resource_block in range(initial_RB, 275):  # Remind that each RACH Channel = 12 RB
                if stop:
                    break
                for subframe in range(0, 10):
                    channel_type = carrier_resources[resource_block][subframe].get_channel_type()
                    if channel_type == "PSCH":
                        channel = carrier_resources[resource_block][subframe].get_channel()
                        subcarriers_per_resource_block = 12
                        subframes = 10
                        T_sym = 1 / (self.subcarrier_spacing * (10 ** 6))  # T(s)
                        V_sym = 1 / T_sym  # V_sym(symbols/s)
                        if channel.get_mobile(mimo_quadrant) == self.mobile_id:
                            if n_remaining_REs == 0:
                                stop = True
                                break
                            n_remaining_REs = n_remaining_REs - 1
                            if channel.get_channel(mimo_quadrant) == "PDSCH":
                                downlink_subcarrier_datarate = downlink_modulation * V_sym  # bps
                                downlink_RE_datarate = (downlink_subcarrier_datarate * subcarriers_per_resource_block) / subframes
                                downlink_datarate = downlink_datarate + downlink_RE_datarate
                                downlink_REs = downlink_REs + 1
                            elif channel.get_channel(mimo_quadrant) == "PUSCH":
                                uplink_subcarrier_datarate = uplink_modulation * V_sym  # bps
                                uplink_RE_datarate = (uplink_subcarrier_datarate * subcarriers_per_resource_block) / subframes
                                uplink_datarate = uplink_datarate + uplink_RE_datarate
                                uplink_REs = uplink_REs + 1
            REs = downlink_REs + uplink_REs
            RBs = math.ceil((downlink_REs + uplink_REs) / 10)
            propagation_latency = (propagation_delay(d) * (10 ** 3))  # t(ms)
            downlink_processing_latency = None
            uplink_processing_latency = None
            # Processing latency
            if 0 < downlink_REs < 10:
                downlink_processing_latency = 10 / downlink_REs  # t(ms)
            elif downlink_REs >= 10:
                downlink_processing_latency = 1  # t(ms)
            if 0 < uplink_REs < 10:
                uplink_processing_latency = 10 / uplink_REs  # t(ms)
            elif uplink_REs >= 10:
                uplink_processing_latency = 1  # t(ms)
            # Total latency
            if downlink_processing_latency is None:
                downlink_latency = numpy.nan
            else:
                downlink_latency = round(propagation_latency + downlink_processing_latency, 3)
            if uplink_processing_latency is None:
                uplink_latency = numpy.nan
            else:
                uplink_latency = round(propagation_latency + uplink_processing_latency, 3)

            # print(f'Mobile {self.mobile_id} -> RBs: {RBs}, REs: {REs}, BWP: {RBs * 12 * self.subcarrier_spacing} MHz, Prx = {round(10 * math.log(power_received_mobile_mw, 10), 2)} dBm, Ptx = {round(10 * math.log(self.power, 10), 2)} dBm | downlink: {downlink_datarate * (10**-3)} kbps, latency: {downlink_latency} ms, {downlink_REs} REs, {downlink_modulation}-QAM | uplink: {uplink_datarate * (10**-3)} kbps, latency: {uplink_latency} ms, {uplink_REs} REs, {uplink_modulation}-QAM')
            if self.save:
                self.info.append({
                                    "RBs": RBs,
                                    "REs": REs,
                                    "BWP": RBs * 12 * self.subcarrier_spacing,
                                    "DL_Prx": round(power_received_mobile_dbm, 2),
                                    "UL_Ptx": round(10 * math.log(self.power, 10), 2),
                                    "DL_Ptx": round(10 * math.log(base_station.get_power(), 10), 2),
                                    "UL_Prx": round(power_received_base_dbm, 2),
                                    "DL_needed_datarate": self.downlink_data_rate * (10**-3),  # kbps
                                    "DL_datarate": downlink_datarate * (10**-3),  # kbps
                                    "DL_latency": downlink_latency,
                                    "DL_REs": downlink_REs,
                                    "DL_modulation": downlink_modulation,
                                    "UL_needed_datarate": self.uplink_data_rate * (10**-3),  # kbps
                                    "UL_datarate": uplink_datarate * (10**-3),  # kbps
                                    "UL_latency": uplink_latency,
                                    "UL_REs": uplink_REs,
                                    "UL_modulation": uplink_modulation,
                                })

            # Check: If the speed is not enough ask for more resources or if the speed is enough ask for less resources
            T_sym = 1 / (self.subcarrier_spacing * (10 ** 6))  # T(s)
            V_sym = 1 / T_sym  # V_sym(symbols/s)
            resource_block = 12
            uplink_subcarrier_datarate = uplink_modulation * V_sym  # bps
            downlink_subcarrier_datarate = downlink_modulation * V_sym  # bps
            uplink_RB_datarate = uplink_subcarrier_datarate * resource_block
            downlink_RB_datarate = downlink_subcarrier_datarate * resource_block
            uplink_RE_datarate = uplink_RB_datarate / 10  # 10 Subframes (Slots)
            downlink_RE_datarate = downlink_RB_datarate / 10  # 10 Subframes (Slots)
            uplink_REs_needed = math.ceil(self.uplink_data_rate / uplink_RE_datarate)
            downlink_REs_needed = math.ceil(self.downlink_data_rate / downlink_RE_datarate)

            if uplink_REs < uplink_REs_needed or downlink_REs < downlink_REs_needed:
                self.graph_state = 1  # 1 => Connected without enough resources
            else:
                self.graph_state = 2  # 2 => Connected with enough resources
                if uplink_latency < 2 and downlink_latency < 2:
                    self.graph_state = 3  # 3 => Connected with enough resources and low latency (1 ms aprox)

            if uplink_REs != uplink_REs_needed or downlink_REs != downlink_REs_needed:
                if self.seconds_for_change_resources == 3:
                    base_station.change_resources(self)
                    self.seconds_for_change_resources = 0
                else:
                    self.seconds_for_change_resources = self.seconds_for_change_resources + 1
            else:
                self.seconds_for_change_resources = 0

            # Update traffic changes in the mobile
            if self.traffic_state == 1:
                self.counter_1 = self.counter_1 + 1
                if self.counter_1 == self.counter_1_limit:
                    self.counter_1 = 0
                    self.traffic_state = 2
                    self.downlink_data_rate = self.downlink_data_rate_2
                    self.uplink_data_rate = self.uplink_data_rate_2
            elif self.traffic_state == 2:
                self.counter_2 = self.counter_2 + 1
                if self.counter_2 == self.counter_2_limit:
                    self.counter_2 = 0
                    self.traffic_state = 1
                    self.downlink_data_rate = self.downlink_data_rate_1
                    self.uplink_data_rate = self.uplink_data_rate_1

        # Time counters in the mobile
        if self.steps_for_reading_cch != 0:
            self.steps_for_reading_cch = self.steps_for_reading_cch - 1
        # Updating time for another random access
        if self.steps_for_random_access != 0:
            self.steps_for_random_access = self.steps_for_random_access - 1

    def save_info(self):
        self.save = True

    def get_info(self):
        return self.info

    def get_save(self):
        return self.save
