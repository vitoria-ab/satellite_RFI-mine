import scipy.signal as ss
import numpy as np


def tophat_rect(f, fi, band, level, values):
    """
    Rectangular tophat function, https://en.wikipedia.org/wiki/Rectangular_function,
    f-frequency range;
    fi-central frequency;
    band-size of the bandwidth;
    level-value of the OOB region
    values-function values
    """

    fx = f < fi + band
    fy = f > fi - band
    idx = np.where(fx * fy == True)[0]

    return np.array([x if i in idx else x * level for i, x in enumerate(values)])


# ---------------------------------------------------------------- #


def gaussian_taper(x, a, b, c):
    """
    Gaussian function for the G_oob function.
    x - values
    a - amplitude
    b - central value
    c - sigma
    """
    return a * np.e ** (-((x - b) ** 2) / (2 * c ** 2))


def gaussian_oob(f, fi, band, sigma, values):
    """
    Creates a guassian rectangular window function where any values outside of the band follows a gaussian:
    f-frequency or x values
    fi-central frequency value
    sigma-the rate of the decline
    values-the y values
    """
    f_high = f < fi + band
    f_low = f > fi - band

    idx_high = np.where(f_high == False)[0]
    idx_low = np.where(f_low == False)[0]

    try:
        value_high = gaussian_taper(
            x=f[idx_high], a=values[idx_high[0] - 1], b=f[idx_high][0], c=sigma
        )  # Looking at high side of gaussian tale
        value_low = gaussian_taper(
            x=f[idx_low], a=values[idx_low[-1] + 1], b=f[idx_low][0], c=sigma
        )[::-1]

    except IndexError:
        try:
            value_high = gaussian_taper(
                x=f[idx_high], a=values[idx_high[0]], b=f[idx_high][0], c=sigma
            )  # Changed the positioning of the data

        except IndexError:
            value_low = gaussian_taper(
                x=f[idx_low], a=values[idx_low[-1]], b=f[idx_low][0], c=sigma
            )[::-1]

    new_vals = []
    for i, x in enumerate(values):
        if i in idx_low:
            new_vals.append(value_low[i])
        elif i in idx_high:
            new_vals.append(value_high[i - idx_high[0]])
        else:
            new_vals.append(x)

    return np.array(new_vals)
