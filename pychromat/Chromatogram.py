import os
from Trace import Trace



class Chromatogram(object):
    def __init__(self, filename):
        self.filename = filename
        self.traces = {
            'raw': Trace.from_file(self.filename)
        }

    def plot_multi_data(self, fig, canvas, data):
        """Plot all chromatograms in data on the canvas.

        This function first clears the canvas and then draws all the
        chromatograms that are in the data list on the canvas.

        Keyword arguments:
        fig -- matplotlib figure object
        canvas -- tkinter canvas object
        data -- list of tuples, consisting of two numbers per tuple
        """
        fig.clear()
        axes = fig.add_subplot(111)
        for i in data:
            xd = []
            yd = []
            for j in i[1]:
                xd.append(j[0])
                yd.append(j[1])
            axes.plot(xd, yd, label=os.path.split(i[0])[-1])
        axes.set_xlabel("Time [m]")
        axes.set_ylabel("Intensity [au]")
        handles, labels = axes.get_legend_handles_labels()
        fig.legend(handles, labels)
        canvas.draw()
