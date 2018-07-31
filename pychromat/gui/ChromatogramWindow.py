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

        canvas_pane = ttk.Frame(self.pw)
        self.fig = matplotlib.figure.Figure(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=canvas_pane)
        self.toolbar = CustomToolbar(self.canvas, canvas_pane)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas.draw()
        self.pw.add(canvas_pane)

        right_pane = ttk.Frame(self.pw)
        traces_label = ttk.Label(right_pane, text="Traces")
        traces_label.pack(anchor=tk.W)

        traces_lb_frame = ttk.Frame(right_pane)
        traces_lb_scrollbar = ttk.Scrollbar(traces_lb_frame, orient=tk.VERTICAL)
        self.traces_listbox = tk.Listbox(traces_lb_frame, selectmode=tk.MULTIPLE, exportselection=tk.NO, yscrollcommand=traces_lb_scrollbar.set)
        traces_lb_scrollbar.config(command=self.traces_listbox.yview)
        traces_lb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.traces_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        traces_lb_frame.pack(fill=tk.X, expand=tk.YES, anchor=tk.N)
        self.traces_selected = []
        self.poll_traces_listbox()
        self.pw.add(right_pane)

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
        """Plot all traces  on the canvas. Update the traces listbox. """

        # if traces deleted, then remove them from the listbox
        trace_entries = self.traces_listbox.get(0, tk.END)
        to_delete = []
        for entry in trace_entries:
            if entry not in self.chromatogram.traces.keys():
                to_delete.append(entry)
        for del_entry in to_delete:
            trace_entries = self.traces_listbox.get(0, tk.END)
            for index, entry in trace_entries:
                if entry == del_entry:
                    self.traces_listbox.delete(index)
                    break

        # if new traces added, insert them into the listbox
        for label, trace in self.chromatogram.traces.items():
            if label not in trace_entries:
                self.traces_listbox.insert(tk.END, label)
                self.traces_listbox.selection_set(tk.END)

        # now get a list of selected (visible) traces to plot
        visible_traces = []
        for index in self.traces_listbox.curselection():
            visible_traces.append(self.traces_listbox.get(index))


        self.fig.clear()
        axes = self.fig.add_subplot(111)

        #for label, trace in self.chromatogram.traces.items():
        #    axes.plot(trace.x, trace.y, label=label, linewidth=0.75)

        for label in visible_traces:
            trace = self.chromatogram.traces[label]
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

    def poll_traces_listbox(self):
        now = self.traces_listbox.curselection()
        if now != self.traces_selected:
            self.plot_chromatogram()
            self.traces_selected = now
        self.after(100, self.poll_traces_listbox)