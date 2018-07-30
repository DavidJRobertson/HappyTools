import tkinter as tk

from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk


class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas_, parent_):
        self.toolitems = (
            ('Home',        'Reset original view',                          'home',         'home'),
            ('Back',        'Back to previous view',                        'back',         'back'),
            ('Forward',     'Forward to next view',                         'forward',      'forward'),
            ('Pan',         'Pan axes with left mouse, zoom with right',    'move',         'pan'),
            ('Zoom',        'Zoom to rectangle',                            'zoom_to_rect', 'zoom'),
            ('Axes',        'Define the X- and Y-axis limits',              'subplots',     'plot_axes'),
            ('Subplots',    'Configure subplots',                           'subplots',     'configure_subplots'),
            ('Save',        'Save the figure',                              'filesave',     'save_figure'),
        )
        NavigationToolbar2Tk.__init__(self, canvas_, parent_)

    def plot_axes(self):
        def close():
            try:
                self.canvas.figure.axes[0].set_xlim([float(x_min_window.get()),float(x_max_window.get())])
            except ValueError:
                pass
            try:
                self.canvas.figure.axes[0].set_ylim([float(y_min_window.get()),float(y_max_window.get())])
            except ValueError:
                pass
            self.canvas.draw()
            top.destroy()
        self.push_current()
        top = tk.Toplevel()
        top.title("Configure Axes")
        top.protocol("WM_DELETE_WINDOW", close)

        x_label = tk.Label(top, text="X-axis", font="bold")
        x_label.grid(row=0, column=0, sticky=tk.W)

        x_min_window = tk.Entry(top)
        x_min_window.grid(row=0, column=1, sticky=tk.W)

        x_max_window = tk.Entry(top)
        x_max_window.grid(row=0, column=2, sticky=tk.W)

        y_label = tk.Label(top, text="Y-axis", font="bold")
        y_label.grid(row=1, column=0, sticky=tk.W)

        y_min_window = tk.Entry(top)
        y_min_window.grid(row=1, column=1, sticky=tk.W)

        y_max_window = tk.Entry(top)
        y_max_window.grid(row=1, column=2, sticky=tk.W)