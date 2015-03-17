__author__ = 'noe'

import unittest
import numpy as np

from timescales import ImpliedTimescales
from pyemma.msm.generation import generate_traj
from pyemma.msm.analysis import timescales

class ImpliedTimescalesTest(unittest.TestCase):

    def setUp(self):
        self.dtrajs = []

        # simple case
        dtraj_simple = [0,1,1,1,0]
        self.dtrajs.append([dtraj_simple])

        # as ndarray
        self.dtrajs.append([np.array(dtraj_simple)])

        dtraj_disc = [0,1,1,0,0]
        self.dtrajs.append([dtraj_disc])

        # multitrajectory case
        self.dtrajs.append([[0],[1,1,1,1],[0,1,1,1,0],[0,1,0,1,0,1,0,1]])

        # large-scale case
        large_trajs = []
        for i in range(10):
            large_trajs.append(np.random.randint(10, size=1000))
        self.dtrajs.append(large_trajs)

        # Markovian timeseries with timescale about 5
        self.P2 = np.array([[0.9, 0.1],[0.1, 0.9]])
        self.dtraj2 = generate_traj(self.P2, 1000)
        self.dtrajs.append([self.dtraj2])

        # Markovian timeseries with timescale about 5
        self.P4 = np.array([[0.95,  0.05,  0.0, 0.0],
                            [0.05, 0.93, 0.02, 0.0],
                            [0.0, 0.02, 0.93, 0.05],
                            [0.0,  0.0,  0.05, 0.95]])
        self.dtraj4_2 = generate_traj(self.P4, 20000)
        I = [0, 0, 1, 1] # coarse-graining
        for i in range(len(self.dtraj4_2)):
            self.dtraj4_2[i] = I[self.dtraj4_2[i]]
        self.dtrajs.append([self.dtraj4_2])
        print "T4 ", timescales(self.P4)[1]


    def compute_nice(self, reversible):
        """
        Tests if standard its estimates run without errors

        :return:
        """
        for i in range(len(self.dtrajs)):
            its = ImpliedTimescales(self.dtrajs[i], reversible=reversible)
            #print its.get_lagtimes()
            #print its.get_timescales()


    def test_nice_sliding_rev(self):
        """
        Tests if nonreversible sliding estimate runs without errors
        :return:
        """
        self.compute_nice(True)

    def test_nice_sliding_nonrev(self):
        """
        Tests if nonreversible sliding estimate runs without errors
        :return:
        """
        self.compute_nice(False)

    def test_too_large_lagtime(self):
        dtraj = [[0,1,1,1,0]]
        lags  = [1,2,3,4,5,6,7,8]
        expected_lags = [1,2,3] # 4 is impossible because only one state remains and no finite timescales.
        its = ImpliedTimescales(dtraj, lags=lags, reversible=False)
        got_lags = its.lagtimes
        assert(np.shape(got_lags) == np.shape(expected_lags))
        assert(np.allclose(got_lags, expected_lags))

    def test_2(self):
        t2 = timescales(self.P2)[1]
        lags = [1,2,3,4,5]
        its = ImpliedTimescales([self.dtraj2], lags=lags)
        est = its.get_timescales(0)
        assert(np.alltrue(est < t2+2.0))
        assert(np.alltrue(est > t2-2.0))

    def test_4_2(self):
        t4 = timescales(self.P4)[1]
        lags = [int(t4)]
        its = ImpliedTimescales([self.dtraj4_2], lags=lags)
        est = its.get_timescales(0)
        assert(np.alltrue(est < t4+15.0))
        assert(np.alltrue(est > t4-15.0))

if __name__ == "__main__":
    unittest.main()