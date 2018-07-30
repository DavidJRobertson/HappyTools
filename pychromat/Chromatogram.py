import os
from Trace import Trace


class Chromatogram(object):
    """ The Chromatogram class encapsulates a collection of traces on the same timebase """

    def __init__(self, filename):
        self.filename = filename
        raw = Trace.from_file(self.filename)
        self.traces = {
            'raw': raw
        }
        self.last_trace = raw

        self.time_units = "min"
        self.intensity_metric = "Absorbance"
        self.intensity_units = "mAU"

    def x_range(self, trace="raw"):
        return self.traces[trace].x_range()

    def y_range(self, trace="raw"):
        return self.traces[trace].y_range()

    def smooth(self):
        new_trace = self.last_trace.smooth()
        self.traces['smoothed'] = new_trace
        self.last_trace = new_trace

    def detect_baseline(self):
        new_trace = self.last_trace.detect_baseline()
        self.traces['baseline'] = new_trace

    def correct_baseline(self):
        new_trace = self.last_trace.correct_baseline()
        self.traces['corrected-baseline'] = new_trace
        self.last_trace = new_trace