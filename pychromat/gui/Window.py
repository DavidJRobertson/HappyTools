import tkinter as tk
import tkinter.ttk as ttk


class Window(ttk.Frame):
    """ Base window class """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, padding=10)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)

        # Necessary for resizing to work properly
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.lift()

    def close(self):
        self.master.destroy()
