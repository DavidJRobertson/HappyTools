import tkinter.ttk as ttk


class Window(ttk.Frame):
    """ Base window class """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, padding=10)
        self.grid()
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.lift()

    def close(self):
        self.master.destroy()
