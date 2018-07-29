import bisect
import math
import os
import shutil
import sys
import tkinter.filedialog
import tkinter.messagebox
from datetime import datetime
import numpy as np
import scipy.interpolate
import scipy.optimize

from Trace import Trace
from gui.settings import *
import util


class Chromatogram(object):
    def __init__(self, filenaame):
        self.filename = filename
        self.traces = {
            'raw': Trace.from_file(filename)
        }

    def plot_multi_data(self, fig, canvas, data):
        """Plot all chromatograms in data on the canvas.

        This function first clears the canvas and then draws all the
        chromatograms that are in the data list on the canvas.

        Keyword arguments:
        fig -- matplotlib figure object
        canvas -- tkinter canvas object
        data -- list of tuples, consisting of two numbers per tuple
        """
        fig.clear()
        axes = fig.add_subplot(111)
        for i in data:
            xd = []
            yd = []
            for j in i[1]:
                xd.append(j[0])
                yd.append(j[1])
            axes.plot(xd, yd, label=os.path.split(i[0])[-1])
        axes.set_xlabel("Time [m]")
        axes.set_ylabel("Intensity [au]")
        handles, labels = axes.get_legend_handles_labels()
        fig.legend(handles, labels)
        canvas.draw()





def determineCalibrants(functions):
    """ Automatically determine suitable calibrant peaks.

    This function is part of the automated peak detection
    functionality, where it attempts to determine the most suitable
    n number of calibrations (n is the user defined setting of minimum
    number of peaks for calibration). The function splits the time
    between the first and last detected peaks into n chunks, determines
    the highest peak in each chunk and classifies these local maxima
    as potential calibrants.

    Keyword Arguments:
    functions -- A list of dicts, containing Peak, Data and FWHM
    """
    calibrants = []
    timeChunks = []
    timeRange = functions[-1]['Data'][-1][0] - functions[0]['Data'][0][0]
    timeChunk = timeRange / minPeaks
    for i in range(0, minPeaks):
        timeChunks.append((functions[0]['Data'][0][0] + i * float(timeChunk),
                           functions[0]['Data'][0][0] + (i + 1) * float(timeChunk)))
    for i in timeChunks:
        maxIntensity = 0
        calBuffer = None
        for j in functions:
            try:
                X, Y = list(zip(*j['Data']))
            except:
                print(j)
            peakCenter = X[Y.index(max(Y))]
            peakIntensity = max(Y)
            if peakIntensity > maxIntensity and i[0] < peakCenter < i[1]:
                maxIntensity = peakIntensity
                calBuffer = j
        if calBuffer:
            calibrants.append(calBuffer)
    return calibrants





def get_peak_list(fileName):
    """Read and parse the peak file and return a list of peaks.

    This function opens the file that is specified in 'fileName', and
    reads it on a line per line basis. The function will split each
    line on '\t' prior to trying to append the parts to the 'peaks'
    list. The function will write a message to the logFile if logging
    is enabled if the previous mentioned try goes to the except clause.

    Keyword argments:
    fileName -- string
    """
    peaks = []
    try:
        with open(fileName, 'r') as fr:
            for line in fr:
                line = line.rstrip("\n").split("\t")
                try:
                    peaks.append((str(line[0]), float(line[1]), float(line[2])))
                except ValueError:
                    if HappyTools.logging == True and HappyTools.logLevel > 1:
                        with open(HappyTools.logFile, 'a') as fw:
                            fw.write(str(datetime.now().replace(microsecond=0)) + "\tIgnoring line: " + str(
                                line) + " from file: " + str(fileName) + "\n")
                    pass
    except IOError:
        tkinter.messagebox.showinfo("File Error", "The selected reference file could not be opened.")
    return peaks


