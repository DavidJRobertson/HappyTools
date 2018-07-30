import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import os
from gui.AboutWindow import AboutWindow
from gui.BatchWindow import BatchWindow
from gui.ChromatogramWindow import ChromatogramWindow
from gui.SettingsWindow import SettingsWindow
from gui.Window import Window
from Chromatogram import Chromatogram


class PyChromatGui(Window):
    @classmethod
    def run(cls):
        root = tk.Tk()
        mw = cls(root)
        # unfortunately we need this hack or scrolling sometimes causes crashes on Mac OS
        while True:
            try:
                root.mainloop()
                break
            except UnicodeDecodeError:
                pass

    def __init__(self, master):
        super().__init__(master)

        self.master.title("PyChromat")
        self.master.resizable(width=False, height=False)

        icon_file = os.path.join(os.path.dirname(__file__), 'assets', 'Icon.ico')
        if os.path.isfile(icon_file):
            self.master.iconbitmap(default=icon_file)

        self.button1 = ttk.Button(self, text='About PyChromat', width=25, command=self.open_about_window)
        self.button1.pack()

        self.button2 = ttk.Button(self, text='Batch process', width=25, command=self.open_batch_window)
        self.button2.pack()

        self.button3 = ttk.Button(self, text='Open chromatogram', width=25, command=self.open_chromatogram_window)
        self.button3.pack()

        self.button4 = ttk.Button(self, text='Settings', width=25, command=self.open_settings_window)
        self.button4.pack()

        self.master.attributes("-topmost", True)
        self.master.attributes("-topmost", False)

    def open_about_window(self):
        AboutWindow(tk.Toplevel(self.master))

    def open_batch_window(self):
        BatchWindow(tk.Toplevel(self.master))

    def open_settings_window(self):
        SettingsWindow(tk.Toplevel(self.master))

    def open_chromatogram_window(self):
        file = tk.filedialog.askopenfilename(title="Open Chromatogram File")
        if file:
            chromatogram = Chromatogram(file)
            ChromatogramWindow(tk.Toplevel(self.master), chromatogram)


if __name__ == "__main__":
    PyChromatGui.run()
