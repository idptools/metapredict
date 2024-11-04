"""
Backend for graphing predicted disorder values in meta.py.
"""


# code for graphing IDRs.
# Import stuff
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from metapredict.metapredict_exceptions import MetapredictError
from metapredict.backend.predictor import predict, predict_pLDDT
from metapredict.parameters import DEFAULT_NETWORK, DEFAULT_NETWORK_PLDDT
from metapredict.backend.network_parameters import metapredict_networks

def graph(sequence,
          title='Predicted protein disorder',
          disorder_threshold=None,
          pLDDT_scores=False,
          disorder_scores=True,
          shaded_regions=None,
          shaded_region_color='red',
          disorder_line_color='blue',
          threshold_line_color='black',
          confidence_line_color = 'darkorange',
          confidence_threshold_color = 'black',
          DPI=150,
          output_file=None,
          version=DEFAULT_NETWORK,
          pLDDT_version=DEFAULT_NETWORK_PLDDT):
    """
    Function for graphing predicted  disorder. By default, this function will show a graph.
    However, you can specify output_file as the
    file path followed by the name of the saved file with the proper extension (.png by default).
    This is the backend for the meta.py graphing functions.
    
    Parameters
    -----------
    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. 
        Default = "Predicted protein disorder"
        
    pLDDT_scores : Bool
        Sets whether to include the predicted confidence scores from
        AlphaFold2. Default = False

    disorder_scores : Bool
        Whether to include disorder scores. Can set to False if you
        just want the AF2 confidence scores. Default = True

    disorder_threshold : float
        Sets a threshold which draws a horizontal black line as a visual
        guide along the length of the figure. Must be a value between 0 
        and 1. Default = 0.3
        
    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain 
        start and end values for regions to be shaded. Assumes that sanity 
        checking on positions has already been done. Default = None.

    shaded_region_color : str or list of strs
        String or list of strings that defines the color of the shaded region. 
        region is always set with an alpha of 0.3 but the color can be 
        any valid matplotlib color name or a hex color string (i.e. "#ff0000" 
        is red). If a single string or a list of length 1 is passed then the
        color defined by that string (or the single element) is used. If a list
        if length = len(shaded_regions) is passed, then EACH shaded region is 
        colored according to the correspondingly-indexed list element. If a 
        mismatch between number of elements in shaded_region and 
        shaded_region_color is found an exception is rasied.

    Disorder_line_color : str
        String that defines the color of the traced disorder score.  Can
        be any standard matplotlib color name or a hex-value (see above). 
        Default = 'blue'.

    threshold_line_color : str
        String that defines the color of the traced disorder score. Can
        be any standard matplotlib color name or a hex-value (see above). 
        Default = 'black'.

    DPI : int
        Dots-per-inch. Defines the resolution of the generated .png figure.
        Note that if an alternative filetype is pathed the matplotlib 
        backened will automatically generate a file of the relevant type (e.g. 
       .pdf, .jpg, or .eps).
        
        
    output_file : str
        If provided, the output_file variable defines the location and type 
        of the file to be saved. This should be a file location and filename 
        with a valid matplotlib extension (such as .png, .jpg, .pdf) and, if 
        provided, this value is passed directly to the 
        ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    version : string
        The network to use for prediction. Default is DEFAULT_NETWORK,
        which is defined at the top of /parameters.
        Options currently include V1, V2, or V3.         

    Returns
    -----------
    None 
        No return type, but will either generate an on-screen plot OR will 
        save a file to disk, depending on if output_file is provided (or not).
        
    """

    # make sure confidence scores and disorder scores not both false
    if pLDDT_scores == False and disorder_scores == False:
        raise MetapredictError('Cannot set both pLDDT_scores and disorder_scores to False. If disorder_scores=False, set confidence_score=True.')
    
    # if confidence scores also added, match the threshold_line_color to the
    # disorder_line_color
    if pLDDT_scores == True and disorder_scores==True:
        threshold_line_color = disorder_line_color
        confidence_threshold_color = confidence_line_color

    # set this such that PDF-generated figures become editable
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    #set n_res to lenght of seq
    n_res = len(sequence)

    # make network uppercase
    version=version.upper()

    # set yValues equal to the predicted disorder from the sequence (normalized)
    if disorder_scores == True:
        yValues = predict(sequence, version=version, return_numpy=False)
        
    # if a name is set, the figure will hold that name as the identifier
    if pLDDT_scores == True and disorder_scores==True:
        fig = plt.figure(num=title, figsize=[11, 3], dpi=DPI, edgecolor='black')
        #axes = fig.add_axes([0.15, 0.15, 0.55, 0.75])
        axes = fig.add_axes([0.1, 0.15, 0.55, 0.75])
    else:
        fig = plt.figure(num=title, figsize=[8, 3], dpi=DPI, edgecolor='black')
        axes = fig.add_axes([0.15, 0.15, 0.75, 0.75])        
    
    # set x label
    axes.set_xlabel("Residue")

    # set disorder threshold
    if disorder_threshold==None:
        disorder_threshold = metapredict_networks[version]['parameters']['disorder_threshold']

    # if default title is used
    if title == 'Predicted protein disorder':
        # if user doesn't set title and confidence scores
        # are added in, change default to include AF2pLDDT
        if pLDDT_scores == True and disorder_scores==True:
            title = 'Predicted protein disorder / AF2pLDDT'
        # if user doesn't set title and only wants confidence scores
        elif pLDDT_scores == True and disorder_scores==False:
            title = 'Predicted protein AF2pLDDT scores'
        else:
            title = title

    # set the title
    axes.set_title(title)
    
    # modify y_label if needed
    if pLDDT_scores == True and disorder_scores == False:
        axes.set_ylabel("AF2 ppLDDT scores")
    else:
        axes.set_ylabel("Consensus Disorder")

    # make x values for each residue with predicted disorder
    xValues = np.arange(1, n_res+1)

    # graph the disorder values of each residue at each point along the x-axis
    if disorder_scores==True:
        ds1, = axes.plot(xValues, yValues, color=disorder_line_color, linewidth='1.6', label = 'Disorder Scores')

    # set x limit as the number of residues
    axes.set_xlim(1, n_res+1)

    # set y limit as 0-1 since the predictor data is normalized from 0 to 1.
    if disorder_scores == True:

        # set ylim
        axes.set_ylim(-0.003, 1.003)

        # plot the disorder cutoff threshold h
        if pLDDT_scores == True:
            ds2, = axes.plot([0, n_res+2], [disorder_threshold, disorder_threshold], color=threshold_line_color, linewidth="1.25", linestyle=(0, (5,5)), label='Disorder Threshold')
        else:
            ds2, = axes.plot([0, n_res+2], [disorder_threshold, disorder_threshold], color=threshold_line_color, linewidth="1.25", linestyle="dashed", label='Disorder Threshold')

        # add dashed lines at 0.2 intervals if cutoff lines not specified
        for i in [0.2, 0.4, 0.6, 0.8]:
            axes.plot([0, n_res+2], [i, i], color="black", linestyle="dashed", linewidth="0.5")
    
    else:

        # if it will just be confidence scores, set to 0 to 100
        axes.set_ylim(0, 100)

        # plot threshold
        ds2, = axes.plot([0, n_res+2], [50, 50], color=confidence_threshold_color, linewidth="1.25", linestyle="dashed", label='Confidence Threshold')

        # add dashed lines at 0.2 intervals if cutoff lines not specified
        for i in [20, 40, 60, 80]:
            axes.plot([0, n_res+2], [i, i], color="black", linestyle="dashed", linewidth="0.5")

    # make sure the shaded_region_color variable makes snese
    if type(shaded_region_color) != list:
        if type(shaded_region_color) == str:
            shaded_region_color = [shaded_region_color]
        else:
            raise MetapredictError('Invalid type passed as shaded_region_color. Expect a list of colors or a string')
    else:
        if len(shaded_region_color) == 1:
            pass
        elif len(shaded_region_color) == len(shaded_regions):
            pass
        else:
            raise MetapredictError('Invalid number of colors passed. If a list is used for shaded_region_color, then the number of elements must be either 1 OR equal the number of shaded regions')
    
    # if we want shaded regions
    if shaded_regions is not None:
        for boundary in range(0, len(shaded_regions)):

            cur_boundary = shaded_regions[boundary]
            start = cur_boundary[0]
            end = cur_boundary[1]

            # if we had multiple shaded regions
            if len(shaded_region_color) == len(shaded_regions):
                cur_color = shaded_region_color[boundary]
            else:
                cur_color = shaded_region_color[0]
            axes.axvspan(start, end, alpha=0.2, color=cur_color, linewidth=0)

    # if graphing both confidence and disorder
    if pLDDT_scores == True and disorder_scores==True:

        # get confidence scores
        pLDDT_scores = predict_pLDDT(sequence, version=pLDDT_version)
        twin1 = axes.twinx()
        af1, = twin1.plot(xValues, pLDDT_scores, color = confidence_line_color, label="Predicted AF2pLDDT")
        twin1.set_ylim(0, 100)
        twin1.set_ylabel('Predicted AF2pLDDT Scores')
        af2, = axes.plot([0, n_res+2], [0.5, 0.5], color=confidence_line_color, linewidth="1.25", linestyle=(5, (5,5)), label = 'AF2pLDDT Threshold')
        axes.legend(handles=[ds1, ds2, af1, af2], bbox_to_anchor=(1.14, 1), loc='best', prop={'size': 12})

    elif pLDDT_scores == True and disorder_scores == False:

        # import alpha predict
        from alphaPredict import alpha

        # get confidence scores
        pLDDT_scores = alpha.predict(sequence)

        # plot the confidence scores
        axes.plot(xValues, pLDDT_scores, color=confidence_line_color, linewidth='1.6', label = 'Disorder Scores')    


    if output_file is None:
        plt.show()
    else:
        plt.savefig(fname=output_file, dpi=DPI)
        plt.close()
