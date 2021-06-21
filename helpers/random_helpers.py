from random import random
from scipy import special as sp
import math


# Returns a random number between n1 and n2
def random_number(n1, n2):
    if n1 > n2:
        numerical_width = n1 - n2
        return numerical_width * random() + n2
    elif n1 < n2:
        numerical_width = n2 - n1
        return numerical_width * random() + n1
    elif n1 == n2:
        return 0


def random_number_between_args(*args):
    num = math.floor(random_number(0, len(args[0])))
    return args[0][num]


def q_function(x):
    return 0.5 - 0.5 * sp.erf(x/math.sqrt(2))

