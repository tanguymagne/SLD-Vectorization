import numpy as np
from numba import jit


@jit(nopython=True)
def _eval(t, P1, P2, P3, P4):
    t = t.reshape(-1, 1)
    return (1 - t) ** 3 * P1 + 3 * (1 - t) ** 2 * t * P2 + 3 * (1 - t) * t**2 * P3 + t**3 * P4


@jit(nopython=True)
def _eval_prime(t, P1, P2, P3, P4):
    t = t.reshape(-1, 1)
    return 3 * (1 - t) ** 2 * (P2 - P1) + 6 * (1 - t) * t * (P3 - P2) + 3 * t**2 * (P4 - P3)


@jit(nopython=True)
def _compute_arc_length(pos):
    diff = pos[1:] - pos[:-1]
    distances = np.sqrt(np.sum(diff**2, axis=1))
    arc_length = np.cumsum(distances)
    return arc_length


@jit(nopython=True)
def precompute_arc_length_bezier(P1, P2, P3, P4, n=10000):
    t = np.linspace(0, 1, n)
    pos = _eval(t, P1, P2, P3, P4)

    temporal = t
    arc_length = np.zeros(len(t))
    arc_length[1:] = _compute_arc_length(pos)
    return temporal, arc_length


class CubicBezier:
    def __init__(self, P1, P2, P3, P4, n=10000):
        self.P1 = np.array(P1).reshape(1, -1)
        self.P2 = np.array(P2).reshape(1, -1)
        self.P3 = np.array(P3).reshape(1, -1)
        self.P4 = np.array(P4).reshape(1, -1)

        self.precompute_arc_length_parameterization(n)

    @classmethod
    def from_list(cls, l, n=10000):
        return cls(l[0], l[1], l[2], l[3], n=n)

    def eval(self, t):
        return _eval(t, self.P1, self.P2, self.P3, self.P4)

    def eval_prime(self, t):
        return _eval_prime(t, self.P1, self.P2, self.P3, self.P4)

    def eval_prime_prime(self, t):
        t = np.array(t).reshape(-1, 1)
        return 6 * (1 - t) * (self.P3 - 2 * self.P2 + self.P1) + 6 * t * (
            self.P4 - 2 * self.P3 + self.P2
        )

    def eval_curvature(self, t):
        t = np.array(t).reshape(-1, 1)
        prime = self.eval_prime(t)
        prime_prime = self.eval_prime_prime(t)
        return (prime_prime[:, 0] * prime[:, 1] - prime_prime[:, 1] * prime[:, 0]) / np.linalg.norm(
            prime, axis=1
        ) ** 3

    def precompute_arc_length_parameterization(self, n=10000):
        self.temporal, self.arc_length = precompute_arc_length_bezier(
            self.P1, self.P2, self.P3, self.P4, n
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
