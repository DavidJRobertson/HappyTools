from tkinter import StringVar, Tk, Toplevel, Label, W, Entry, OptionMenu, Button, E
from util.ToolTip import createToolTip
import HappyTools


slicepoints = 5
points = 100
start = 10
end = 60
baselineOrder = 1
backgroundWindow = 1
peakDetectionMin = 0.05
peakDetectionEdge = "Sigma"
peakDetectionEdgeValue = 2.0
minPeaks = 4
decimalNumbers = 6
min_improvement = 0.05
use_interpolation = False
noise = "RMS"
backgroundNoiseMethod = "MT"


def get_settings():
    """Read the settings file.

    This function opens the settings file (default is HappyTools.ini),
    parses the lines of the settings file and takes the value from the
    settings file as a value for the changeable settings (e.g. the start
    variable can be read from the settings file).

    Keyword arguments:
    none
    """
    with open("HappyTools.ini", 'r') as fr:
        for line in fr:
            chunks = line.strip('\n').split('\t')
            if chunks[0] == "points:":
                settings.points = int(chunks[1])
            elif chunks[0] == "start:":
                settings.start = float(chunks[1])
            elif chunks[0] == "end:":
                settings.end = float(chunks[1])
            elif chunks[0] == "baselineOrder:":
                settings.baselineOrder = int(chunks[1])
            elif chunks[0] == "backgroundWindow:":
                settings.backgroundWindow = float(chunks[1])
            elif chunks[0] == "noise:":
                settings.noise = str(chunks[1])
            # elif chunks[0] == "nobanStart:":
            # global nobanStart
            # nobanStart = float(chunks[1])
            elif chunks[0] == "slicepoints:":
                settings.slicepoints = int(chunks[1])
            elif chunks[0] == "createFigure:":
                global createFigure
                createFigure = str(chunks[1])
            elif chunks[0] == "minPeaks:":
                settings.minPeaks = int(chunks[1])
            elif chunks[0] == "minPeakSN:":
                global minPeakSN
                minPeakSN = int(chunks[1])
            elif chunks[0] == "peakDetectionMin:":
                settings.peakDetectionMin = float(chunks[1])
            elif chunks[0] == "peakDetectionEdge:":
                settings.peakDetectionEdge = str(chunks[1])
            elif chunks[0] == "peakDetectionEdgeValue:":
                settings.peakDetectionEdgeValue = float(chunks[1])