def noban(data):
    """Determine background and noise using the NOBAN algorithm.

    This function is based on the NOBAN algorithm, published by Jansen et
    al, in 2016. The function sorts the data by increasing intensity,
    takes an initial estimate (defined in nobanStart) and calculates
    the background (average) and noise (root-mean-square or the maximum
    difference) from the initial estimate. The algorithm will then loop
    over the subsequent data points until the next data point falls
    outside of the current average plus three times the standard
    definition (as any point that is > 3SD is considered a signal).
    Alternatively, the function can also shrink the initial region if it
    appears that the initial estimate was too greedy. A major difference
    between the original implementation and this implementation is that
    this function should converge faster by allowing to take different
    step sizes.

    Keyword arguments:
    data -- list of numbers
    """

    def calc_values(sorted_data, curr_size, curr_average, curr_noise, increment):
        curr_size += increment
        curr_average = np.average(sorted_data[0:curr_size])
        if noise == "MM":
            curr_noise = max(sorted_data[0:curr_size]) - min(sorted_data[0:curr_size])
        elif noise == "RMS":
            curr_noise = np.std(sorted_data[0:curr_size])
        return curr_size, curr_average, curr_noise

    sorted_data = sorted(data)
    start_size = int(nobanStart * float(len(sorted_data)))
    curr_size = start_size
    curr_average = np.average(sorted_data[0:curr_size])
    if noise == "MM":
        curr_noise = max(sorted_data[0:curr_size]) - min(sorted_data[0:curr_size])
    elif noise == "RMS":
        curr_noise = np.std(sorted_data[0:curr_size])
    direction_flag = 0
    # <<NOBAN-V2>>
    # This algorithm now includes faster convergence (by starting with a large step
    # and taking smaller steps the closer we get to the minimum).
    for k in range(0, len(sorted_data) - (start_size + 1)):
        remainder = len(sorted_data) - curr_size
        try:
            if sorted_data[curr_size + int(math.ceil(0.1 * remainder))] < curr_average + 3 * curr_noise:
                direction_flag == 1
                curr_size, curr_average, curr_noise = calc_values(sorted_data, curr_size, curr_average, curr_noise,
                                                                  int(math.ceil(0.1 * remainder)))
            elif sorted_data[curr_size + int(math.ceil(0.05 * remainder))] < curr_average + 3 * curr_noise:
                direction_flag == 1
                curr_size, curr_average, curr_noise = calc_values(sorted_data, curr_size, curr_average, curr_noise,
                                                                  int(math.ceil(0.05 * remainder)))
            elif sorted_data[curr_size + 1] < curr_average + 3 * curr_noise:
                direction_flag == 1
                curr_size, curr_average, curr_noise = calc_values(sorted_data, curr_size, curr_average, curr_noise, 1)
            elif sorted_data[
                curr_size - int(math.ceil(0.1 * remainder))] > curr_average + 3 * curr_noise and direction_flag == 0:
                curr_size, curr_average, curr_noise = calc_values(sorted_data, curr_size, curr_average, curr_noise,
                                                                  -int(math.ceil(0.1 * remainder)))
            elif sorted_data[
                curr_size - int(math.ceil(0.05 * remainder))] > curr_average + 3 * curr_noise and direction_flag == 0:
                curr_size, curr_average, curr_noise = calc_values(sorted_data, curr_size, curr_average, curr_noise,
                                                                  -int(math.ceil(0.05 * remainder)))
            elif sorted_data[curr_size - 1] > curr_average + 3 * curr_noise and direction_flag == 0:
                curr_size, curr_average, curr_noise = calc_values(sorted_data, curr_size, curr_average, curr_noise, -1)
            else:
                break
        except IndexError:
            break
    if curr_noise == 0:
        curr_noise = 1
    return {'Background': curr_average, 'Noise': curr_noise}


def quantifyChrom(fig, canvas):
    """ TODO
    This is super preliminary, should/will produce a lot more values
    """
    peakList = tkinter.filedialog.askopenfilename()
    peaks = get_peak_list(peakList)
    data = {'Name': readData()[0][0], 'Data': readData()[0][1]}
    time, intensity = list(zip(*data['Data']))
    results = []
    for i in peaks:
        low = bisect.bisect_left(time, i[1] - i[2])
        high = bisect.bisect_right(time, i[1] + i[2])
        peakArea = 0
        residual = 0
        signalNoise = "Nan"
        # Get signal-to-noise
        lowBackground = bisect.bisect_left(time, max(i[1] - backgroundWindow, start))
        highBackground = bisect.bisect_right(time, min(i[1] + backgroundWindow, end))
        if backgroundNoiseMethod == "NOBAN":
            NOBAN = noban(intensity[lowBackground:highBackground])
        elif backgroundNoiseMethod == "MT":
            NOBAN = noban(intensity[lowBackground:highBackground])
        signalNoise = (max(intensity[low:high]) - NOBAN['Background']) / NOBAN['Noise']
        # Get background subtracted peak area
        for index, j in enumerate(intensity[low:high]):
            try:
                peakArea += max(j - NOBAN['Background'], 0) * (time[low + index] - time[low + index - 1])
            except IndexError:
                continue
        # Gaussian fit (to get residuals)
        x_data = np.array(time[low:high])
        y_data = np.array(intensity[low:high])
        newX = np.linspace(x_data[0], x_data[-1], 2500 * (x_data[-1] - x_data[0]))
        p0 = [np.max(y_data), x_data[np.argmax(y_data)], 0.1]
        try:
            coeff, var_matrix = scipy.optimize.curve_fit(gauss_function, x_data, y_data, p0)
            newY = gauss_function(newX, *coeff)
            # Get residuals
            for index, j in enumerate(time[low:high]):
                residual += abs(intensity[index] - gauss_function(j, *coeff)) ** 2
            residual = math.sqrt(residual)
        except RuntimeError:
            residual = "Nan"
    data['Name'] = str(data['Name'].split('.')[0]) + ".raw"
    with open(data['Name'], 'w') as fw:
        fw.write("Name\tTime\tPeak Area\tS/N\tGaussian Residual RMS\n")
        for i in results:
            fw.write(str(i['Peak']) + "\t" + str(i['Time']) + "\t" + str(i['Area']) + "\t" + str(i['S/N']) + "\t" + str(
                i['Residual']) + "\n")
    tkinter.messagebox.showinfo("Status Message", "Quantitation finished on " + str(datetime.now()))


