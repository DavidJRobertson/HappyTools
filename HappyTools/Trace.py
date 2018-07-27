import re
import sys

import numpy as np
from scipy.signal import *
import operator

from settings import slicepoints, noise


class Trace(object):
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_file(cls, file):
        data = []
        with open(file, 'r') as fr:
            if '.txt' in file:
                for line in fr:
                    if line[0].isdigit():
                        lineChunks = line.strip().split()
                        # Number based regex splitting to get rid of thousand separators
                        time_sep = re.sub(r'-?\d', '', lineChunks[0], flags=re.U)
                        for sep in time_sep[:-1]:
                            lineChunks[0] = lineChunks[0].replace(sep, '')
                        if time_sep:
                            lineChunks[0] = lineChunks[0].replace(time_sep[-1], '.')
                        int_sep = re.sub(r'-?\d', '', lineChunks[-1], flags=re.U)
                        for sep in int_sep[:-1]:
                            lineChunks[-1] = lineChunks[-1].replace(sep[-1], '')
                        if int_sep:
                            lineChunks[-1] = lineChunks[-1].replace(int_sep[-1], '.')
                        # End of regex based splitting
                        try:
                            data.append((float(lineChunks[0]), float(lineChunks[-1])))
                        except UnicodeEncodeError:
                            print("Omitting line: " + str(line))
            elif '.arw' in file:
                for line in fr:
                    lines = line.split('\r')
                for line in lines:
                    try:
                        if not line[0][0].isdigit():
                            pass
                        else:
                            chunks = line.rstrip()
                            chunks = chunks.split()
                            data.append((float(chunks[0]), float(chunks[1])))
                    except IndexError:
                        pass
            else:
                print("Incorrect input file format, please choose a raw data 'txt' or 'arw' file.")
        return cls(data)

    def plot(self, fig, canvas, label):
        x_array = []
        y_array = []
        for i in self.data:
            x_array.append(i[0])
            y_array.append(i[1])
        fig.clear()
        axes = fig.add_subplot(111)
        laxes.plot(x_array, y_array, label=label)
        handles, labels = axes.get_legend_handles_labels()
        fig.legend(handles, labels)
        axes.get_xaxis().get_major_formatter().set_useOffset(False)
        axes.set_xlabel("Time [m]")
        axes.set_ylabel("Intensity [au]")
        canvas.draw()

    def background_noise(self):
        """Return the background and noise.

        This function determines the average and the standard deviation or
        the maximum difference of all segments of data, where each segment
        has the length specified in the slice points parameter.
        """
        background = sys.maxsize
        curr_noise = 0
        for index, i in enumerate(self.data[:-slicepoints]):
            buffer = self.data[index:index + slicepoints]
            if np.mean(buffer) < background:
                background = np.mean(buffer)
                if noise == "MM":
                    curr_noise = max(buffer) - min(buffer)
                elif noise == "RMS":
                    curr_noise = np.std(buffer)
        if curr_noise == 0:
            curr_noise = 1
        return {'Background': background, 'Noise': curr_noise}

    def smoothChrom(self):

        time, intensity = list(zip(*self.data[0][1]))
        new = savgol_filter(intensity, 21, 3)
        new_data = list(zip(time, new))

        # Plot & Write Data to Disk
        multiData = [(os.path.split(self.data[0][0])[-1], self.data[0][1]),
                     (os.path.split(self.data[0][0])[-1] + " (Smoothed)", new_data)]
        plotMultiData(fig, canvas, multiData)
        writeData(new_data, os.path.split(self.data[0][0])[-1] + " (Smoothed)")

    def detect_baseline(self, points, start, end, baseline_order):
        """Detect the baseline

        This function determines the baseline of a chromatogram between two time points, specified with the start and
        end parameter. The chromatogram is split into segments of a length specified in the points parameter. The lowest
        intensity of each segment is used to determine a function of the order specified in the baseline_order using the
        numpy.polyfit function.

        Returns a callable polynomial object
        """
        background = []

        chunks = [ self.data[0][1][x:x + points] for x in range(0, len(self.data[0][1]), points) ]
        for i in chunks:
            buff1, buff2 = list(zip(*i))
            min_index, min_value = min(enumerate(buff2), key=operator.itemgetter(1))
            if buff1[0] > start and buff1[-1] < end:
                background.append((buff1[min_index], buff2[min_index]))

        time, intensity = list(zip(*background))
        coefficients = np.polyfit(time, intensity, baseline_order)
        return np.poly1d(coefficients)

    def baseline_correction(self, fig, canvas):
        """Perform baseline correction and draw the corrected chromatogram.
...
        The original chromatogram is then transformed by subtracting the function
        from the original data.

        The resulting chromatogram might have negative intensities between the
        start and end time points -  the minimum intensity within that region
        is used to uplift the entire chromatogram. The transformed and
        uplifted chromatogram is written to disk and plotted together with
        the original chromatogram on the canvas.

        Keyword arguments:
        fig -- matplotlib figure object
        canvas -- tkinter canvas object
        """
        ...

        # Transform
        time = [a for a, b in self.data[0][1]]
        new_chrom_intensity = [b - p(a) for a, b in self.data[0][1]]

        # Uplift
        low = bisect.bisect_left(time, start)
        high = bisect.bisect_right(time, end)
        offset = abs(min(min(new_chrom_intensity[low:high]), 0))
        new_data = list(zip(time, [x + offset for x in new_chrom_intensity]))


