import tkinter as tk
import tkinter.filedialog
from gui.ToolTip import ToolTip
from gui.OutputWindow import OutputWindow


class BatchWindow(object):
    """Batch processing pop-up.

    This window is used to control the batch processing. Specifically, it allows the user to select a
    calibration file, an analyte file, select the desired outputs (by
    calling the outputPopup function) and starting the batch process.
    """

    def __init__(self, master):
        self.master = master
        self.master.title("Batch Process")
        self.master.resizable(width=False, height=False)
        self.master.protocol("WM_DELETE_WINDOW", self.close)

        self.calibration_file = tk.StringVar()
        self.analyte_file = tk.StringVar()
        self.batch_folder = tk.StringVar()

        calibration_button = tk.Button(self.master, text="Calibration File", width=20, command=self.set_calibration_file)
        calibration_button.grid(row=1, column=0, sticky=tk.W)
        calibration_label = tk.Label(self.master, textvariable=self.calibration_file, width=20)
        calibration_label.grid(row=1, column=1)

        analyte_button = tk.Button(self.master, text="Analyte File", width=20, command=self.set_analyte_file)
        analyte_button.grid(row=2, column=0, sticky=tk.W)
        analyte_label = tk.Label(self.master, textvariable=self.analyte_file, width=20)
        analyte_label.grid(row=2, column=1)

        batch_button = tk.Button(self.master, text="Batch Directory", width=20, command=self.set_batch_folder)
        batch_button.grid(row=3, column=0, sticky=tk.W)
        batch_label = tk.Label(self.master, textvariable=self.batch_folder, width=20)
        batch_label.grid(row=3, column=1, sticky=tk.W)

        output_button = tk.Button(self.master, text="Output Options", command=self.open_output_window)
        output_button.grid(row=4, column=0, columnspan=2, sticky=tk.E + tk.W)

        run_button = tk.Button(self.master, text="Run", width=20, command=self.run)
        run_button.grid(row=5, column=0, sticky=tk.W)
        close_button = tk.Button(self.master, text="Close", width=20, command=self.close)
        close_button.grid(row=5, column=1, sticky=tk.E)

        # Tooltips
        self.calibrate_tooltip = ToolTip(calibration_button,
                "This button will allow you to select your calibration file, the program expects a " +
                "tab separated text file where each line consists of a peak ID, peak RT and a RT window.")
        self.analyte_tooltip = ToolTip(analyte_button,
                "This button will allow you to select your analyte file, the program expects a tab separated " +
                "text file where each line consists of a peak ID, peak RT and a RT window.")
        self.output_tooltip =ToolTip(output_button, "This button will open another window in which you can select which outputs you want " +
                "PyChromat to show in the final summary.")

        self.master.lift()

    def close(self):
        self.master.destroy()

    def open_output_window(self):
        OutputWindow(tk.Toplevel(self.master))

    def set_calibration_file(self):
        """Ask for the calibration file."""
        self.calibration_file.set(tk.filedialog.askopenfilename(title="Calibration File"))

    def set_analyte_file(self):
        """Ask for the analyte file."""
        self.analyte_file.set(tk.filedialog.askopenfilename(title="Analyte File"))

    def set_batch_folder(self):
        """Ask for the batch folder. """
        self.batch_folder.set(tk.filedialog.askdirectory(title="Batch Folder"))

    def run(self):
        """Start the batch process. """
        batchFunctions.batchProcess(self.calibration_file, self.analyte_file, self.batch_folder)