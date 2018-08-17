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
        self._create_menus()
        self.pw = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self._create_canvas(self.pw)
        self._create_sidebar(self.pw)
        self.pw.pack(fill=tk.BOTH, expand=tk.YES)
        self._update_display()
        self.master.lift()

    def _create_menus(self):
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Chromatogram", command=lambda: None)
        file_menu.add_command(label="Save Chromatogram", command=lambda: None)
        file_menu.add_command(label="Compare Chromatogram", command=lambda: None)
        file_menu.add_command(label="Settings", command=lambda: None)
        file_menu.add_command(label="About PyChromat", command=lambda: None)

        # file_menu.add_command(label="Chromatogram Calibration", command=lambda: functions.chromCalibration(self.fig, self.canvas))
        # file_menu.add_command(label="Overlay Quantitation Windows", command=lambda: functions.overlayQuantitationWindows(self.fig, self.canvas))
        # file_menu.add_command(label="Quantify Chromatogram", command=lambda: Chromatogram.quantifyChrom(self.fig, self.canvas))

        baseline_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Baseline", menu=baseline_menu)
        baseline_menu.add_command(label="Detect baseline", command=self.detect_baseline)
        baseline_menu.add_command(label="Correct baseline", command=self.correct_baseline)
        baseline_menu.add_command(label="Smooth Chromatogram", command=self.smooth)

        multi_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Multi File", menu=multi_menu)
        # multi_menu.add_command(label="Raw Batch Plot", command=lambda: functions.batchPlot(self.fig, self.canvas))
        # multi_menu.add_command(label="Normalized Batch Plot", command=lambda: functions.batchPlotNorm(self.fig, self.canvas))
        # multi_menu.add_command(label="Batch Process", command=gui.batch_popup)

        advanced_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Advanced Tools", menu=advanced_menu)
        # advanced_menu.add_command(label="Peak Detection", command=lambda: Chromatogram.peak_detection(self.fig, self.canvas))
        # advanced_menu.add_command(label="Save Calibrants", command=lambda: Chromatogram.saveCalibrants(self.fig, self.canvas))
        # advanced_menu.add_command(label="Save Annotation", command=lambda: functions.saveAnnotation())

    def _create_canvas(self, parent):
        canvas_frame = ttk.Frame(parent)
        self.fig = matplotlib.figure.Figure(figsize=(9, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_frame)
        self.toolbar = CustomToolbar(self.canvas, canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas.draw()
        parent.add(canvas_frame, weight=5)

    def _create_sidebar(self, parent):
        sidebar = ttk.Frame(parent)

        # Label
        traces_label = ttk.Label(sidebar, text="Traces")
        traces_label.pack(anchor=tk.W)


        # Treeview
        self.treeview = ttk.Treeview(sidebar, columns=('name',), selectmode=tk.EXTENDED)
        self.treeview.heading('#0', text='Directory Structure', anchor=tk.W)
        self.treeview.heading('name', text='Trace Name', anchor=tk.W)
        # self.treeview.column('size', stretch=0, width=70)
        self.treeview.pack(fill=tk.X, expand=tk.YES, anchor=tk.N)

        parent.add(sidebar, weight=1)

        self.traces_selected = []

    def _update_display(self):
        """Plot all traces on the canvas. Update the traces treeview """

        # additions:
        chromat = self.chromatogram

        if not self.treeview.exists(id(chromat)):
            self.treeview.insert('', tk.END, iid=id(chromat), text=chromat.filename)
        for label, trace in chromat.traces.items():
            if not self.treeview.exists(id(trace)):
                self.treeview.insert(id(chromat), tk.END, iid=id(trace), text=label)

        # deletions todo


        # now get a list of selected (visible) traces to plot
        visible_traces = []
        #for index in self.traces_listbox.curselection():
        #    visible_traces.append(self.traces_listbox.get(index))

        self.fig.clear()
        axes = self.fig.add_subplot(111)

        for label, trace in self.chromatogram.traces.items():
            axes.plot(trace.x, trace.y, label=label, linewidth=0.75)

        #for label in visible_traces:
        #    trace = self.chromatogram.traces[label]
        #    axes.plot(trace.x, trace.y, label=label, linewidth=0.75)

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



    def smooth(self):
        self.chromatogram.smooth()
        self._update_display()

    def detect_baseline(self):
        self.chromatogram.detect_baseline()
        self._update_display()

    def correct_baseline(self):
        self.chromatogram.correct_baseline()
        self._update_display()