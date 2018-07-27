import bisect
import math
import operator
import os
import shutil
import sys
import tkinter.filedialog
import tkinter.messagebox
from datetime import datetime

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline, PchipInterpolator, Akima1DInterpolator
from scipy.optimize import curve_fit
from scipy.signal import argrelextrema
from Trace import Trace
from crap import background_noise, plotMultiData
from functions import nobanStart
from settings import *
from util.PowerLawCall import PowerLawCall


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




def powerLaw(x, a, b, c):
    penalty = 0
    if b > 2.:
        penalty = abs(b - 1.) * 10000
    if b < 0.:
        penalty = abs(2. - b) * 10000
    return a * x ** b + c + penalty


def fwhm(coeff):
    """Calculate the FWHM.

    This function will calculate the FWHM based on the following formula
    FWHM = 2*sigma*sqrt(2*ln(2)). The function will return a dictionary
    with the fwhm ('fwhm'), the Gaussian peak center ('center') and the
    +/- width, from the peak center ('width').

    Keyword arguments:
    coeff -- coefficients as calculated by SciPy curve_fit
    """
    fwhm = abs(2 * coeff[2] * math.sqrt(2 * math.log(2)))
    width = 0.5 * fwhm
    center = coeff[1]
    return {'fwhm': fwhm, 'width': width, 'center': center}


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


def gaussFunction(x, *p):
    """Define and return a Gaussian function.

    This function returns the value of a Gaussian function, using the
    A, mu and sigma value that is provided as *p.

    Keyword arguments:
    x -- number
    p -- A, mu and sigma numbers
    """
    A, mu, sigma = p
    return A * np.exp(-(x - mu) ** 2 / (2. * sigma ** 2))


def getPeakList(fileName):
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


