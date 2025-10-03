from typing import Tuple

import numpy as np
from numpy import asarray, split, sum, unique
from scipy.interpolate import insert


def b_spline_to_bezier_series(tck: Tuple, per: bool = False) -> np.array:
    """Convert a parametric b-spline into a sequence of Bezier curves of the same degree.
    This was taken from # https://stackoverflow.com/a/22734164/22851577

    Inputs:
      tck : (t,c,k) tuple of b-spline knots, coefficients, and degree returned by splprep.
      per : if tck was created as a periodic spline, per *must* be true, else per *must* be false.

    Output:
      A list of Bezier curves of degree k that is equivalent to the input spline.
      Each Bezier curve is an array of shape (k+1,d) where d is the dimension of the
      space; thus the curve includes the starting point, the k-1 internal control
      points, and the endpoint, where each point is of d dimensions.
    """

    t, c, k = tck
    t = asarray(t)
    try:
        c[0][0]
    except Exception:
        # I can't figure out a simple way to convert nonparametric splines to
        # parametric splines. Oh well.
        raise TypeError("Only parametric b-splines are supported.")
    new_tck = tck
    if per:
        # ignore the leading and trailing k knots that exist to enforce periodicity
        knots_to_consider = unique(t[k:-k])
    else:
        # the first and last k+1 knots are identical in the non-periodic case, so
        # no need to consider them when increasing the knot multiplicities below
        knots_to_consider = unique(t[k + 1 : -k - 1])
    # For each unique knot, bring it's multiplicity up to the next multiple of k+1
    # This removes all continuity constraints between each of the original knots,
    # creating a set of independent Bezier curves.
    desired_multiplicity = k + 1
    for x in knots_to_consider:
        current_multiplicity = sum(t == x)
        remainder = current_multiplicity % desired_multiplicity
        if remainder != 0:
            # add enough knots to bring the current multiplicity up to the desired multiplicity
            number_to_insert = desired_multiplicity - remainder
            new_tck = insert(x, new_tck, number_to_insert, per)
    tt, cc, kk = new_tck
    # strip off the last k+1 knots, as they are redundant after knot insertion if there is some
    # knot insertion
    if len(knots_to_consider) > 0:
        bezier_points = np.transpose(cc)[:-desired_multiplicity]
    else:
        bezier_points = np.transpose(cc)
    if per:
        # again, ignore the leading and trailing k knots
        bezier_points = bezier_points[k:-k]
    # group the points into the desired bezier curves
    return split(bezier_points, len(bezier_points) / desired_multiplicity, axis=0)