def settingsPopup():
    """ TODO: Redesign settings window (it's fugly)
    """

    figureVariable = StringVar()
    figureVariable.set(createFigure)
    peakDetectionEdgeVar = StringVar()
    peakDetectionEdgeVar.set(peakDetectionEdge)

    def close():
        """ TODO
        """
        global points
        global start
        global end
        global baselineOrder
        global backgroundWindow
        global backgroundNoise
        # global nobanStart
        global slicepoints
        global createFigure
        global minPeaks
        global minPeakSN
        global peakDetectionMin
        global peakDetectionEdge
        global peakDetectionEdgeValue
        points = int(pointsWindow.get())
        start = float(startWindow.get())
        end = float(endWindow.get())
        baselineOrder = int(baselineOrderWindow.get())
        backgroundWindow = float(backgroundWindowWindow.get())
        # nobanStart = float(nobanWindow.get())
        slicepoints = int(slicepointsWindow.get())
        createFigure = str(figureVariable.get())
        minPeaks = int(minPeakWindow.get())
        minPeakSN = int(minPeakSNWindow.get())
        peakDetectionMin = float(peakDetection.get())
        peakDetectionEdge = str(peakDetectionEdgeVar.get())
        peakDetectionEdgeValue = float(peakDetectionEdgeValueWindow.get())
        top.destroy()

    def save():
        """ TODO
        """
        with open(HappyTools.settings, 'w') as fw:
            fw.write("points:\t" + str(int(pointsWindow.get())) + "\n")
            fw.write("start:\t" + str(float(startWindow.get())) + "\n")
            fw.write("end:\t" + str(float(endWindow.get())) + "\n")
            fw.write("baselineOrder:\t" + str(int(baselineOrderWindow.get())) + "\n")
            fw.write("backgroundWindow:\t" + str(float(backgroundWindowWindow.get())) + "\n")
            # fw.write("nobanStart:\t"+str(float(nobanWindow.get()))+"\n")
            fw.write("noise:\t" + str(noise) + "\n")
            fw.write("slicepoints:\t" + str(slicepoints) + "\n")
            fw.write("createFigure:\t" + str(figureVariable.get()) + "\n")
            fw.write("minPeaks:\t" + str(minPeakWindow.get()) + "\n")
            fw.write("minPeakSN:\t" + str(minPeakSNWindow.get()) + "\n")
            fw.write("peakDetectionMin:\t" + str(peakDetection.get()) + "\n")
            fw.write("peakDetectionEdge:\t" + str(peakDetectionEdgeVar.get()) + "\n")
            fw.write("peakDetectionEdgeValue:\t" + str(peakDetectionEdgeValueWindow.get()) + "\n")

    top = Tk.top = Toplevel()
    top.title("HappyTools " + str(HappyTools.version) + " Settings")
    top.protocol("WM_DELETE_WINDOW", lambda: close())

    # General Settings
    generalLabel = Label(top, text="General Settings", font=("Helvetica", 16))
    generalLabel.grid(row=0, columnspan=2, sticky=W)

    startLabel = Label(top, text="Start Time", font=("Helvetica", 12))
    startLabel.grid(row=1, column=0, sticky=W)
    startWindow = Entry(top)
    startWindow.insert(0, start)
    startWindow.grid(row=1, column=1, sticky=W)

    endLabel = Label(top, text="End Time", font=("Helvetica", 12))
    endLabel.grid(row=2, column=0, sticky=W)
    endWindow = Entry(top)
    endWindow.insert(0, end)
    endWindow.grid(row=2, column=1, sticky=W)

    # Peak Detection Settings
    peakDetectionLabel = Label(top, text="Peak Detection Settings", font=("Helvetica", 16))
    peakDetectionLabel.grid(row=3, columnspan=2, sticky=W)

    peakDetectionLabel = Label(top, text="Minimum Intensity", font=("Helvetica", 12))
    peakDetectionLabel.grid(row=4, column=0, sticky=W)
    peakDetection = Entry(top)
    peakDetection.insert(0, peakDetectionMin)
    peakDetection.grid(row=4, column=1, sticky=W)

    peakDetectionEdgeLabel = Label(top, text="Edge Method", font=("Helvetica", 12))
    peakDetectionEdgeLabel.grid(row=5, column=0, sticky=W)
    peakDetectionEdgeWindow = OptionMenu(top, peakDetectionEdgeVar, "Sigma", "FWHM")
    peakDetectionEdgeWindow.grid(row=5, column=1, sticky=W)

    peakDetectionEdgeValueLabel = Label(top, text="Sigma Value", font=("Helvetica", 12))
    peakDetectionEdgeValueLabel.grid(row=6, column=0, sticky=W)
    peakDetectionEdgeValueWindow = Entry(top)
    peakDetectionEdgeValueWindow.insert(0, peakDetectionEdgeValue)
    peakDetectionEdgeValueWindow.grid(row=6, column=1, sticky=W)

    # Calibration Settings
    calibrationLabel = Label(top, text="Calibration Settings", font=("Helvetica", 16))
    calibrationLabel.grid(row=7, columnspan=2, sticky=W)

    minPeakLabel = Label(top, text="Minimum Peaks", font=("Helvetica", 12))
    minPeakLabel.grid(row=8, column=0, sticky=W)
    minPeakWindow = Entry(top)
    minPeakWindow.insert(0, minPeaks)
    minPeakWindow.grid(row=8, column=1, sticky=W)

    minPeakSNLabel = Label(top, text="Minimum S/N", font=("Helvetica", 12))
    minPeakSNLabel.grid(row=9, column=0, sticky=W)
    minPeakSNWindow = Entry(top)
    minPeakSNWindow.insert(0, minPeakSN)
    minPeakSNWindow.grid(row=9, column=1, sticky=W)

    # Quantitation Settings
    quantitationLabel = Label(top, text="Quantitation Settings", font=("Helvetica", 16))
    quantitationLabel.grid(row=10, columnspan=2, sticky=W)

    pointsLabel = Label(top, text="Datapoints", font=("Helvetica", 12))
    pointsLabel.grid(row=11, column=0, sticky=W)
    pointsWindow = Entry(top)
    pointsWindow.insert(0, points)
    pointsWindow.grid(row=11, column=1, sticky=W)

    baselineOrderLabel = Label(top, text="Baseline Order", font=("Helvetica", 12))
    baselineOrderLabel.grid(row=12, column=0, sticky=W)
    baselineOrderWindow = Entry(top)
    baselineOrderWindow.insert(0, baselineOrder)
    baselineOrderWindow.grid(row=12, column=1, sticky=W)

    backgroundWindowLabel = Label(top, text="Background Window", font=("Helvetica", 12))
    backgroundWindowLabel.grid(row=13, column=0, sticky=W)
    backgroundWindowWindow = Entry(top)
    backgroundWindowWindow.insert(0, backgroundWindow)
    backgroundWindowWindow.grid(row=13, column=1, sticky=W)

    # nobanLabel = Label(top, text="NOBAN Start", font=("Helvetica", 12))
    # nobanLabel.grid(row=14, column=0, sticky=W)
    # nobanWindow = Entry(top)
    # nobanWindow.insert(0, nobanStart)
    # nobanWindow.grid(row=14, column=1, sticky=W)

    slicepointsLabel = Label(top, text="MT Slice points", font=("Helvetica", 12))
    slicepointsLabel.grid(row=15, column=0, sticky=W)
    slicepointsWindow = Entry(top)
    slicepointsWindow.insert(0, slicepoints)
    slicepointsWindow.grid(row=15, column=1, sticky=W)

    figureLabel = Label(top, text="Create figure for each analyte", font=("Helvetica", 12))
    figureLabel.grid(row=16, column=0, sticky=W)
    options = ["True", "False"]
    figureWindow = OptionMenu(top, figureVariable, *options)
    figureWindow.grid(row=16, column=1, sticky=W)

    # Close/Save Buttons
    saveButton = Button(top, text="Save", command=lambda: save())
    saveButton.grid(row=17, column=0, sticky=W)
    closeButton = Button(top, text="Close", command=lambda: close())
    closeButton.grid(row=17, column=1, sticky=E)

    # Tooltips
    createToolTip(pointsLabel, "The number of data points that is used to determine the baseline. Specifically, " +
                  "this setting specifies how large each segment of the whole chromatogram will be to identify the lowest " +
                  "data point per window, i.e. a setting of 100 means that the chromatogram is split into segments of 100 " +
                  "data points per segment.")
    createToolTip(startLabel, "This setting tells the program from which time point it is supposed to begin " +
                  "processing, this setting should be set in such a way that it is before the analytes of interest but " +
                  "after any potential big increases or decrease in intensity.")
    createToolTip(endLabel,
                  "This setting tells the program until which time point it is supposed to begin processing, " +
                  "this setting should be set in such a way that it is after the analytes of interest but before any " +
                  "potential big increases or decrease in intensity.")
    createToolTip(baselineOrderLabel,
                  "This setting tells the program what sort of function should be used to correct " +
                  "the baseline. A value of 1 refers to a linear function, while a value of 2 refers to a quadratic " +
                  "function. We advise to use a linear function as the need for any higher order function indicates an " +
                  "unexpected event in the chromatography.")
    createToolTip(backgroundWindowLabel,
                  "This setting tells the program the size of the region that will be examined " +
                  "to determine the background. A value of 1 means that the program will look from 20.0 to 21.0 minutes " +
                  "and 21.4 to 22.4 for an analyte that elutes from 21.0 to 21.4 minutes.")
    # createToolTip(nobanLabel,"This setting specifies the initial estimate for the NOBAN algorithm, specifically a "+
    # "value of 0.25 means that the lowest 25% of all data points will be used as an initial estimate for the "+
    # "background. This value should be changed depending on how many signals there are in the chromatogram, "+
    # "e.g. in a crowded chromatogram this value should be low.")
    createToolTip(slicepointsLabel, "The number of conscutive data points that will be used to determine the " +
                  "background and noise using the MT method. The MT method will scan all datapoints that fall within the " +
                  "background window (specified above) to find the here specified number of consecutive data points that " +
                  "yield the lowest average intensity, the average of these data points is then used as background while " +
                  "the standard deviation of these data points is used as the noise.")
    createToolTip(figureLabel,
                  "This setting specifies if HappyTools should create a figure for each integrated peak, " +
                  "showing the raw datapoints, background, noise, S/N and GPQ values. This is a very performance intensive " +
                  "option and it is recommended to only use this on a subset of your samples (e.g. less than 25 samples).")
    createToolTip(minPeakLabel, "This setting specifies the minimum number of calibrant peaks that have to pass the " +
                  "specified S/N value that must be present in a chromatogram. A chromatogram for which there are not " +
                  "enough calibrant peaks passing the specified criteria will not be calibrated and excluded from further " +
                  "quantitation.")
    createToolTip(minPeakSNLabel, "This setting specifies the minimum S/N value a calibrant peak must surpass to be " +
                  "included in the calibration. The actual S/N value that is determined by HappyTools depends heavily on " +
                  "which method to determine signal and noise is used, the default method being rather conservative.")
    createToolTip(peakDetectionLabel, "This setting specifies the minimum intensity, relative to the main peak in " +
                  "a chromatogram, that the peak detection algorithm will try to annotate. For example, a value of 0.01 " +
                  "means that the program will attempt to annotate peaks until the next highest peak is below 1% of the " +
                  "intensity of the main peak in the chromatogram.")
    createToolTip(peakDetectionEdgeLabel,
                  "This setting specifies if HappyTools will determine the integration window " +
                  "using either the full width at half maximum (FWHM) or a specified sigma value. The Sigma value has to be " +
                  "specified in the field below if Sigma is the selected method.")
    createToolTip(peakDetectionEdgeValueLabel, "This setting specifies the Sigma value that will be used for " +
                  "determining the border of the integration window. A value of 1.0 means that HappyTools will set the " +
                  "integration window so that 68.3% of the Gaussian peak will be quantified (2 Sigma = 95.5% and 3 sigma " +
                  "= 99.7%). Please note that this value should depend on how complex the chromatogram is, for instance " +
                  "a low sigma will yield better results in a complex chromatogram.")

