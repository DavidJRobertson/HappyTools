from tkinter import *
import tkinter.filedialog

import HappyTools
import batchFunctions
from util.ToolTip import createToolTip

root = Tk()
root.withdraw()
outputWindow = IntVar()
absInt = IntVar()
relInt = IntVar()
bckSub = IntVar()
bckNoise = IntVar()
peakQual = IntVar()


def info_popup():
    """ Generate the about window.

    This function will generate a new window that lists some information
    about HappyTools, such as the license and author.

    Keyword Arguments:
    none
    """

    def close():
        """Close the output pop-up.
        """
        top.destroy()

    top = Tk.top = Toplevel()
    top.protocol("WM_DELETE_WINDOW", lambda: close())
    top.title("HappyTools " + str(HappyTools.version) + " About")
    information = ("HappyTools Version " + str(HappyTools.version) + " build " + str(HappyTools.build) +
                   " by Bas Cornelis Jansen, bas.c.jansen@gmail.com\n\n" +
                   "This software is released under the Apache 2.0 License." +
                   " Full details regarding this license can be found at" +
                   "the following URL:\n\n" +
                   "http://www.apache.org/licenses/LICENSE-2.0")
    about = Label(top, text=information, justify=LEFT, wraplength=250)
    about.pack()
    top.lift()


def update_progress_bar(bar, variable, index, length):
    variable.set(str(int((float(index) / float(length)) * 100)) + "%")
    bar["value"] = int((float(index) / float(length)) * 100)
    bar.update()


def output_popup():
    """Create a pop-up enabling output selection.

    This function creates a pop up box that allows the user to specify
    what output should be shown in the final summary. The default value
    for all variables is off (0) and by ticking a box it is set to on
    (1).

    """
    if outputWindow.get() == 1:
        return
    outputWindow.set(1)

    def select_all():
        """Set all variables to on (1).
        """
        absInt.set(1)
        relInt.set(1)
        bckSub.set(1)
        bckNoise.set(1)
        peakQual.set(1)

    def select_none():
        """Set all variables to off (0).
        """
        absInt.set(0)
        relInt.set(0)
        bckSub.set(0)
        bckNoise.set(0)
        peakQual.set(0)

    def close():
        """Close the output pop-up.
        """
        outputWindow.set(0)
        top.destroy()

    top = Toplevel()
    top.protocol("WM_DELETE_WINDOW", lambda: close())
    top.title("HappyTools " + str(HappyTools.version) + " Output Options")
    selAll = Button(top, text="Select All", command=lambda: select_all())
    selAll.grid(row=0, column=0, sticky=W)
    none = Button(top, text="Select None", command=lambda: select_none())
    none.grid(row=0, column=1, sticky=E)
    text1 = Label(top, text="Base Outputs", font="bold")
    text1.grid(row=1, column=0, sticky=W)
    text2 = Label(top, text="Output Modifiers", font="bold")
    text2.grid(row=1, column=1, sticky=W)
    ai = Checkbutton(top, text="Analyte Intensity\u00B9", variable=absInt, onvalue=1, offvalue=0)
    ai.grid(row=2, column=0, sticky=W)
    ri = Checkbutton(top, text="Relative Intensity\u00B9", variable=relInt, onvalue=1, offvalue=0)
    ri.grid(row=3, column=0, sticky=W)
    pq = Checkbutton(top, text="Peak Quality Criteria", variable=peakQual, onvalue=1, offvalue=0)
    pq.grid(row=4, column=0, sticky=W)
    bn = Checkbutton(top, text="Background and Noise", variable=bckNoise, onvalue=1, offvalue=0)
    bn.grid(row=5, column=0, sticky=W)
    bck = Checkbutton(top, text="\u00B9Background subtracted Intensities", variable=bckSub, onvalue=1, offvalue=0)
    bck.grid(row=2, column=1, sticky=W)
    button = Button(top, text='Ok', command=lambda: close())
    button.grid(row=6, column=0, columnspan=2)
    top.lift()
    return


def batch_popup():
    """Create a batch processing pop-up.

    This function creates a new tkinter window that is used to control
    the batch processing. Specifically, it allows the user to select a
    calibration file, an analyte file, select the desired outputs (by
    calling the outputPopup function) and starting the batch process.

    Keyword arguments:
    none
    """

    calFile = StringVar()
    analFile = StringVar()
    batchFolder = StringVar()

    def close():
        """Close the batch processing pop-up.
        """
        top.destroy()

    def setCalibrationFile():
        """Ask for the calibration file.
        """
        calFile.set(tkinter.filedialog.askopenfilename(title="Calibration File"))

    def setAnalyteFile():
        """Ask for the analyte file.
        """
        analFile.set(tkinter.filedialog.askopenfilename(title="Analyte File"))

    def setBatchFolder():
        """Ask for the batch folder.
        """
        batchFolder.set(tkinter.filedialog.askdirectory(title="Batch Folder"))

    def run():
        """Start the batch process.
        """
        batchFunctions.batchProcess(calFile, analFile, batchFolder)

    top = Tk.top = Toplevel()
    top.title("HappyTools " + str(HappyTools.version) + " Batch Process")
    top.protocol("WM_DELETE_WINDOW", lambda: close())

    calibrationButton = Button(top, text="Calibration File", width=20, command=lambda: setCalibrationFile())
    calibrationButton.grid(row=1, column=0, sticky=W)
    calibrationLabel = Label(top, textvariable=calFile, width=20)
    calibrationLabel.grid(row=1, column=1)

    analyteButton = Button(top, text="Analyte File", width=20, command=lambda: setAnalyteFile())
    analyteButton.grid(row=2, column=0, sticky=W)
    analyteLabel = Label(top, textvariable=analFile, width=20)
    analyteLabel.grid(row=2, column=1)

    batchButton = Button(top, text="Batch Directory", width=20, command=lambda: setBatchFolder())
    batchButton.grid(row=3, column=0, sticky=W)
    batchLabel = Label(top, textvariable=batchFolder, width=20)
    batchLabel.grid(row=3, column=1, sticky=W)

    outputButton = Button(top, text="Output Options", command=lambda: output_popup())
    outputButton.grid(row=4, column=0, columnspan=2, sticky=E + W)

    runButton = Button(top, text="Run", width=20, command=lambda: run())
    runButton.grid(row=5, column=0, sticky=W)
    closeButton = Button(top, text="Close", width=20, command=lambda: close())
    closeButton.grid(row=5, column=1, sticky=E)

    # Tooltips
    createToolTip(calibrationButton,
                  "This button will allow you to select your calibration file, the program expects a " +
                  "tab separated text file where each line consists of a peak ID, peak RT and a RT window.")
    createToolTip(analyteButton,
                  "This button will allow you to select your analyte file, the program expects a tab separated " +
                  "text file where each line consists of a peak ID, peak RT and a RT window.")
    createToolTip(outputButton, "This button will open another window in which you can select which outputs you want " +
                  "HappyTools to show in the final summary.")