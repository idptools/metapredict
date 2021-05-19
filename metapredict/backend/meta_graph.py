"""
Backend for graphing predicted disorder values in meta.py.
"""


# code for graphing IDRs.
# Import stuff
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from metapredict.backend import meta_predict_disorder
from metapredict.backend.meta_predict_disorder import meta_predict as predict


def graph(sequence,
          title='Predicted protein disorder',
          disorder_threshold=0.3,
          shaded_regions=None,
          shaded_region_color='red',
          disorder_line_color='blue',
          threshold_line_color='black',
          DPI=150,
          output_file=None):
    """
    Function for graphing predicted disorder. By default, this function will show a graph.
    However, if saveFig = True, then it will save the figure (by default) to the location
    where the script is (which isn't ideal). However, you can specify outputFile as the
    file path followed by the name of the saved file with the proper extension (.png by default).
    This is the backend for the meta.py graphing functions.

    Parameters
    -----------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"

    disorder_threshold : float
        Sets a threshold which draws a horizontal black line as a visual guide along
        the length of the figure. Must be a value between 0 and 1. Default = 0.3

    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None.

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red). Default = 'red'.

    disorder_line_color : str
        String that defines the color of the traced disorder score.  Can
        be any standard matplotlib color name or a hex-value (see above). 
        Default = 'blue'.

    threshold_line_color : str
        String that defines the color of the traced disorder score. Can
        be any standard matplotlib color name or a hex-value (see above). 
        Default = 'black'.

    DPI : int
        Dots-per-inch. Defines the resolution of the generated .png figure. Note that
        if an alternative filetype is pathed the matplotlib backened will automatically
        generate a file of the relevant type (e.g. .pdf, .jpg, or .eps).

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, .jpg, .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.


    Returns
    -----------
    None 
        No return type, but will either generate an on-screen plot OR will save a file to disk,
        depending on if output_file is provided (or not).

    """

    # set this such that PDF-generated figures become editable
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    # set yValues equal to the predicted disorder from the sequence (normalized)
    yValues = predict(sequence)
    n_res = len(sequence)

    # if a name is set, the figure will hold that name as the identifier
    fig = plt.figure(num=title, figsize=[8, 3], dpi=DPI, edgecolor='black')
    axes = fig.add_axes([0.15, 0.15, 0.75, 0.75])
    axes.set_title(title)
    axes.set_xlabel("Residue")
    axes.set_ylabel("Consensus Disorder")

    # make x values for each residue with predicted disorder
    xValues = np.arange(1, n_res+1)

    # graph the disorder values of each residue at each point along the x-axis
    axes.plot(xValues, yValues, color=disorder_line_color, linewidth='1.6')

    # set x limit as the number of residues
    axes.set_xlim(1, n_res+1)

    # set y limit as 0-1 since the predictor data is normalized from 0 to 1.
    axes.set_ylim(-0.003, 1.003)

    # plot the disorder cutoff threshold h
    axes.plot([0, n_res+2], [disorder_threshold, disorder_threshold], color="black", linewidth="1.25")

    # add dashed lines at 0.2 intervals if cutoff lines not specified
    for i in [0.2, 0.4, 0.6, 0.8]:
        axes.plot([0, n_res+2], [i, i], color="black", linestyle="dashed", linewidth="0.5")

    # if we want shaded regions
    if shaded_regions is not None:
        for boundaries in shaded_regions:
            start = boundaries[0]
            end = boundaries[1]
            axes.axvspan(start, end, alpha=0.2, color=shaded_region_color)

    if output_file is None:
        plt.show()
    else:
        plt.savefig(fname=output_file, dpi=DPI)
        plt.close()
