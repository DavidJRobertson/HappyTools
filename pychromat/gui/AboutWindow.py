import tkinter as tk
import tkinter.ttk as ttk
from gui.Window import Window


class AboutWindow(Window):
    INFORMATION = ("PyChromat Version v0.03 by David Robertson <david@robertson.yt>\n\n"
                   "Based on HappyTools by Bas Cornelis Jansen <bas.c.jansen@gmail.com>\n\n"
                   "This software is released under the Apache 2.0 License. Full details regarding this license can "
                   "be found at the following URL: \n"
                   "http://www.apache.org/licenses/LICENSE-2.0")

    def __init__(self, master):
        super().__init__(master)

        self.master.title("About PyChromat")
        self.master.resizable(width=False, height=False)

        about = ttk.Label(self, text=self.INFORMATION, justify=tk.LEFT, wraplength=250)
        about.pack()