from tkinter import Toplevel, TclError, Label, LEFT, SOLID


class ToolTip(object):
    def __init__(self, widget, text):
        """Create a tooltip.
        This function will create a tooltip and assign it to the widget that
        was handed to this function. The widget will then show the provided
        text upon mouseover.
        """
        self.widget = widget
        self.tip_window = None
        self.text = text
        widget.bind('<Enter>', self.show_tip())
        widget.bind('<Leave>', self.hide_tip())

    def show_tip(self):
        """Display text in tooltip window"""
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tip_window = Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(1)
        self.tip_window.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            self.tip_window.tk.call("::tk::unsupported::MacWindowStyle",
                                "style", self.tip_window._w,
                                "help", "noActivates")
        except TclError:
            pass
        label = Label(self.tip_window, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      wraplength=500, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None



