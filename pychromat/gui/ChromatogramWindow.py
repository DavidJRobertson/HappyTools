import tkinter as tk
import tkinter.ttk as ttk

from gui.Window import Window
from gui.CustomToolbar import CustomToolbar

import matplotlib
import matplotlib.figure
import matplotlib.image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



class ChromatogramWindow(Window):
    def __init__(self, master, chromatogram):
        super().__init__(master)

        self.chromatogram = chromatogram

        self.master.title("Chromatogram: "+self.chromatogram.filename)
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.lift()

        self.pw = ttk.PanedWindow(self, orient=tk.HORIZONTAL)

        frame1 = ttk.Frame(self.pw)
        self.fig = matplotlib.figure.Figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame1)
        self.toolbar = CustomToolbar(self.canvas, frame1)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas.draw()
        self.pw.add(frame1)

        frame2 = ttk.Frame(self.pw)
        b = ttk.Button(frame2, text="button here")
        b.pack()
        self.pw.add(frame2)

        self.pw.pack()


        # background_file = os.path.join(os.path.dirname(__file__), 'assets', 'UI.png')
        # if os.path.isfile(background_file):
        #     background_image = self.fig.add_subplot(111)
        #     image = matplotlib.image.imread(background_file)
        #     background_image.axis('off')
        #     self.fig.set_tight_layout(True)
        #     background_image.imshow(image)

        # MENUS
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Chromatogram", command=lambda: None)
        file_menu.add_command(label="Save Chromatogram", command=lambda: None)
        2
        file_menu.add_command(label="Compare Chromatogram", command=lambda: None)
        file_menu.add_command(label="Settings", command=lambda: None)
        file_menu.add_command(label="About PyChromat", command=lambda: None)

        #file_menu.add_command(label="Chromatogram Calibration", command=lambda: functions.chromCalibration(self.fig, self.canvas))
        #file_menu.add_command(label="Overlay Quantitation Windows", command=lambda: functions.overlayQuantitationWindows(self.fig, self.canvas))
        #file_menu.add_command(label="Quantify Chromatogram", command=lambda: Chromatogram.quantifyChrom(self.fig, self.canvas))

        baseline_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Baseline", menu=baseline_menu)
        baseline_menu.add_command(label="Detect baseline", command=self.detect_baseline)
        baseline_menu.add_command(label="Correct baseline", command=self.correct_baseline)
        baseline_menu.add_command(label="Smooth Chromatogram", command=self.smooth)

        multi_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Multi File", menu=multi_menu)
        #multi_menu.add_command(label="Raw Batch Plot", command=lambda: functions.batchPlot(self.fig, self.canvas))
        #multi_menu.add_command(label="Normalized Batch Plot", command=lambda: functions.batchPlotNorm(self.fig, self.canvas))
        #multi_menu.add_command(label="Batch Process", command=gui.batch_popup)

        advanced_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Advanced Tools", menu=advanced_menu)
        #advanced_menu.add_command(label="Peak Detection", command=lambda: Chromatogram.peak_detection(self.fig, self.canvas))
        #advanced_menu.add_command(label="Save Calibrants", command=lambda: Chromatogram.saveCalibrants(self.fig, self.canvas))
        #advanced_menu.add_command(label="Save Annotation", command=lambda: functions.saveAnnotation())

        self.plot_chromatogram()

    def smooth(self):
        self.chromatogram.smooth()
        self.plot_chromatogram()

    def detect_baseline(self):
        self.chromatogram.detect_baseline()
        self.plot_chromatogram()

    def correct_baseline(self):
        self.chromatogram.correct_baseline()
        self.plot_chromatogram()

    def plot_chromatogram(self):
        """Plot all traces  on the canvas."""
        self.fig.clear()
        axes = self.fig.add_subplot(111)

        for label, trace in self.chromatogram.traces.items():
            axes.plot(trace.x, trace.y, label=label, linewidth=0.75)

        axes.get_xaxis().get_major_formatter().set_useOffset(False)
        axes.set_xlabel("Time (%s)" % self.chromatogram.time_units)
        axes.set_xlim(self.chromatogram.x_range())

        axes.set_ylabel("%s (%s)" % (self.chromatogram.intensity_metric, self.chromatogram.intensity_units))
        ymin, ymax = self.chromatogram.y_range()
        ypad = 0.2 * (ymax - ymin)
        axes.set_ylim(bottom=ymin-ypad, top=ymax+ypad)

        axes.grid(True)
        handles, labels = axes.get_legend_handles_labels()
        self.fig.legend(handles, labels)

        self.canvas.draw()

    def close(self):
        self.master.destroy()