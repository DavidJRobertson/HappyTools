import bisect
import operator
import sys
import numpy as np
import scipy
import scipy.interpolate
import scipy.signal
import scipy.optimize
import util


class Trace(object):
    DATA_TYPE = np.dtype([('x', np.float64), ('y', np.float64)])

    def __init__(self, data):
        self.data = data
        self.x = data['x']
        self.y = data['y']

    @classmethod
    def from_xy(cls, x, y):
        data = np.zeros(len(x), dtype=cls.DATA_TYPE)
        data['x'] = x
        data['y'] = y
        return cls(data)

    @classmethod
    def from_file_txt(cls, file, x_col=0, y_col=1, sep="\t"):
        header_length = 0
        with open(file, 'r') as fr:
            for line in fr:
                if line[0].isdigit():
                    break
                header_length += 1

        data = np.genfromtxt(file, delimiter=sep, skip_header=header_length, usecols=(x_col, y_col), dtype=cls.DATA_TYPE)

        return cls(data)

    @classmethod
    def from_file(cls, file):
        if '.txt' in file:
            return cls.from_file_txt(file, x_col=0, y_col=2)
        elif '.csv' in file:
            return cls.from_file_txt(file, x_col=1, y_col=2)
        elif '.arw' in file:
            print("NOT IMPLEMENTED")
        else:
            print("Incorrect input file format, please choose a raw data 'txt' or 'arw' file.")

    def x_range(self):
        return min(self.x), max(self.x)

    def y_range(self):
        return min(self.y), max(self.y)

    def background_noise(self, slice_points=5, noise_method="RMS"):
        """Return the background and noise.

        This function determines the average and the standard deviation or
        the maximum difference of all segments of data, where each segmwent
        has the length specified in the slice points parameter.
        """
        background = sys.maxsize
        noise = 0
        for index in range(len(self.data) - slice_points):
            segment = self.y[index:(index + slice_points)]

            if np.mean(segment) < background:
                background = np.mean(segment)

                if noise_method == "MM":
                    noise = max(segment) - min(segment)
                elif noise_method == "RMS":
                    noise = np.std(segment)
        if noise == 0:
            noise = 1
        return background, noise

    def smooth(self, window_length=21, order=3):
        """ Returns a new Trace which has been smoothed """
        new_y = scipy.signal.savgol_filter(self.y, window_length, order)
        return Trace.from_xy(self.x, new_y)

    def detect_baseline(self, points=250, order=3):
        """Detect the baseline

        This function determines the baseline of a chromatogram.
        The chromatogram is split into segments of a length specified in the points parameter. The lowest
        intensity of each segment is used to determine a function of the order specified in the baseline_order using the
        numpy.polyfit function.

        Returns a new trace representing the baseline
        """
        background = []
        chunks = [self.data[x:(x + points)] for x in range(0, len(self.data), points)]
        for chunk in chunks:
            chunk_x = chunk['x']
            chunk_y = chunk['y']
            min_index, min_value = min(enumerate(chunk_y), key=operator.itemgetter(1))
            background.append((chunk_x[min_index], chunk_y[min_index]))
        background = np.asarray(background)

        coefficients = np.polyfit(background[:, 0], background[:, 1], order)
        poly = np.poly1d(coefficients)

        return Trace.from_xy(self.x, poly(self.x))

    def correct_baseline(self, points=250, order=3):
        """ Returns a new Trace having the baseline corrected """
        baseline_trace = self.detect_baseline(points, order)
        new_y = self.y - baseline_trace.y
        new_y -= min(new_y)
        return Trace.from_xy(self.x, new_y)

    def detect_peaks(self, peak_detection_min=0.001, peak_detection_edge="FWHM", peakDetectionEdgeValue=1):
        """Detect all peaks in the currently active chromatogram.

        This function performs peak detection by fitting a Gaussian function
        through the highest data points in a chromatogram. The fitted
        function is then subtracted from the original data to yield a
        chromatogram without the removed analyte, after which this process
        is repeated until the highest datapoint falls below the specified
        cut-off (determined by comparing the intensity of the most intense
        analyte in the original data with the intensity of the most intense
        analyte in the current (residual) data).

        The peak detection is based on the assumption that the first
        derivative of the data is 0 at a local maxima or minima.
        """

        # Determine the background
        background, noise = self.background_noise()

        # Determine the local maxima and minima, using first order derivative
        f = scipy.interpolate.InterpolatedUnivariateSpline(self.x, self.y)
        f_prime = f.derivative()

        new_x = np.linspace(self.x[0], self.x[-1], 25000 * (self.x[-1] - self.x[0]))
        new_y = f(new_x)
        new_prime_y = f_prime(new_x)
        maxima = scipy.signal.argrelextrema(new_prime_y, np.greater)
        minima = scipy.signal.argrelextrema(new_prime_y, np.less)
        breaks = maxima[0].tolist() + minima[0].tolist()
        breaks = sorted(breaks)

        # Determine the maximum full peak, for the cut-off
        max_intensity = 0
        for func in range(0, len(breaks) - 2):
            max_intensity = max(max(new_y[breaks[func]:breaks[func + 1]]), max_intensity)
        cutoff = peak_detection_min * (max_intensity - max(background, 0))

        # Detect peaks
        functions = []
        counter = 0
        x_data = new_x.copy()
        y_data = new_y.copy()
        while (max(y_data) - background) > cutoff:
            counter += 1
            print("Fitting peak: " + str(counter))

            f = scipy.interpolate.InterpolatedUnivariateSpline(x_data, y_data)
            f_prime = f.derivative()
            new_y = f(new_x)
            new_prime_y = f_prime(new_x)
            maxima = scipy.signal.argrelextrema(new_prime_y, np.greater)
            minima = scipy.signal.argrelextrema(new_prime_y, np.less)
            breaks = maxima[0].tolist() + minima[0].tolist()
            breaks = sorted(breaks)
            print('b0 = ' + str(breaks[0]))

            # Subset the data
            max_point = 0
            # # Region from new_y[0] to breaks[0]
            # print(len(x_data))
            # try:
            #     if max(new_y[0:breaks[0]]) > max_point:
            #         max_point = max(new_y[0:breaks[0]])
            #         x_data = new_x[0:breaks[0]]
            #         y_data = new_y[0:breaks[0]] - background
            # except IndexError:
            #     pass
            # print(len(x_data))
            # # Regions between breaks[x] and breaks[x+1]
            # try:
            #     for index, j in enumerate(breaks):
            #         if max(new_y[breaks[index]:breaks[index + 1]]) > max_point:
            #             pass
            #             max_point = max(new_y[breaks[index]:breaks[index + 1]])
            #             x_data = new_x[breaks[index]:breaks[index + 1]]
            #             y_data = new_y[breaks[index]:breaks[index + 1]] - max(background, 0)
            # except IndexError:
            #     pass
            # print(len(x_data))
            # # Region from break[-1] to newY[-1]
            # try:
            #     if max(new_y[breaks[-1]:-1]) > max_point:
            #         max_point = max(new_y[breaks[-1]:-1])
            #         x_data = new_x[breaks[-1]:-1]
            #         y_data = new_y[breaks[-1]:-1] - background
            # except IndexError:
            #     pass

            print(len(x_data))

            # Gaussian fit on main points
            peak = x_data[y_data > np.exp(-0.5) * max(y_data)]
            guess_sigma = 0.5 * (max(peak) - min(peak))

            p0 = (np.max(y_data), x_data[np.argmax(y_data)], guess_sigma)
            print(p0)
            coeff, var_matrix = scipy.optimize.curve_fit(util.gauss_function, x_data, y_data, p0)
            new_gauss_x = np.linspace(x_data[0], x_data[-1], 2500 * (x_data[-1] - x_data[0]))
            new_gauss_y = util.gauss_function(new_gauss_x, *coeff)

            # Limit the peak to either FWHM or a user specified Sigma value
            if peak_detection_edge == "FWHM":
                hwhm = util.hwhm(coeff)
                low = bisect.bisect_left(new_gauss_x, coeff[1] - hwhm)
                high = bisect.bisect_right(new_gauss_x, coeff[1] + hwhm)
                new_gauss_x = new_gauss_x[low:high]
                new_gauss_y = new_gauss_y[low:high]

            elif peak_detection_edge == "Sigma":
                low = bisect.bisect_left(new_gauss_x, coeff[1] - peakDetectionEdgeValue * abs(coeff[2]))
                high = bisect.bisect_right(new_gauss_x, coeff[1] + peakDetectionEdgeValue * abs(coeff[2]))
                try:
                    new_gauss_x = new_gauss_x[low:high]
                    new_gauss_y = new_gauss_y[low:high]
                except:
                    pass

            # Ignore breaks (f'(x) == 0) that did not match any data (reword this)
            if new_gauss_x.any():
                data = np.zeros(len(new_gauss_x), dtype=self.DATA_TYPE)
                data['x'] = new_gauss_x
                data['y'] = new_gauss_y
                functions.append({
                    'Peak': new_gauss_x[np.argmax(new_gauss_y)],
                    'Data': data,
                    'FWHM': util.fwhm(coeff)
                })

            # Subtract the fitted Gaussian from the raw or intermediate data and repeat the peak detection step.
            gauss_y = util.gauss_function(x_data, *coeff)
            new_y = y_data - gauss_y
            if max(new_y) == max(y_data):
                break
            y_data = new_y

        functions = sorted(functions, key=lambda d: d['Peak'])


        # iterate over all peaks and remove overlap
        overlap_detected = False
        for index, func in enumerate(functions):
            if (index+1) < len(functions) and len(func['Data']) > 0 and func['Data'][-1]['x'] > functions[index + 1]['Data'][0]['x']:
                overlap_detected = True
                overlap = abs(functions[index + 1]['Data'][0]['x'] - func['Data'][-1]['x'])
                peak1 = max(func['Data']['y'])
                peak2 = max(functions[index + 1]['Data']['y'])
                peak1fraction = (peak1 / (peak1 + peak2)) * overlap
                peak2fraction = (peak2 / (peak1 + peak2)) * overlap
                low = bisect.bisect_right(func['Data']['x'], func['Data'][-1]['x'] - peak2fraction)
                high = bisect.bisect_left(functions[index + 1]['Data']['x'],
                                          functions[index + 1]['Data'][0]['x'] + peak1fraction)
                func['Data'] = func['Data'][0:low]
                functions[index + 1]['Data'] = functions[index + 1]['Data'][high:-1]

        # Determine calibrants
        # calibrants = determineCalibrants(functions)

        # Writing to temp folder
        with open('annotation.ref', 'w') as fw:
            fw.write("Peak\tRT\tWindow\n")
            for index, analyte in enumerate(functions):
                if len(analyte['Data']) > 0:
                    window = 0.5 * (float(analyte['Data'][-1]["x"]) - float(analyte['Data'][0]["x"]))
                    center = float(analyte['Data'][0]["x"]) + 0.5 * window
                    fw.write(str("%.2f" % analyte['Peak']) + "\t" +
                             str("%.2f" % center) + "\t" +
                             str("%.2f" % window) + "\n")

        # with open('calibrants.ref', 'w') as fw:
        #     fw.write("Peak\tRT\tWindow\n")
        #     for index, analyte in enumerate(calibrants):
        #         window = 0.5 * (float(analyte['Data'][-1][0]) - float(analyte['Data'][0][0]))
        #         center = float(analyte['Data'][0][0]) + 0.5 * window
        #         fw.write(
        #             str("%.2f" % analyte['Peak']) + "\t" + str("%.2f" % center) + "\t" + str("%.2f" % window) + "\n")

        # Plotting
        # fig.clear()
        # axes = fig.add_subplot(111)
        # axes.plot(orig_x, orig_y, 'b', alpha=0.5)
        # for index, func in enumerate(functions):
        #     try:
        #         xd, yd = list(zip(*func['Data']))
        #         axes.plot(xd, yd, label=str(index + 1) + ": " + str("%.2f" % func['Peak']))
        #         axes.fill_between(xd, 0, yd, alpha=0.2)
        #     except ValueError:
        #         pass
        # for index, func in enumerate(calibrants):
        #     try:
        #         xd, yd = list(zip(*func['Data']))
        #         axes.annotate('Cal: ' + str(index), xy=(xd[yd.index(max(yd))], max(yd)),
        #                       xytext=(xd[yd.index(max(yd))], max(yd)),
        #                       arrowprops=dict(facecolor='black', shrink=0.05))
        #     except ValueError:
        #         pass
        # axes.set_xlabel("Time [m]")
        # axes.set_ylabel("Intensity [au]")
        # handles, labels = axes.get_legend_handles_labels()
        # fig.legend(handles, labels)
        # canvas.draw()

        # Warn (if needed)
        if overlap_detected:
            print("Overlap detected!!")
            # tkinter.messagebox.showinfo("Peak Overlap", "PyChromat detected overlap between several automatically " +
            #                             "detected peaks. PyChromat has attempted to automatically re-adjust the borders to capture the " +
            #                             "largest possible portion of the analytes, based on their signal intensities. However, please feel " +
            #                             "free to manually re-adjust the signals if desired in the peak list.")