def readData():
    """ TODO
    """
    data = []
    with open('temp/tracebuffer.txt', 'r') as fr:
        for line in fr:
            if line[0] == ">" and len(data) > 0:
                data.append(name, dataBuffer)
                name = line[2:].rstrip("\n")
                dataBuffer = []
            elif line[0] == ">" and len(data) == 0:
                name = line[2:].rstrip("\n")
                dataBuffer = []
            else:
                chunks = line.rstrip().split("\t")
                dataBuffer.append((float(chunks[0]), float(chunks[1])))
        data.append((name, dataBuffer))
    return data


def saveCalibrants(fig, canvas):
    """ TODO
        Add correct try/except handling
    """
    origin = os.path.join(str(os.getcwd()), "temp", "calibrants.ref")
    target = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".ref")
    shutil.copyfile(origin, target.name)


def saveChrom():
    """ TODO
    """
    data = readData()
    saveFile = tkinter.filedialog.asksaveasfilename()
    with open(saveFile, 'w') as fw:
        for i in data[0][1]:
            fw.write(str(format(i[0], '0.' + str(decimalNumbers) + 'f')) + "\t" + str(
                format(i[1], '0.' + str(decimalNumbers) + 'f')) + "\n")




def ultraPerformanceCalibration(measured, expected, minimum, maximum):
    """ This function tries various calibration methods, starting with
    polynomials, followed by a power law function and lastly tries two
    interpolation methods (Pchip and Akima1D). The latter methods should
    always return an RMS of 0, which is why the function will only use
    those if they give a significant improvement in RMS (defined in
    min_improvement) and if the user has selected to use interpolation
    methods as well (defined in use_interpolation).

    INPUT1: List of measured data points
    INPUT2: List of expected data points
    OUTPUT: Function object
    """
    RMS = sys.maxsize
    func = None

    # Polynomials between 1 and len(expected)
    for i in range(1, len(expected)):
        z = np.polyfit(measured, expected, i)
        f = np.poly1d(z)

        # Check if the fitted polynomial is monotone
        X_range = np.linspace(minimum, maximum, 10000)
        dx = np.diff(f(X_range))
        if not np.all(dx > 0):
            break

        # Calculate RMS
        RMS_buffer = []
        for index, j in enumerate(measured):
            RMS_buffer.append((f(j) - expected[index]) ** 2)
        RMS_buffer = np.mean(RMS_buffer)
        RMS_buffer = math.sqrt(RMS_buffer)
        if RMS_buffer < RMS - min_improvement * RMS:
            RMS = RMS_buffer
            func = f

    # Power Law
    z = scipy.optimize.curve_fit(powerLaw, measured, expected)

    # Check if the fitted power law function is monotone
    X_range = np.linspace(minimum, maximum, 10000)
    dx = np.diff(powerLaw(X_range, *z[0]))
    if np.all(dx > 0):
        # Calculate RMS
        RMS_buffer = []
        for index, i in enumerate(measured):
            RMS_buffer.append((powerLaw(i, *z[0]) - expected[index]) ** 2)
        RMS_buffer = np.mean(RMS_buffer)
        RMS_buffer = math.sqrt(RMS_buffer)
        if RMS_buffer < RMS - min_improvement * RMS:
            RMS = RMS_buffer
            func = util.PowerLawCall(*z[0])

    if use_interpolation:
        # Monotonic Piecewise Cubic Hermite Interpolating Polynomial
        RMS_buffer = []
        f = scipy.interpolate.PchipInterpolator(measured, expected)
        for index, j in enumerate(measured):
            RMS_buffer.append((f(j) - expected[index]) ** 2)
        RMS_buffer = np.mean(RMS_buffer)
        RMS_buffer = math.sqrt(RMS_buffer)
        if RMS_buffer < RMS - min_improvement * RMS:
            RMS = RMS_buffer
            func = f

        # Akima 1D Interpolator
        RMS_buffer = []
        f = scipy.interpolate.Akima1DInterpolator(measured, expected)
        for index, j in enumerate(measured):
            RMS_buffer.append((f(j) - expected[index]) ** 2)
        RMS_buffer = np.mean(RMS_buffer)
        RMS_buffer = math.sqrt(RMS_buffer)
        if RMS_buffer < RMS - min_improvement * RMS:
            RMS = RMS_buffer
            func = f

    return func


def writeData(data, file_path):
    """ TODO
    """
    with open('temp/tracebuffer.txt', 'w') as fw:
        fw.write(">>" + str(file_path) + "\n")
        for i in data:
            fw.write(str(format(i[0], '0.' + str(decimalNumbers) + 'f')) + "\t" + str(
                format(i[1], '0.' + str(decimalNumbers) + 'f')) + "\n")



