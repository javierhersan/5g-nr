import matplotlib.pyplot as plt
import math
import numpy

from helpers.frequency_band import FrequencyBand
from helpers.random_helpers import random_number, q_function, random_number_between_args
from helpers.radio_helpers import distance, modulation
from helpers.radio_helpers import free_space_attenuation
from helpers.radio_helpers import model_attenuation

from base_station import BaseStation
from mobile import Mobile


def main():
    # Simulation configuration
    step_simulation_frequency = 15000  # f(Hz) - One OFDM symbol per step - Subcarrier spacing: f(Hz) = 2^n * 15000 , 0 < n =< 4
    step_simulation_time = 1 / step_simulation_frequency  # t(s) - Time between each simulation step
    n_step_simulation_time_per_s = int(1 / step_simulation_time)  # nº/s - Number of simulation steps per second
    n_step_simulation_time_per_ms = int(n_step_simulation_time_per_s / 1000)  # nº/ms - Number of simulation steps per milisecond
    n_step_simulation_time_per_m = int(60 / step_simulation_time)  # nº/min - Number of simulation steps per minute
    n_step_simulation_time_per_h = int(3600 / step_simulation_time)  # nº/h - Number of simulation steps per hour

    # Simulation parameters
    n_mobiles = 20  # nº - Number of initial mobiles
    mobiles_connection_rate = 20  # Mobiles connected per second - If rate>0 then n_mobiles grow, If rate <0 then n_mobiles decrease
    mobiles_speed_kmh = 4  # km/h - Mobiles speed average (km/h): 0 km/h < Speed < 500 km/h
    mobiles_speed_kms = mobiles_speed_kmh / 3600  # km/s - Mobiles speed average (km/s)

    # Cell size
    # Max cell size = 660 m (Limited by the propagation model)
    cell_size = 0.400  # Cell size (km) - The max cell radius is 100 km - Stage: Industrial environment
    # cell_size = 0.250  # Cell size (km) - The max cell radius is 100 km - Urban micro-cell environment
    cell_area = cell_size * cell_size  # Cell area (km^2)

    # Frequency Band - f(MHz)
    nr_frequency_band = FrequencyBand("n78", 3300, 3800, [5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100], "TDD")

    # Noise power
    noise_spectral_density_dbm_hz = -173.8  # P(dBm)/Hz - Thermal Noise in ambient temperature = -173.8 dBm/Hz
    noise_spectral_density_mw_hz = 10 ** (noise_spectral_density_dbm_hz / 10)  # P(mW)/Hz - Thermal Noise in ambient temperature

    # Base station parameters
    base_id = 0
    subcarrier_spacing = step_simulation_frequency / (10**6)  # f(MHz)
    base_power_dbm = 38  # P(dBm)
    base_power_mw = 10 ** (base_power_dbm / 10)   # P(mW)
    base_antenna_gain = 17  # G(dBi)
    base_stations = [BaseStation(0, 0, 0, base_id, nr_frequency_band, 3750, 3800, subcarrier_spacing, 4, base_power_mw, base_antenna_gain, noise_spectral_density_mw_hz, step_simulation_time)]
    base_stations[0].configuration()
    base_stations[0].save_info()

    # Mobiles parameters
    # TODO: Random Mobile Data Rates
    # TODO: Change datarate in time
    mobile_power_dbm = 22  # P(dBm)
    mobile_power_mw = 10 ** (mobile_power_dbm / 10)  # P(mW)
    mobile_antenna_gain = 0  # G(dBi)
    mobile_latency = "High"
    # mobile_categories = [0, 1, 2, 3, 4, 5, 6, 7]  # Microcell urban environment
    mobile_categories = [2, 3, 6, 7]  # Microcell industrial environment
    mobiles = [Mobile(random_number(-cell_size, cell_size), random_number(-cell_size, cell_size), 0, mobile_id, mobile_power_mw, mobile_antenna_gain, noise_spectral_density_mw_hz, random_number_between_args(mobile_categories), mobile_latency, subcarrier_spacing, step_simulation_time) for mobile_id in range(n_mobiles)]
    # Plot information of some mobiles
    mobiles[0].save_info()

    # Time References
    step = 0
    subframe = 0
    second = 0
    minute = 0
    hour = 0

    # Interactive plot
    plt.ion()

    # List for plots
    n_mobiles_in_time = []
    n_connected_mobiles_in_time = []
    n_mobiles0_in_time = []
    n_mobiles1_in_time = []
    n_mobiles2_in_time = []
    n_mobiles3_in_time = []

    while True:
        # TODO: Contar cuántos móviles no se han podido conectar
        # If statement executed once per milisecond (For subframes and frames updates)
        if step % n_step_simulation_time_per_ms == 0 and step != 0:
            if subframe < 9:
                subframe = subframe + 1
            elif subframe == 9:
                subframe = 0
                base_stations[0].configuration()  # Clean the resource grid for each frame

        # Mobile scheduling (If It is connected we execute this function once per second to reduce computational complexity)
        for mobile in range(len(mobiles)):
            if mobiles[mobile].get_state() != "Connected":
                mobiles[mobile].scheduler(base_stations[0], subframe)  # Add slot param for other numerologies

        # Short Time Base scheduling
        base_stations[0].scheduler(subframe)  # Add slot param for other numerologies

        # If statement executed once per second (For plotting, update position and update time)
        if step % n_step_simulation_time_per_s == 0 and step != 0:
            # Update time reference
            step = 0
            second = second + 1
            if second == 60:
                second = 0
                minute = minute + 1
            if minute == 60:
                minute = 0
                hour = hour + 1
            print(f"Time: {hour}:{minute}:{second}")

            # Mobile scheduling (If It is connected we execute this function once per second to reduce computational complexity)
            n_connected_mobiles = 0
            for mobile in range(len(mobiles)):
                if mobiles[mobile].get_state() == "Connected":
                    n_connected_mobiles = n_connected_mobiles + 1
                    mobiles[mobile].scheduler(base_stations[0], subframe)  # Add slot param for other numerologies

            # Long Time Base scheduling and Print base station resources
            base_stations[0].long_scheduler()

            # Print Connected Mobiles
            print(f"Mobiles -> Total: {n_mobiles} | Connected: {n_connected_mobiles}")

            # Mobiles state
            n_mobiles0 = 0
            n_mobiles1 = 0
            n_mobiles2 = 0
            n_mobiles3 = 0

            # Map plot
            # Plot Tittle and Axis
            figure = 1  # Figure number
            plt.figure(figure)
            plt.cla()  # Clear previous plot
            plt.tight_layout(pad=2.0)
            plt.suptitle('5G-NR')
            ax = plt.subplot(1, 1, 1)
            ax.axis([-cell_size, cell_size, -cell_size, cell_size])
            ax.set_xlabel('X (km)')
            ax.set_ylabel('Y (km)')
            ax.set_title('Map')
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            # Plotting Mobiles
            for i in range(len(mobiles)):
                new_x = mobiles[i].get_x() + random_number(-mobiles_speed_kms, mobiles_speed_kms)
                new_y = mobiles[i].get_y() + random_number(-mobiles_speed_kms, mobiles_speed_kms)
                mobiles[i].move(new_x, new_y, 0)  # Moving the mobile
                # Plotting the mobile
                if mobiles[i].graph_state == 0:
                    n_mobiles0 = n_mobiles0 + 1
                    if n_mobiles0 == 1:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'yo', label="Not connected")
                        ax.legend(loc="upper left")
                    else:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'yo')
                elif mobiles[i].graph_state == 1:
                    n_mobiles1 = n_mobiles1 + 1
                    if n_mobiles1 == 1:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'go', label="Connected without enough resources")
                        ax.legend(loc="upper left")
                    else:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'go')
                elif mobiles[i].graph_state == 2:
                    n_mobiles2 = n_mobiles2 + 1
                    if n_mobiles2 == 1:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'co', label="Connected with enough resources")
                        ax.legend(loc="upper left")
                    else:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'co')
                elif mobiles[i].graph_state == 3:
                    n_mobiles3 = n_mobiles3 + 1
                    if n_mobiles3 == 1:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'bo', label="Connected with enough resources and low latency")
                        ax.legend(loc="upper left")
                    else:
                        ax.plot(mobiles[i].get_x(), mobiles[i].get_y(), 'bo')
            plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
            plt.draw()
            # Plotting Base Station
            ax.plot(base_stations[0].get_x(), base_stations[0].get_y(), 'ro')
            # Plot time pause (s)
            plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
            plt.draw()

            figure = 2  # Figure number
            # Base Params plot
            if base_stations[0].get_save():
                # Get Base Info
                info = base_stations[0].get_info()
                RBs = [i['RBs'] for i in info]
                CCH_RBs = [i['CCH_RBs'] for i in info]
                RACH_AGCH_RBs = [i['RACH_AGCH_RBs'] for i in info]
                carrier_load = [i['carrier_load'] for i in info]
                carrier_load_s1 = [i['carrier_load_s1'] for i in info]
                carrier_load_s2 = [i['carrier_load_s2'] for i in info]
                carrier_load_s3 = [i['carrier_load_s3'] for i in info]
                carrier_load_s4 = [i['carrier_load_s4'] for i in info]
                max_allowed_REs_per_device = [i['max_allowed_REs_per_device'] for i in info]
                # Plot base info
                plt.figure(figure)
                plt.tight_layout(pad=2.0)
                plt.suptitle(f'Base {0}')
                #
                axb1 = plt.subplot(3, 1, 1)
                axb1.plot(range(len(info)), carrier_load, 'r-', label="Total")
                axb1.plot(range(len(info)), carrier_load_s1, 'b-', label="Sector 1")
                axb1.plot(range(len(info)), carrier_load_s2, 'c-', label="Sector 2")
                axb1.plot(range(len(info)), carrier_load_s3, 'y-', label="Sector 3")
                axb1.plot(range(len(info)), carrier_load_s4, 'g-', label="Sector 4")
                if len(info) == 1:
                    axb1.legend(loc="upper left")
                axb1.set_ylabel('%')
                axb1.set_title('Carrier load')
                plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                plt.draw()
                #
                axb2 = plt.subplot(3, 1, 2)
                axb2.plot(range(len(info)), max_allowed_REs_per_device, 'r-')
                axb2.set_ylabel('REs')
                axb2.set_title('Max allowed REs per device')
                plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                plt.draw()
                #
                n_mobiles_in_time.append(n_mobiles)
                n_connected_mobiles_in_time.append(n_mobiles)
                n_mobiles0_in_time.append(n_mobiles0)
                n_mobiles1_in_time.append(n_mobiles1)
                n_mobiles2_in_time.append(n_mobiles2)
                n_mobiles3_in_time.append(n_mobiles3)
                axb3 = plt.subplot(3, 1, 3)
                if len(n_mobiles_in_time) == 1:
                    axb3.plot(range(len(n_mobiles_in_time)), n_mobiles_in_time, 'k-', label="Total")
                    axb3.plot(range(len(n_connected_mobiles_in_time)), n_connected_mobiles_in_time, 'r-', label="Connected")
                    axb3.plot(range(len(n_mobiles0_in_time)), n_mobiles0_in_time, 'y-', label="Not connected")
                    axb3.plot(range(len(n_mobiles1_in_time)), n_mobiles1_in_time, 'g-', label="Connected without enough resources")
                    axb3.plot(range(len(n_mobiles2_in_time)), n_mobiles2_in_time, 'c-', label="Connected with enough resources")
                    axb3.plot(range(len(n_mobiles3_in_time)), n_mobiles3_in_time, 'b-', label="Connected with enough resources and low latency")
                    # axb3.legend(loc="upper left")
                else:
                    axb3.plot(range(len(n_mobiles_in_time)), n_mobiles_in_time, 'k-')
                    axb3.plot(range(len(n_connected_mobiles_in_time)), n_connected_mobiles_in_time, 'r-')
                    axb3.plot(range(len(n_mobiles0_in_time)), n_mobiles0_in_time, 'y-')
                    axb3.plot(range(len(n_mobiles1_in_time)), n_mobiles1_in_time, 'g-')
                    axb3.plot(range(len(n_mobiles2_in_time)), n_mobiles2_in_time, 'c-')
                    axb3.plot(range(len(n_mobiles3_in_time)), n_mobiles3_in_time, 'b-')
                axb3.set_ylabel('N º')
                axb3.set_xlabel('t (s)')
                axb3.set_title('Total devices')
                plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                plt.draw()

            figure = 3  # Figure number
            # Mobiles params plot
            for m in range(len(mobiles)):
                if mobiles[m].get_save():
                    # Get Mobile Info
                    info = mobiles[m].get_info()
                    RBs = [i['RBs'] for i in info]
                    REs = [i['REs'] for i in info]
                    BWP = [i['BWP'] for i in info]
                    DL_Prx = [i['DL_Prx'] for i in info]
                    UL_Ptx = [i['UL_Ptx'] for i in info]
                    DL_Ptx = [i['DL_Ptx'] for i in info]
                    UL_Prx = [i['UL_Prx'] for i in info]
                    DL_needed_datarate = [i['DL_needed_datarate'] for i in info]
                    DL_datarate = [i['DL_datarate'] for i in info]
                    DL_latency = [i['DL_latency'] for i in info]
                    DL_REs = [i['DL_REs'] for i in info]
                    DL_modulation = [i['DL_modulation'] for i in info]
                    UL_needed_datarate = [i['UL_needed_datarate'] for i in info]
                    UL_datarate = [i['UL_datarate'] for i in info]
                    UL_latency = [i['UL_latency'] for i in info]
                    UL_REs = [i['UL_REs'] for i in info]
                    UL_modulation = [i['UL_modulation'] for i in info]

                    # Plot Mobile Info
                    plt.figure(figure)
                    plt.tight_layout(pad=2.0)
                    plt.suptitle(f'Mobile {m}')
                    #
                    ax1 = plt.subplot(5, 2, 1)
                    ax1.plot(range(len(info)), DL_Prx, 'r-', label="Prx")
                    ax1.plot(range(len(info)), DL_Ptx, 'b-', label="Ptx")
                    if len(info) == 1:
                        ax1.legend(loc="upper left")
                    ax1.set_ylabel('P (dBm)')
                    ax1.set_title('Downlink')
                    ax1.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax2 = plt.subplot(5, 2, 2)
                    ax2.plot(range(len(info)), UL_Prx, 'r-', label="Prx")
                    ax2.plot(range(len(info)), UL_Ptx, 'b-', label="Ptx")
                    if len(info) == 1:
                        ax2.legend(loc="upper left")
                    ax2.set_ylabel('P (dBm)')
                    ax2.set_title('Uplink')
                    ax2.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax3 = plt.subplot(5, 2, 3)
                    ax3.plot(range(len(info)), DL_REs, 'r-')
                    ax3.set_ylabel('REs')
                    ax3.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax4 = plt.subplot(5, 2, 4)
                    ax4.plot(range(len(info)), UL_REs, 'r-')
                    ax4.set_ylabel('REs')
                    ax4.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax5 = plt.subplot(5, 2, 5)
                    ax5.plot(range(len(info)), DL_latency, 'r-')
                    ax5.set_ylabel('Latency (ms)')
                    ax5.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax6 = plt.subplot(5, 2, 6)
                    ax6.plot(range(len(info)), UL_latency, 'r-')
                    ax6.set_ylabel('Latency (ms)')
                    ax6.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax7 = plt.subplot(5, 2, 7)
                    ax7.plot(range(len(info)), DL_modulation, 'r-')
                    ax7.set_ylabel('Modulation')
                    ax7.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax8 = plt.subplot(5, 2, 8)
                    ax8.plot(range(len(info)), UL_modulation, 'r-')
                    ax8.set_ylabel('Modulation')
                    ax8.set_xticklabels([])
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    #
                    ax9 = plt.subplot(5, 2, 9)
                    ax9.plot(range(len(info)), DL_needed_datarate, 'r-', label="Needed")
                    ax9.plot(range(len(info)), DL_datarate, 'b-', label="Current")
                    if len(info) == 1:
                        ax9.legend(loc="upper left")
                    ax9.set_ylabel('Datarate (kbps)')
                    ax9.set_xlabel('t (s)')
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    plt.ticklabel_format(style='plain')
                    #
                    ax10 = plt.subplot(5, 2, 10)
                    ax10.plot(range(len(info)), UL_needed_datarate, 'r-', label="Needed")
                    ax10.plot(range(len(info)), UL_datarate, 'b-', label="Current")
                    if len(info) == 1:
                        ax10.legend(loc="upper left")
                    ax10.set_ylabel('Datarate (kbps)')
                    ax10.set_xlabel('t (s)')
                    plt.pause(0.100)  # Updates the plot once per 100 ms (equivalent to plt.show())
                    plt.draw()
                    plt.ticklabel_format(style='plain')
                    # Update the figure number for the next plot of mobile info
                    figure = figure + 1

            # Creating new mobiles
            for n in range(0, mobiles_connection_rate):
                mobile_id = n_mobiles
                n_mobiles = n_mobiles + 1
                mobiles.append(Mobile(random_number(-cell_size, cell_size), random_number(-cell_size, cell_size), 0, mobile_id, mobile_power_mw, mobile_antenna_gain, noise_spectral_density_mw_hz, random_number_between_args(mobile_categories), mobile_latency, subcarrier_spacing, step_simulation_time))

        # Update Time Reference
        step = step + 1


if __name__ == '__main__':
    main()
