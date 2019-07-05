import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../lib")
sys.path.append(lib_path)
import detMetrics as dm

def create_parser():
    """Command line interface creation with arguments definition.
    Returns:
        argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(description='Average ROC Plotter.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("paths", nargs='+', help="Sequence of .dm file paths")
    return parser

class System():
    """Class implementing data container for a system loaded from a dm file.
    Attributes:
        fpr (numpy.ndarray): False Positive Rates array
        tpr (numpy.ndarray): True Positive Rates array
        label (str): Label used in the plot's legend
        line_options (dict): dictionnary of matplotlib.lines.Line2D options
    """
    def __init__(self, fpr, tpr, label=None, line_options="default"):
        self.fpr = fpr
        self.tpr = tpr
        self.label = label
        self.line_options = self.get_default_line_options(line_options)
    
    def get_default_line_options(self, line_options):
        """Creates a default set of line options if the "default" value 
           is provided. Show a subset of potential options available.
        """
        if line_options=="default":
            default_line_options_dict = {"color":"blue",
                                         "linewidth":2,
                                         "linestyle":"solid",
                                         "marker":None,
                                         "markersize":None,
                                         "markeredgewidth":None,
                                         "markerfacecolor":None,
                                         "markeredgecolor":None,
                                         "markeredgewidth":None,
                                         "antialiased":True,
                                         "drawstyle":"default"}
            return default_line_options_dict
        else:
            return line_options


def create_systems_from_dm(dm_filepaths):
    """Create the sequence of System object, initialised 
    with the loading of dm files
    Parameters:
        dm_filepaths (list): list of path to dm files.
    Returns:
        list: list of System objects
    """
    systems = []
    for i, path in enumerate(dm_filepaths):
        try:
            if os.path.isfile(path): # Use this instead of catching  FileNotFoundError for Python2 support
                dm_object = dm.load_dm_file(path)
            else:
                print("FileNotFoundError: No such file or directory: '{}'".format(path))
                sys.exit(1)
        except IOError as e:
            print("IOError: {}".format(str(e)))
            sys.exit(1)

        except UnicodeDecodeError as e:
            print("UnicodeDecodeError: {}\n".format(str(e)))
            sys.exit(1)
        
        system = System(dm_object.fpr, dm_object.tpr, label="System_{}".format(i), line_options="default")
        systems.append(system)
    return systems


def roc_plot(systems, 
             title="Receiver Operating Characteristic", 
             x_label="False Positive Rate", 
             y_label="True Positive Rate",
             figsize=(10, 10)):
    """ Basic roc plot function. Plot a sequence of roc curves based
    on the list of system provided. It allows a few plot customizations.
    Parameters:
        systems (list): list of System objects
        title (str): Set the plot title
        x_label (str): Set the label for the x-axis
        y_label (str): Set the label for the y-axis
        figsize (float, float): width, height in inches
    Returns:
        The matplotlib.pyplot.figure created
    """
    fig = plt.figure(figsize=figsize, constrained_layout=True)
    axe = fig.add_subplot(111)
    linewidth, linestyle = 2, "solid"
    axe.plot([0, 1], [0, 1], color='navy', linewidth=linewidth, linestyle="--")

    for system in systems:
        axe.plot(system.fpr, system.tpr, label=system.label, **system.line_options)

    axe.axis(xmin=0.0,xmax=1.0,ymin=0.0,ymax=1.05)
    axe.set_xlabel(x_label)
    axe.set_ylabel(y_label)
    axe.set_title(title)
    axe.grid()    
    axe.legend(loc="lower right")
    return fig

def create_average_system(systems, resolution=500, label="average", line_options="default"):
    """Instanciate the pseudo system representing the average of systems's fprs and tpr.
    The function performs an linear interpolation with the provided resolution of each
    roc curves and compute the mean in each interpolated points.
    Parameters:
        systems (list): list of System objects
        resolution (int): number of point on the x-axis where the curves will be interpolated.
        label (str): Label used in the plot's legend for the average system
        line_option (dict): dictionnary of matplotlib.lines.Line2D options for the average system
    Returns:
        System: the average system object
    """
    x = np.linspace(0, 1, resolution)
    ys = [np.interp(x, sys.fpr, sys.tpr) for sys in systems]
    return System(x, np.vstack(ys).mean(0), label="average", line_options=line_options)

def roc_plot_average(systems, average_line_options="default", **kwargs):
    """Main function plotting the average of multiple roc curves
    Parameters:
        systems (list): list of System objects
        average_line_options (dict): dictionnary of matplotlib.lines.Line2D options for the average system
        **kwargs: Options to pass to the roc_plot() method
    """
    if isinstance(systems, list):
        avg_sys = create_average_system(systems, resolution=500, label="average", line_options=average_line_options)
        systems.append(avg_sys)
        fig = roc_plot(systems, **kwargs)
        plt.show()
    else:
        print("Error: the system argument must be a list.")

if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if len(args.paths) > 1:

        systems = create_systems_from_dm(args.paths)
        roc_plot_average(systems, average_line_options={"color":"red"})

    else:
        print("Error: At least two inputs must be provided to compute the average.")



