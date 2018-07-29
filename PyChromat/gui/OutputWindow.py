import tkinter as tk


class OutputWindow(object):
    """Create a pop-up enabling output selection.

    This function creates a pop up box that allows the user to specify
    what output should be shown in the final summary. The default value
    for all variables is off (0) and by ticking a box it is set to on
    (1).

    """

    def __init__(self, master):
        # if outputWindow.get() == 1:
        #     return
        # outputWindow.set(1)

        self.master = master
        self.master.title("Output Options")
        self.master.resizable(width=False, height=False)
        self.master.grab_set()
        self.master.protocol("WM_DELETE_WINDOW", self.close)

        #outputWindow = tk.IntVar()
        self.absInt = tk.IntVar()
        self.relInt = tk.IntVar()
        self.bckSub = tk.IntVar()
        self.bckNoise = tk.IntVar()
        self.peakQual = tk.IntVar()

        select_all_button = tk.Button(self.master, text="Select All", command=self.select_all)
        select_all_button.grid(row=0, column=0, sticky=tk.W)

        select_none_button = tk.Button(self.master, text="Select None", command=self.select_none)
        select_none_button.grid(row=0, column=1, sticky=tk.E)

        text1 = tk.Label(self.master, text="Base Outputs", font="bold")
        text1.grid(row=1, column=0, sticky=tk.W)

        text2 = tk.Label(self.master, text="Output Modifiers", font="bold")
        text2.grid(row=1, column=1, sticky=tk.W)

        ai = tk.Checkbutton(self.master, text="Analyte Intensity\u00B9", variable=self.absInt, onvalue=1, offvalue=0)
        ai.grid(row=2, column=0, sticky=tk.W)

        ri = tk.Checkbutton(self.master, text="Relative Intensity\u00B9", variable=self.relInt, onvalue=1, offvalue=0)
        ri.grid(row=3, column=0, sticky=tk.W)

        pq = tk.Checkbutton(self.master, text="Peak Quality Criteria", variable=self.peakQual, onvalue=1, offvalue=0)
        pq.grid(row=4, column=0, sticky=tk.W)

        bn = tk.Checkbutton(self.master, text="Background and Noise", variable=self.bckNoise, onvalue=1, offvalue=0)
        bn.grid(row=5, column=0, sticky=tk.W)

        bck = tk.Checkbutton(self.master, text="\u00B9Background subtracted Intensities", variable=self.bckSub, onvalue=1, offvalue=0)
        bck.grid(row=2, column=1, sticky=tk.W)

        button = tk.Button(self.master, text='Ok', command=self.close)
        button.grid(row=6, column=0, columnspan=2)

        self.master.lift()

    def close(self):
        #outputWindow.set(0)
        self.master.grab_release()
        self.master.destroy()

    def select_all(self):
        self.absInt.set(1)
        self.relInt.set(1)
        self.bckSub.set(1)
        self.bckNoise.set(1)
        self.peakQual.set(1)

    def select_none(self):
        self.absInt.set(0)
        self.relInt.set(0)
        self.bckSub.set(0)
        self.bckNoise.set(0)
        self.peakQual.set(0)