def peakDetection(fig, canvas):
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

    <<TODO>>
    the current implementation is overly complex and can be optimized
    and the code has to be cleaned up.

    Keyword arguments:
    fig -- matplotlib figure object
    canvas -- tkinter canvas object
    """
    data = readData()

    # Retrieve subset of data and determine the background
    x_data, y_data = list(zip(*data[0][1]))
    orig_x = x_data
    orig_y = y_data
    low = bisect.bisect_left(x_data, start)
    high = bisect.bisect_right(x_data, end)
    x_data = x_data[low:high]
    y_data = y_data[low:high]
    if backgroundNoiseMethod == "NOBAN":
        NOBAN = noban(y_data)
    elif backgroundNoiseMethod == "MT":
        NOBAN = background_noise(y_data)

    # Determine the local maxima and minima, using first order derivative
    newX = np.linspace(x_data[0], x_data[-1], 25000 * (x_data[-1] - x_data[0]))
    f = InterpolatedUnivariateSpline(x_data, y_data)
    fPrime = f.derivative()
    newY = f(newX)
    newPrimeY = fPrime(newX)
    maxm = argrelextrema(newPrimeY, np.greater)
    minm = argrelextrema(newPrimeY, np.less)
    breaks = maxm[0].tolist() + minm[0].tolist()
    breaks = sorted(breaks)

    # Determine the maximum full peak within the specified window, for the cut-off
    maxIntensity = 0
    for i in range(0, len(breaks) - 2):
        maxIntensity = max(max(newY[breaks[i]:breaks[i + 1]]), maxIntensity)
    cutoff = peakDetectionMin * (maxIntensity - max(NOBAN['Background'], 0))

    # Detect peaks
    functions = []
    counter = 0
    while max(y_data) - NOBAN['Background'] > cutoff:
        counter += 1
        print("Fitting peak: " + str(counter))
        f = InterpolatedUnivariateSpline(x_data, y_data)
        fPrime = f.derivative()
        newY = f(newX)
        newPrimeY = fPrime(newX)
        maxm = argrelextrema(newPrimeY, np.greater)
        minm = argrelextrema(newPrimeY, np.less)
        breaks = maxm[0].tolist() + minm[0].tolist()
        breaks = sorted(breaks)
        maxPoint = 0

        # Subset the data
        # Region from newY[0] to breaks[0]
        try:
            if max(newY[0:breaks[0]]) > maxPoint:
                maxPoint = max(newY[0:breaks[0]])
                xData = newX[0:breaks[0]]
                yData = [x - NOBAN['Background'] for x in newY[0:breaks[0]]]
        except IndexError:
            pass
        # Regions between breaks[x] and breaks[x+1]
        try:
            for index, j in enumerate(breaks):
                if max(newY[breaks[index]:breaks[index + 1]]) > maxPoint:
                    maxPoint = max(newY[breaks[index]:breaks[index + 1]])
                    xData = newX[breaks[index]:breaks[index + 1]]
                    yData = [x - max(NOBAN['Background'], 0) for x in newY[breaks[index]:breaks[index + 1]]]
        except IndexError:
            pass
        # Region from break[-1] to newY[-1]
        try:
            if max(newY[breaks[-1]:-1]) > maxPoint:
                maxPoint = max(newY[breaks[-1]:-1])
                xData = newX[breaks[-1]:-1]
                yData = [x - NOBAN['Background'] for x in newY[breaks[-1]:-1]]
        except IndexError:
            pass

        # Gaussian fit on main points
        peak = xData[yData > np.exp(-0.5) * max(yData)]
        guess_sigma = 0.5 * (max(peak) - min(peak))
        newGaussX = np.linspace(x_data[0], x_data[-1], 2500 * (x_data[-1] - x_data[0]))
        p0 = [np.max(yData), xData[np.argmax(yData)], guess_sigma]
        try:
            coeff, var_matrix = curve_fit(gaussFunction, xData, yData, p0)
            newGaussY = gaussFunction(newGaussX, *coeff)
        except:
            pass

        # Limit the peak to either FWHM or a user specified Sigma value
        FWHM = fwhm(coeff)
        if peakDetectionEdge == "FWHM":
            low = bisect.bisect_left(newGaussX, coeff[1] - FWHM['width'])
            high = bisect.bisect_right(newGaussX, coeff[1] + FWHM['width'])
            try:
                newGaussX = newGaussX[low:high]
                newGaussY = newGaussY[low:high]
            except:
                pass
        elif peakDetectionEdge == "Sigma":
            low = bisect.bisect_left(newGaussX, coeff[1] - peakDetectionEdgeValue * abs(coeff[2]))
            high = bisect.bisect_right(newGaussX, coeff[1] + peakDetectionEdgeValue * abs(coeff[2]))
            try:
                newGaussX = newGaussX[low:high]
                newGaussY = newGaussY[low:high]
            except:
                pass

        # Ignore breaks (f'(x) == 0) that did not match any data (reword this)
        if newGaussX.any():
            functions.append(
                {'Peak': newGaussX[np.argmax(newGaussY)], 'Data': list(zip(newGaussX, newGaussY)), 'FWHM': FWHM})

        # Subtract the fitted Gaussian from the raw or intermediate data and repeat
        # the peak detection step.
        GaussY = gaussFunction(x_data, *coeff)
        new_y = list(map(operator.sub, y_data, GaussY))
        if max(new_y) == max(y_data):
            break
        y_data = new_y
    functions = sorted(functions, key=lambda tup: tup['Peak'])

    # iterate over all peaks and remove overlap
    overlapDetected = False
    for index, i in enumerate(functions):
        try:
            if i['Data'][-1][0] > functions[index + 1]['Data'][0][0]:
                overlapDetected = True
                overlap = abs(functions[index + 1]['Data'][0][0] - i['Data'][-1][0])
                peak1 = max([x[1] for x in i['Data']])
                peak2 = max([x[1] for x in functions[index + 1]['Data']])
                peak1fraction = (peak1 / (peak1 + peak2)) * overlap
                peak2fraction = (peak2 / (peak1 + peak2)) * overlap
                low = bisect.bisect_right([x[0] for x in i['Data']], i['Data'][-1][0] - peak2fraction)
                high = bisect.bisect_left([x[0] for x in functions[index + 1]['Data']],
                                          functions[index + 1]['Data'][0][0] + peak1fraction)
                i['Data'] = i['Data'][0:low]
                functions[index + 1]['Data'] = functions[index + 1]['Data'][high:-1]
        except IndexError:
            pass

    # Determine calibrants
    calibrants = determineCalibrants(functions)

    # Writing to temp folder
    with open('temp/annotation.ref', 'w') as fw:
        fw.write("Peak\tRT\tWindow\n")
        for index, analyte in enumerate(functions):
            try:
                window = 0.5 * (float(analyte['Data'][-1][0]) - float(analyte['Data'][0][0]))
                center = float(analyte['Data'][0][0]) + 0.5 * window
                fw.write(
                    str("%.2f" % analyte['Peak']) + "\t" + str("%.2f" % center) + "\t" + str("%.2f" % window) + "\n")
            except:
                pass
    with open('temp/calibrants.ref', 'w') as fw:
        fw.write("Peak\tRT\tWindow\n")
        for index, analyte in enumerate(calibrants):
            try:
                window = 0.5 * (float(analyte['Data'][-1][0]) - float(analyte['Data'][0][0]))
                center = float(analyte['Data'][0][0]) + 0.5 * window
                fw.write(
                    str("%.2f" % analyte['Peak']) + "\t" + str("%.2f" % center) + "\t" + str("%.2f" % window) + "\n")
            except:
                pass

    # Plotting
    fig.clear()
    axes = fig.add_subplot(111)
    axes.plot(orig_x, orig_y, 'b', alpha=0.5)
    for index, i in enumerate(functions):
        try:
            xd, yd = list(zip(*i['Data']))
            axes.plot(xd, yd, label=str(index + 1) + ": " + str("%.2f" % i['Peak']))
            axes.fill_between(xd, 0, yd, alpha=0.2)
        except ValueError:
            pass
    for index, i in enumerate(calibrants):
        try:
            xd, yd = list(zip(*i['Data']))
            axes.annotate('Cal: ' + str(index), xy=(xd[yd.index(max(yd))], max(yd)),
                          xytext=(xd[yd.index(max(yd))], max(yd)),
                          arrowprops=dict(facecolor='black', shrink=0.05))
        except ValueError:
            pass
    axes.set_xlabel("Time [m]")
    axes.set_ylabel("Intensity [au]")
    handles, labels = axes.get_legend_handles_labels()
    fig.legend(handles, labels)
    canvas.draw()

    # Warn (if needed)
    if overlapDetected:
        tkinter.messagebox.showinfo("Peak Overlap", "HappyTools detected overlap between several automatically " +
                                    "detected peaks. HappyTools has attempted to automatically re-adjust the borders to capture the " +
                                    "largest possible portion of the analytes, based on their signal intensities. However, please feel " +
                                    "free to manually re-adjust the signals if desired in the peak list.")


def quantifyChrom(fig, canvas):
    """ TODO
    This is super prelimenary, should/will produce a lot more values
    """
    peakList = tkinter.filedialog.askopenfilename()
    peaks = getPeakList(peakList)
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
            coeff, var_matrix = curve_fit(gaussFunction, x_data, y_data, p0)
            newY = gaussFunction(newX, *coeff)
            # Get residuals
            for index, j in enumerate(time[low:high]):
                residual += abs(intensity[index] - gaussFunction(j, *coeff)) ** 2
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
    z = curve_fit(powerLaw, measured, expected)

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
            func = PowerLawCall(*z[0])

    if use_interpolation:
        # Monotonic Piecewise Cubic Hermite Interpolating Polynomial
        RMS_buffer = []
        f = PchipInterpolator(measured, expected)
        for index, j in enumerate(measured):
            RMS_buffer.append((f(j) - expected[index]) ** 2)
        RMS_buffer = np.mean(RMS_buffer)
        RMS_buffer = math.sqrt(RMS_buffer)
        if RMS_buffer < RMS - min_improvement * RMS:
            RMS = RMS_buffer
            func = f

        # Akima 1D Interpolator
        RMS_buffer = []
        f = Akima1DInterpolator(measured, expected)
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



