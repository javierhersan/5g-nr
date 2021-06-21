import math
import random
from .random_helpers import q_function


# Returns attenuation in free space (u.l.) -> distance (m), frequency (Hz)
def free_space_attenuation(distance, frequency):
    wavelength = (3 * (10 ** 8)) / frequency
    return (wavelength / (4 * math.pi * distance)) ** 2


# Returns attenuation in Rec. P.1411 (u.l.) -> distance (m), frequency (Hz)
def model_attenuation(distance, frequency):
    alpha = 2.12
    beta = 29.2
    gamma = 2.11
    mu = 0  # Gaussian mean
    sigma = 5.06  # Gaussian standard deviation
    att_dB = -((10 * alpha * math.log(distance, 10)) + beta + (10 * gamma * math.log(frequency * (10 ** (-9)), 10)) + random.gauss(mu, sigma))
    att_ul = 10 ** (att_dB / 10)
    return att_ul


def propagation_delay(distance):
    return distance / (3 * (10 ** 8))


def distance(mobile, base_station):
    return math.sqrt((mobile.get_x()-base_station.get_x())**2 + (mobile.get_y()-base_station.get_y())**2 + (mobile.get_z()-base_station.get_z())**2)


# Best modulation
def modulation(received_power, noise_power_spectral_density, subcarrier_spacing):
    subcarrier_spacing = subcarrier_spacing * (10**6)
    received_power_dbm = 10 * math.log(received_power, 10)  # dBm
    noise_power = noise_power_spectral_density * subcarrier_spacing  # u.l.
    noise_power_dbm = 10 * math.log(noise_power, 10)  # dBm
    interference_power_dbm = 3  # dBm -> Interference and impairments
    SINR = received_power_dbm - (noise_power_dbm + interference_power_dbm)
    SE = math.log(1 + SINR, 2)
    SE_eff = math.floor(SE)
    if SE_eff < 1:
        # modulation = 0  # None
        modulation = 2  # Should be zero modulation but we dont want any problems we dont have time
    elif SE_eff < 2:
        modulation = 2  # PI/2-BPSK
    elif SE_eff < 3:
        modulation = 4  # QAM or QPSK
    elif SE_eff < 4:
        modulation = 16  # 16-QAM
    elif SE_eff < 5:
        modulation = 64  # 64-QAM
    else:
        modulation = 256  # 256 -QAM
    return modulation
