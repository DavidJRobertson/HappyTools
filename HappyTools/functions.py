#! /usr/bin/env python

import tkinter.filedialog
import tkinter.messagebox
from Chromatogram import *

nobanStart = 0.25



def addFile(fig, canvas):
    """Ask for a file and draw it on the existing canvas."""
    data = readData()
    file_path = tkinter.filedialog.askopenfilename()
    if not file_path:
        pass
    else:
        data.append((file_path, openChrom(file_path)))
    fig.clear()
    axes = fig.add_subplot(111)
    for i in data:
        x_array, y_array = list(zip(*i[1]))
        axes.plot(x_array, y_array, label=str(os.path.split(i[0])[-1]))
    axes.legend()
    canvas.draw()


def chromCalibration(fig, canvas):
    """Ask for a reference file and calibrate the current chromatogram.

    This function will first ask the user to select a reference file
    using a tkinter filedialog.  The function will then find the highest
    intensity timepoint for each calibrant window. The actual
    calibration is achieved by fitting a second degree polynomial
    through the observed and expected retention times and applying the
    formula on the original chromatogram, with the new retention time
    being cast into a float of a user defined number of decimal numbers.
    The function finishes by plotting the calibrated chromatograom on
    top of the original chromatogram and writing the calibrated
    chromatogram to the temporary file.

    Keyword arguments:
    fig -- matplotlib figure object
    canvas -- tkinter canvas object
    """
    refFile = tkinter.filedialog.askopenfilename(title="Reference File")
    try:
        refPeaks = []
        with open(refFile, 'r') as fr:
            for line in fr:
                line = line.rstrip("\n").split("\t")
                try:
                    refPeaks.append((str(line[0]), float(line[1]), float(line[2])))
                except ValueError:
                    pass
    except IOError:
        tkinter.messagebox.showinfo("File Error", "The selected reference file could not be opened.")

    # Get observed times
    data = readData()
    time, intensity = list(zip(*data[0][1]))
    timePairs = []
    for i in refPeaks:
        low = bisect.bisect_left(time, i[1] - i[2])
        high = bisect.bisect_right(time, i[1] + i[2])
        max_value = max(intensity[low:high])
        max_index = intensity[low:high].index(max_value)
        timePairs.append((i[1], time[low + max_index]))

    # Calibration
    observedTime = []
    expectedTime = []
    for i in timePairs:
        expectedTime.append(float(i[0]))
        observedTime.append(float(i[1]))
    # z = np.polyfit(observedTime,expectedTime,2)
    # f = np.poly1d(z)
    f = ultraPerformanceCalibration(observedTime, expectedTime, time[0], time[-1])
    calibratedData = list(zip(f(time), intensity))

    # Plot & Write Data to Disk
    multiData = [(os.path.split(data[0][0])[-1], data[0][1]),
                 (os.path.split(data[0][0])[-1] + " (Cal)", calibratedData)]
    plotMultiData(fig, canvas, multiData)
    writeData(calibratedData, os.path.split(data[0][0])[-1] + " (Cal)")


def openFile(fig, canvas):
    """Open a file and show it on the canvas.

    This function first asks the user to select a file via a file
    dialog. The function will then call two other functions to write a
    temporary file to the disk (writeData) and to plot the selected file
    on the canvas (plotData).

    Keyword arguments:
    fig -- matplotlib figure object
    canvas -- tkinter canvas object
    """
    file_path = tkinter.filedialog.askopenfilename()
    if not file_path:
        pass
    else:
        data = openChrom(file_path)
        try:
            data = data.tolist()
        except AttributeError:
            pass
        if data:
            writeData(data, os.path.split(file_path)[-1])
            plotData(data, fig, canvas, file_path)


def overlayQuantitationWindows(fig, canvas):
    """ TODO
    """
    # Prompt for peaklist
    peakList = tkinter.filedialog.askopenfilename()
    peaks = []
    with open(peakList, 'r') as fr:
        for line in fr:
            line = line.rstrip("\n").split("\t")
            try:
                peaks.append((str(line[0]), float(line[1]), float(line[2])))
            except ValueError:
                pass

    # Read data currently on canvas
    data = {'Name': readData()[0][0], 'Data': readData()[0][1]}
    time, intensity = list(zip(*data['Data']))

    # Plot the original data
    fig.clear()
    axes = fig.add_subplot(111)
    line, = axes.plot(time, intensity, label=data['Name'])
    handles, labels = axes.get_legend_handles_labels()
    fig.legend(handles, labels)
    axes.get_xaxis().get_major_formatter().set_useOffset(False)
    axes.set_xlabel("Time [m]")
    axes.set_ylabel("Intensity [au]")
    canvas.draw()

    # Plot the quantitation windows
    for i in peaks:
        low = bisect.bisect_left(time, i[1] - i[2])
        high = bisect.bisect_right(time, i[1] + i[2])
        newTime = np.linspace(time[low], time[high], len(time[low:high]))
        f = InterpolatedUnivariateSpline(time[low:high], intensity[low:high])
        newIntensity = f(newTime)
        axes.fill_between(time[low:high], 0, newIntensity, alpha=0.5)
        axes.text(i[1], max(intensity[low:high]), i[0])
        canvas.draw()


def saveAnnotation():
    """ TODO
        Add correct try/except handling
    """
    origin = os.path.join(str(os.getcwd()), "temp", "annotation.ref")
    target = tkinter.filedialog.asksaveasfile(mode='w', defaultextension=".ref")
    shutil.copyfile(origin, target.name)


