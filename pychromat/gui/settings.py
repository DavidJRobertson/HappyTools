from tkinter import StringVar, Tk, Toplevel, Label, W, Entry, OptionMenu, Button, E

from gui.ToolTip import ToolTip

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
output = "summary.results"


def get_settings():
    """Read the settings file.

    This function opens the settings file (default is PyChromat.ini),
    parses the lines of the settings file and takes the value from the
    settings file as a value for the changeable settings (e.g. the start
    variable can be read from the settings file).

    Keyword arguments:
    none
    """
    with open("PyChromat.ini", 'r') as fr:
        for line in fr:
            chunks = line.strip('\n').split('\t')
            if chunks[0] == "points:":
                points = int(chunks[1])
            elif chunks[0] == "start:":
                start = float(chunks[1])
            elif chunks[0] == "end:":
                end = float(chunks[1])
            elif chunks[0] == "baselineOrder:":
                baselineOrder = int(chunks[1])
            elif chunks[0] == "backgroundWindow:":
                backgroundWindow = float(chunks[1])
            elif chunks[0] == "noise:":
                noise = str(chunks[1])
            # elif chunks[0] == "nobanStart:":
            # global nobanStart
            # nobanStart = float(chunks[1])
            elif chunks[0] == "slicepoints:":
                slicepoints = int(chunks[1])
            elif chunks[0] == "createFigure:":
                global createFigure
                createFigure = str(chunks[1])
            elif chunks[0] == "minPeaks:":
                minPeaks = int(chunks[1])
            elif chunks[0] == "minPeakSN:":
                global minPeakSN
                minPeakSN = int(chunks[1])
            elif chunks[0] == "peakDetectionMin:":
                peakDetectionMin = float(chunks[1])
            elif chunks[0] == "peakDetectionEdge:":
                peakDetectionEdge = str(chunks[1])
            elif chunks[0] == "peakDetectionEdgeValue:":
                peakDetectionEdgeValue = float(chunks[1])

