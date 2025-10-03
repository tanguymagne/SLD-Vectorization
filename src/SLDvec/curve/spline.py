import numpy as np

from SLDvec.curve.bezier import CubicBezier


class Spline:
    def __init__(self, points, n=10000):
        """Create a MultiBezier object from a list of points.
        The list of points is a list of list of points, each list of points
        represents a bezier curve and contains 4 controls points."""

        self.beziers = np.array([CubicBezier.from_list(p, n) for p in points])
        self.n_beziers = len(self.beziers)

        self.precompute_arc_length_parameterization(n)

    def eval(self, t):
        t = np.array(t).reshape(-1, 1)
        t[-1] -= np.finfo(float).eps

        t = t * self.n_beziers  # t is between 0 and n_beziers
        idx = t.astype(int)  # get the index of the bezier curve to sample from
        t = t - idx  # get the t value in the bezier curve coordinates

        res = []
        for i in range(self.n_beziers):
            res.extend(self.beziers[i].eval(t[idx == i]))
        return np.array(res)

    def eval_prime(self, t):
        t = np.array(t).reshape(-1, 1)
        t[-1] -= np.finfo(float).eps

        t = t * self.n_beziers  # t is between 0 and n_beziers
        idx = t.astype(int)  # get the index of the bezier curve to sample from
        t = t - idx  # get the t value in the bezier curve coordinates

        res = []
        for i in range(self.n_beziers):
            res.extend(self.beziers[i].eval_prime(t[idx == i]))
        return np.array(res)

    def eval_prime_prime(self, t):
        t = np.array(t).reshape(-1, 1)
        t[-1] -= np.finfo(float).eps

        t = t * self.n_beziers  # t is between 0 and n_beziers
        idx = t.astype(int)  # get the index of the bezier curve to sample from
        t = t - idx  # get the t value in the bezier curve coordinates

        res = []
        for i in range(self.n_beziers):
            res.extend(self.beziers[i].eval_prime_prime(t[idx == i]))
        return np.array(res)

    def eval_curvature(self, t):
        t = np.array(t).reshape(-1, 1)
        t[-1] -= np.finfo(float).eps

        t = t * self.n_beziers  # t is between 0 and n_beziers
        idx = t.astype(int)  # get the index of the bezier curve to sample from
        t = t - idx  # get the t value in the bezier curve coordinates

        res = []
        for i in range(self.n_beziers):
            res.extend(self.beziers[i].eval_curvature(t[idx == i]))
        return np.array(res)

    @staticmethod
    def __precompute_arc_length_parameterization(all_arc_length, all_t, n):
        n_curve = len(all_arc_length)
        arc_length = np.zeros(n_curve * (n - 1) + 1)
        t = np.zeros(n_curve * (n - 1) + 1)

        for i, (_arc_length, _t) in enumerate(zip(all_arc_length, all_t)):
            offset = arc_length[i * (n - 1)]
            arc_length[i * (n - 1) + 1 : (i + 1) * (n - 1) + 1] = _arc_length[1:] + offset

            offset_t = t[i * (n - 1)]
            t[i * (n - 1) + 1 : (i + 1) * (n - 1) + 1] = _t[1:] + offset_t

        t /= t[-1]
        return arc_length, t

    def precompute_arc_length_parameterization(self, n):
        all_arc_length = [bez.arc_length for bez in self.beziers]
        all_t = [bez.temporal for bez in self.beziers]

        self.arc_length, self.temporal = Spline.__precompute_arc_length_parameterization(
            all_arc_length, all_t, n
        )

    def get_corresponding_time_coordinate(self, arc_parameter):
        return np.interp(arc_parameter, self.arc_length / self.length(), self.temporal)

    def eval_at_arc_length(self, a):
        t = self.get_corresponding_time_coordinate(a)
        return self.eval(t)

    def eval_prime_at_arc_length(self, a):
        t = self.get_corresponding_time_coordinate(a)
        return self.eval_prime(t)

    def eval_prime_prime_at_arc_length(self, a):
        t = self.get_corresponding_time_coordinate(a)
        return self.eval_prime_prime(t)

    def eval_curvature_at_arc_length(self, a):
        t = self.get_corresponding_time_coordinate(a)
        return self.eval_curvature(t)

    def length(self):
        return self.arc_length[-1]
