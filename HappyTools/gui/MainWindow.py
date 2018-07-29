import os
import tkinter as tk

import matplotlib
import matplotlib.figure
import matplotlib.image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from util import functions

import CustomToolbar
import crap

import Chromatogram


#outputWindow = IntVar()
#absInt = IntVar()
#relInt = IntVar()
#bckSub = IntVar()
#bckNoise = IntVar()
#peakQual = IntVar()


class MainWindow(object):
    @classmethod
    def run(cls):
        root = tk.Tk()
        #root.withdraw()
        mw = cls(root)
        root.mainloop()

    def __init__(self, master):
        self.master = master

        self.master.title("HappyTools")


        # SETTINGS
        #settings.get_settings()

        # CANVAS
        self.fig = matplotlib.figure.Figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.toolbar = CustomToolbar(self.canvas, master)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        self.canvas.draw()

        # FRAME
        frame = Frame(master)


        icon_file = os.path.join(os.path.dirname(__file__), 'assets', 'Icon.ico')
        if os.path.isfile(icon_file):
            master.iconbitmap(default=icon_file)

        background_file = os.path.join(os.path.dirname(__file__), 'assets', 'UI.png')
        if os.path.isfile(background_file):
            background_image = self.fig.add_subplot(111)
            image = matplotlib.image.imread(background_file)
            background_image.axis('off')
            self.fig.set_tight_layout(True)
            background_image.imshow(image)

        # QUIT
        def close():
            self.master.destroy()
            self.master.quit()
        self.master.protocol("WM_DELETE_WINDOW", lambda: close())

        # MENUS
        menu = Menu(master)
        self.master.config(menu=menu)

        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Chromatogram", command=lambda: functions.open_file(self.fig, self.canvas))
        file_menu.add_command(label="Smooth Chromatogram",
                              command=lambda: Chromatogram.smoothChrom(self.fig, self.canvas))
        file_menu.add_command(label="Compare Chromatogram", command=lambda: functions.addFile(self.fig, self.canvas))
        file_menu.add_command(label="Baseline Correction",
                              command=lambda: Chromatogram.baselineCorrection(self.fig, self.canvas))
        file_menu.add_command(label="Chromatogram Calibration",
                              command=lambda: functions.chromCalibration(self.fig, self.canvas))
        file_menu.add_command(label="Save Chromatogram", command=Chromatogram.saveChrom)
        file_menu.add_command(label="Overlay Quantitation Windows",
                              command=lambda: functions.overlayQuantitationWindows(self.fig, self.canvas))
        file_menu.add_command(label="Quantify Chromatogram",
                              command=lambda: Chromatogram.quantifyChrom(self.fig, self.canvas))
        file_menu.add_command(label="Settings", command=settings.settings_popup)
        file_menu.add_command(label="About HappyTools", command=lambda: gui.info_popup())

        multi_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Multi File", menu=multi_menu)
        multi_menu.add_command(label="Raw Batch Plot", command=lambda: functions.batchPlot(self.fig, self.canvas))
        multi_menu.add_command(label="Normalized Batch Plot",
                               command=lambda: functions.batchPlotNorm(self.fig, self.canvas))
        multi_menu.add_command(label="Batch Process", command=gui.batch_popup)

        advanced_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Advanced Tools", menu=advanced_menu)
        advanced_menu.add_command(label="Peak Detection",
                                  command=lambda: Chromatogram.peak_detection(self.fig, self.canvas))
        advanced_menu.add_command(label="Save Calibrants",
                                  command=lambda: Chromatogram.saveCalibrants(self.fig, self.canvas))
        advanced_menu.add_command(label="Save Annotation", command=lambda: functions.saveAnnotation())


if __name__ == "__main__":
    MainWindow.run()
