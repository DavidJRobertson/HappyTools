import numpy as np
import math


def gauss_function(x, *p):
    """Define and return a Gaussian function.

    This function returns the value of a Gaussian function, using the
    a, mu and sigma value that is provided as *p.

    Keyword arguments:
    x -- number
    p -- a, mu and sigma numbers
    """
    a, mu, sigma = p
    return a * np.exp(-(x - mu) ** 2 / (2. * sigma ** 2))


def power_law(x, a, b, c):
    penalty = 0
    if b > 2.0:
        penalty = abs(b - 1.0) * 10000
    if b < 0.0:
        penalty = abs(2.0 - b) * 10000
    return a * x ** b + c + penalty


def fwhm(coeff):
    """Calculate the Full-Width at Half Maximum

    This function will calculate the FWHM based on the following formula
    fwhm = 2*sigma*sqrt(2*ln(2)).

    Arguments:
    coeff -- coefficients as calculated by SciPy curve_fit
    """
    return abs(2 * coeff[2] * math.sqrt(2 * math.log(2)))


def hwhm(coeff):
    """Calculate the Half-Width at Half Maximum

    This function will calculate the HWHM based on the following formula
    HWHM = sigma*sqrt(2*ln(2)).

    Arguments:
    coeff -- coefficients as calculated by SciPy curve_fit
    """
    return fwhm(coeff) * 0.5


def peak_centre(coeff):
    return coeff[1]
