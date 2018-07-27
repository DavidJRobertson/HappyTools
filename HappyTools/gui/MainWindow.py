from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
import matplotlib
import matplotlib.figure
import os
import Chromatogram
import gui
import settings
import functions
from gui.CustomToolbar import CustomToolbar

version = "0.0.2"
output = "summary.results"


class MainWindow(object):
    def __init__(self, master):
        # SETTINGS
        if os.path.isfile(settings):
            settings.get_settings()

        # CANVAS
        self.fig = matplotlib.figure.Figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.toolbar = CustomToolbar(self.canvas, master)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
        self.canvas.draw()

        # FRAME
        frame = Frame(master)
        master.title("HappyTools "+str(version))

        if os.path.isfile(os.path.join(".","ui","Icon.ico")):
            master.iconbitmap(default=os.path.join(".","ui","Icon.ico"))
        if os.path.isfile(os.path.join(".","ui","UI.png")):
            background_image = self.fig.add_subplot(111)
            image = matplotlib.image.imread(os.path.join(".","ui","UI.png"))
            background_image.axis('off')
            self.fig.set_tight_layout(True)
            background_image.imshow(image)

        # QUIT
        def close():
            root.destroy()
            root.quit()
        root.protocol("WM_DELETE_WINDOW", lambda: close())

        # MENU
        menu = Menu(master)
        master.config(menu=menu)

        file_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Chromatogram", command=lambda: functions.openFile(self.fig, self.canvas))
        file_menu.add_command(label="Smooth Chromatogram", command=lambda: Chromatogram.smoothChrom(self.fig, self.canvas))
        file_menu.add_command(label="Compare Chromatogram", command=lambda: functions.addFile(self.fig, self.canvas))
        file_menu.add_command(label="Baseline Correction", command=lambda: Chromatogram.baselineCorrection(self.fig, self.canvas))
        file_menu.add_command(label="Chromatogram Calibration", command=lambda: functions.chromCalibration(self.fig, self.canvas))
        file_menu.add_command(label="Save Chromatogram", command=Chromatogram.saveChrom)
        file_menu.add_command(label="Overlay Quantitation Windows", command=lambda: functions.overlayQuantitationWindows(self.fig, self.canvas))
        file_menu.add_command(label="Quantify Chromatogram", command=lambda: Chromatogram.quantifyChrom(self.fig, self.canvas))
        file_menu.add_command(label="Settings", command=settings.settingsPopup)
        file_menu.add_command(label="About HappyTools", command=lambda: gui.info_popup())

        multi_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Multi File", menu=multi_menu)
        multi_menu.add_command(label="Raw Batch Plot", command=lambda: functions.batchPlot(self.fig, self.canvas))
        multi_menu.add_command(label="Normalized Batch Plot", command=lambda: functions.batchPlotNorm(self.fig, self.canvas))
        multi_menu.add_command(label="Batch Process", command=gui.batch_popup)

        advanced_menu = Menu(menu, tearoff=0)
        menu.add_cascade(label="Advanced Tools", menu=advanced_menu)
        advanced_menu.add_command(label="Peak Detection", command=lambda: Chromatogram.peakDetection(self.fig, self.canvas))
        advanced_menu.add_command(label="Save Calibrants", command=lambda: Chromatogram.saveCalibrants(self.fig, self.canvas))
        advanced_menu.add_command(label="Save Annotation", command=lambda: functions.saveAnnotation())


# Call the main app
if __name__ == "__main__":
    root = Tk()
    app = MainWindow(root)
    root.mainloop()
