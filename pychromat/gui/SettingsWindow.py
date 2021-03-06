import tkinter as tk
import tkinter.ttk as ttk

from gui.ToolTip import ToolTip
from gui.Window import Window


class SettingsWindow(Window):
    def __init__(self, master):
        super().__init__(master)

        self.master.title("PyChromat Settings")
        self.master.resizable(width=False, height=False)
        self.master.protocol("WM_DELETE_WINDOW", self.close)

        self.var_fig_per_analyte = tk.BooleanVar()
        self.var_fig_per_analyte.set(0)

        self.var_peak_detection_edge = tk.StringVar()
        # self.tkvar_peak_detection_edge.set(peakDetectionEdge)

        # General Settings
        general_label = ttk.Label(self, text="General Settings", font=("Helvetica", 16))
        general_label.grid(row=0, columnspan=2, sticky=tk.W)

        start_label = ttk.Label(self, text="Start Time")
        start_label.grid(row=1, column=0, sticky=tk.W)

        start_window = ttk.Entry(self)
        # start_window.insert(0, start)
        start_window.grid(row=1, column=1, sticky=tk.W)

        end_label = ttk.Label(self, text="End Time")
        end_label.grid(row=2, column=0, sticky=tk.W)

        end_window = ttk.Entry(self)
        # end_window.insert(0, end)
        end_window.grid(row=2, column=1, sticky=tk.W)

        # Peak Detecti#on Settings
        peak_detection_label = ttk.Label(self, text="Peak Detection Settings", font=("Helvetica", 16), padding="0 25 0 0")
        peak_detection_label.grid(row=3, columnspan=2, sticky=tk.W)

        peak_detection_label = ttk.Label(self, text="Minimum Intensity")
        peak_detection_label.grid(row=4, column=0, sticky=tk.W)
        peak_detection = ttk.Entry(self)
        # peak_detection.insert(0, peakDetectionMin)
        peak_detection.grid(row=4, column=1, sticky=tk.W)

        peak_detection_edge_label = ttk.Label(self, text="Edge Method")
        peak_detection_edge_label.grid(row=5, column=0, sticky=tk.W)
        peak_detection_edge_frame = ttk.Frame(self)
        peak_detection_edge_radio_sigma = ttk.Radiobutton(peak_detection_edge_frame, text="Sigma", variable=self.var_peak_detection_edge, value="Sigma")
        peak_detection_edge_radio_sigma.pack(side=tk.LEFT)
        peak_detection_edge_radio_fwhm = ttk.Radiobutton(peak_detection_edge_frame, text="FWHM", variable=self.var_peak_detection_edge, value="FWHM")
        peak_detection_edge_radio_fwhm.pack(side=tk.RIGHT)
        peak_detection_edge_frame.grid(row=5, column=1, sticky=tk.E+tk.W)


        peak_detection_edge_value_label = ttk.Label(self, text="Sigma Value")
        peak_detection_edge_value_label.grid(row=6, column=0, sticky=tk.W)
        peak_detection_edge_value_window = ttk.Entry(self)
        # peak_detection_edge_value_window.insert(0, peakDetectionEdgeValue)
        peak_detection_edge_value_window.grid(row=6, column=1, sticky=tk.W)

        # Calibration Settings
        calibration_label = ttk.Label(self, text="Calibration Settings", font=("Helvetica", 16), padding="0 25 0 0")
        calibration_label.grid(row=7, columnspan=2, sticky=tk.W)

        min_peak_label = ttk.Label(self, text="Minimum Peaks")
        min_peak_label.grid(row=8, column=0, sticky=tk.W)
        min_peak_window = ttk.Entry(self)
        # min_peak_window.insert(0, minPeaks)
        min_peak_window.grid(row=8, column=1, sticky=tk.W)

        min_peak_sn_label = ttk.Label(self, text="Minimum S/N")
        min_peak_sn_label.grid(row=9, column=0, sticky=tk.W)
        min_peak_sn_window = ttk.Entry(self)
        # min_peak_sn_window.insert(0, minPeakSN)
        min_peak_sn_window.grid(row=9, column=1, sticky=tk.W)

        # Quantitation Settings
        quantitation_label = ttk.Label(self, text="Quantitation Settings", font=("Helvetica", 16), padding="0 25 0 0")
        quantitation_label.grid(row=10, columnspan=2, sticky=tk.W)

        points_label = ttk.Label(self, text="Datapoints")
        points_label.grid(row=11, column=0, sticky=tk.W)
        points_window = ttk.Entry(self)
        # points_window.insert(0, points)
        points_window.grid(row=11, column=1, sticky=tk.W)

        baseline_order_label = ttk.Label(self, text="Baseline Order")
        baseline_order_label.grid(row=12, column=0, sticky=tk.W)
        baseline_order_window = ttk.Entry(self)
        # baseline_order_window.insert(0, baselineOrder)
        baseline_order_window.grid(row=12, column=1, sticky=tk.W)

        background_window_label = ttk.Label(self, text="Background Window")
        background_window_label.grid(row=13, column=0, sticky=tk.W)
        background_window_window = ttk.Entry(self)
        # background_window_window.insert(0, backgroundWindow)
        background_window_window.grid(row=13, column=1, sticky=tk.W)

        # nobanLabel = Label(top, text="NOBAN Start")
        # nobanLabel.grid(row=14, column=0, sticky=W)
        # nobanWindow = Entry(top)
        # nobanWindow.insert(0, nobanStart)
        # nobanWindow.grid(row=14, column=1, sticky=W)

        slicepoints_label = ttk.Label(self, text="MT Slice points")
        slicepoints_label.grid(row=15, column=0, sticky=tk.W)
        slicepoints_window = ttk.Entry(self)
        # slicepoints_window.insert(0, slicepoints)
        slicepoints_window.grid(row=15, column=1, sticky=tk.W)

        figure_label = ttk.Label(self, text="Create figure for each analyte?")
        figure_label.grid(row=16, column=0, sticky=tk.W, ipadx=5)
        figure_radio_frame = ttk.Frame(self)
        figure_radio_yes = ttk.Radiobutton(figure_radio_frame, text="Yes", variable=self.var_fig_per_analyte, value=1)
        figure_radio_yes.pack(side=tk.LEFT)
        figure_radio_no = ttk.Radiobutton(figure_radio_frame, text="No", variable=self.var_fig_per_analyte, value=0)
        figure_radio_no.pack(side=tk.RIGHT)
        figure_radio_frame.grid(row=16, column=1, sticky=tk.E+tk.W)

        # Close/Save Buttons
        save_button = ttk.Button(self, text="Save", command=self.save)
        save_button.grid(row=17, column=0, sticky=tk.E+tk.W, pady="25 0")

        close_button = ttk.Button(self, text="Close", command=self.close)
        close_button.grid(row=17, column=1, sticky=tk.E+tk.W, pady="25 0")

        # Tooltips
        ToolTip(points_label, "The number of data points that is used to determine the baseline. Specifically, " +
                "this setting specifies how large each segment of the whole chromatogram will be to identify the lowest " +
                "data point per window, i.e. a setting of 100 means that the chromatogram is split into segments of 100 " +
                "data points per segment.")
        ToolTip(start_label, "This setting tells the program from which time point it is supposed to begin " +
                "processing, this setting should be set in such a way that it is before the analytes of interest but " +
                "after any potential big increases or decrease in intensity.")
        ToolTip(end_label,
                "This setting tells the program until which time point it is supposed to begin processing, " +
                "this setting should be set in such a way that it is after the analytes of interest but before any " +
                "potential big increases or decrease in intensity.")
        ToolTip(baseline_order_label,
                "This setting tells the program what sort of function should be used to correct " +
                "the baseline. A value of 1 refers to a linear function, while a value of 2 refers to a quadratic " +
                "function. We advise to use a linear function as the need for any higher order function indicates an " +
                "unexpected event in the chromatography.")
        ToolTip(background_window_label,
                "This setting tells the program the size of the region that will be examined " +
                "to determine the background. A value of 1 means that the program will look from 20.0 to 21.0 minutes " +
                "and 21.4 to 22.4 for an analyte that elutes from 21.0 to 21.4 minutes.")
        # ToolTip(nobanLabel,"This setting specifies the initial estimate for the NOBAN algorithm, specifically a "+
        # "value of 0.25 means that the lowest 25% of all data points will be used as an initial estimate for the "+
        # "background. This value should be changed depending on how many signals there are in the chromatogram, "+
        # "e.g. in a crowded chromatogram this value should be low.")
        ToolTip(slicepoints_label, "The number of conscutive data points that will be used to determine the " +
                "background and noise using the MT method. The MT method will scan all datapoints that fall within the " +
                "background window (specified above) to find the here specified number of consecutive data points that " +
                "yield the lowest average intensity, the average of these data points is then used as background while " +
                "the standard deviation of these data points is used as the noise.")
        ToolTip(figure_label,
                "This setting specifies if PyChromat should create a figure for each integrated peak, " +
                "showing the raw datapoints, background, noise, S/N and GPQ values. This is a very performance intensive " +
                "option and it is recommended to only use this on a subset of your samples (e.g. less than 25 samples).")
        ToolTip(min_peak_label, "This setting specifies the minimum number of calibrant peaks that have to pass the " +
                "specified S/N value that must be present in a chromatogram. A chromatogram for which there are not " +
                "enough calibrant peaks passing the specified criteria will not be calibrated and excluded from further " +
                "quantitation.")
        ToolTip(min_peak_sn_label, "This setting specifies the minimum S/N value a calibrant peak must surpass to be " +
                "included in the calibration. The actual S/N value that is determined by PyChromat depends heavily on " +
                "which method to determine signal and noise is used, the default method being rather conservative.")
        ToolTip(peak_detection_label, "This setting specifies the minimum intensity, relative to the main peak in " +
                "a chromatogram, that the peak detection algorithm will try to annotate. For example, a value of 0.01 " +
                "means that the program will attempt to annotate peaks until the next highest peak is below 1% of the " +
                "intensity of the main peak in the chromatogram.")
        ToolTip(peak_detection_edge_label,
                "This setting specifies if PyChromat will determine the integration window " +
                "using either the full width at half maximum (FWHM) or a specified sigma value. The Sigma value has to be " +
                "specified in the field below if Sigma is the selected method.")
        ToolTip(peak_detection_edge_value_label, "This setting specifies the Sigma value that will be used for " +
                "determining the border of the integration window. A value of 1.0 means that PyChromat will set the " +
                "integration window so that 68.3% of the Gaussian peak will be quantified (2 Sigma = 95.5% and 3 sigma " +
                "= 99.7%). Please note that this value should depend on how complex the chromatogram is, for instance " +
                "a low sigma will yield better results in a complex chromatogram.")

    def close(self):
        self.master.destroy()

    #     global points
    #     global start
    #     global end
    #     global baselineOrder
    #     global backgroundWindow
    #     global backgroundNoise
    #     # global nobanStart
    #     global slicepoints
    #     global createFigure
    #     global minPeaks
    #     global minPeakSN
    #     global peakDetectionMin
    #     global peakDetectionEdge
    #     global peakDetectionEdgeValue
    #
    #     points = int(pointsWindow.get())
    #     start = float(startWindow.get())
    #     end = float(endWindow.get())
    #     baselineOrder = int(baselineOrderWindow.get())
    #     backgroundWindow = float(backgroundWindowWindow.get())
    #     # nobanStart = float(nobanWindow.get())
    #     slicepoints = int(slicepointsWindow.get())
    #     createFigure = str(figureVariable.get())
    #     minPeaks = int(minPeakWindow.get())
    #     minPeakSN = int(minPeakSNWindow.get())
    #     peakDetectionMin = float(peakDetection.get())
    #     peakDetectionEdge = str(peakDetectionEdgeVar.get())
    #     peakDetectionEdgeValue = float(peakDetectionEdgeValueWindow.get())
    #     self.master.destroy()

    def save(self):
        pass
    #     """ TODO
    #     """
    #     with open(gui.settings, 'w') as fw:
    #         fw.write("points:\t" + str(int(pointsWindow.get())) + "\n")
    #         fw.write("start:\t" + str(float(startWindow.get())) + "\n")
    #         fw.write("end:\t" + str(float(endWindow.get())) + "\n")
    #         fw.write("baselineOrder:\t" + str(int(baselineOrderWindow.get())) + "\n")
    #         fw.write("backgroundWindow:\t" + str(float(backgroundWindowWindow.get())) + "\n")
    #         # fw.write("nobanStart:\t"+str(float(nobanWindow.get()))+"\n")
    #         fw.write("noise:\t" + str(noise) + "\n")
    #         fw.write("slicepoints:\t" + str(slicepoints) + "\n")
    #         fw.write("createFigure:\t" + str(figureVariable.get()) + "\n")
    #         fw.write("minPeaks:\t" + str(minPeakWindow.get()) + "\n")
    #         fw.write("minPeakSN:\t" + str(minPeakSNWindow.get()) + "\n")
    #         fw.write("peakDetectionMin:\t" + str(peakDetection.get()) + "\n")
    #         fw.write("peakDetectionEdge:\t" + str(peakDetectionEdgeVar.get()) + "\n")
    #         fw.write("peakDetectionEdgeValue:\t" + str(peakDetectionEdgeValueWindow.get()) + "\n")
