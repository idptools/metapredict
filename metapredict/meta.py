##
## meta.py
## 
## meta.py contains all the user-facing function associated with metapredict. If a new function is added it should be included
## here and added to the __all__ list
## 

##Handles the primary functions

# NOTE - any new functions must be added to this list!
__all__ =  ['predict_disorder_domains', 'predict_disorder', 'graph_disorder', 'percent_disorder', 'predict_disorder_fasta', 'graph_disorder_fasta', 'predict_disorder_uniprot', 'graph_disorder_uniprot', 'predict_disorder_domains_uniprot', 'predict_disorder_domains_from_external_scores', 'graph_pLDDT_uniprot', 'predict_pLDDT_uniprot', 'graph_pLDDT_fasta', 'predict_pLDDT_fasta', 'graph_pLDDT', 'predict_pLDDT']
 
import os
import sys


# note - we imort packages below with a leading _ which means they are ignored in the import

#import protfasta to read .fasta files
import protfasta as _protfasta

# import stuff for confidence score predictions
from alphaPredict import alpha as _AF2pLDDTscores

# import stuff for IDR predictor from backend. Note the 'as _*' hides the imported
# module from the user
from metapredict.backend.meta_predict_disorder import meta_predict as _meta_predict
from metapredict.backend import meta_tools as _meta_tools

#import stuff for graphing from backend
from metapredict.backend.meta_graph import graph as _graph
from metapredict.backend import domain_definition as _domain_definition

# stuff for uniprot from backend
from metapredict.backend.uniprot_predictions import fetch_sequence as _fetch_sequence
from metapredict.metapredict_exceptions import MetapredictError



def predict_disorder_domains_from_external_scores(disorder, 
                                                  sequence=None,
                                                  disorder_threshold=0.5, 
                                                  minimum_IDR_size=12, 
                                                  minimum_folded_domain=50,
                                                  gap_closure=10,
                                                  override_folded_domain_minsize=False):
    
    """

    This function takes in disorder scores generated from another predictor and applies the same domain-decomposition
    algorithm as predict_disorder_domains() does to extract out congigous IDRs. For example, if one were to predict
    disorder using the (excellent) ODiNPred, download the resulting scores, and read the scores into a list, that 
    list could be passed as the $disorder argument to this function.

    Note that the settings used here may be inapplicable to another disorder predictor, so you may need to play
    around with the parameters including disorder_threshold, minimum_IDR_size, minimum_folded_domain and gap_closure.

    the following information:

        [0] -  Smoothed disorder score used to aid in domain boundary identification. This can be useful for 
               understanding how IDRs/folded domains were identified, and will vary depending on the settings 
               provided.
         
        [1] - a list of elements, where each element defines the start and end position of each IDR 

        [2] - a list of elements, where each element defines the start and end position of each folded region  


    Parameters
    -------------

    disorder : list
        A list of per-residue disorder scores.

    sequence : str
        An optional argument which, if provided, is assumed to reflect the the amino acid sequence from which the 
        disorder scores were computed. Note if these do not match one another in length then the function raises
        an exception. Default = None

    disorder_threshold : float
        Value that defines what 'disordered' is based on the input predictor score. The higher the value the more
        stringent the cutoff. Default = 0.5. 

    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - i.e. we CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
        Defines where we expect the limit of small folded domains to be. This is NOT a hard limit and functions to modulate
        the removal of large gaps (i.e. gaps less than this size are treated less strictly). Note that, in addition, 
        gaps < 35 are evaluated with a threshold of 0.35*disorder_threshold and gaps < 20 are evaluated with a threshold 
        of 0.25*disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which
        are IDRs in isolation) often show up with reduced apparent disorder within IDRs, and but can be as short as 20-30 
        residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain 
        to be identified. Default=50.

    gap_closure : int
        Defines the largest gap that would be 'closed'. Gaps here refer to a scenario in which you have two groups
        of disordered residues seprated by a 'gap' of un-disordered residues. In general large gap sizes will favour 
        larger contigous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes
        very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps
        are increasingly rare. Default=10.

    override_folded_domain_minsize : bool
        By default this function includes a fail-safe check that assumes folded domains
        really shouldn't be less than 35 or 20 residues. However, for some approaches we
        may wish to over-ride these thresholds to match the passed minimum_folded_domain
        value. If this flag is set to True this override occurs. This is generally not 
        recommended unless you expect there to be well-defined sharp boundaries which could
        define small (20-30) residue folded domains. This is not provided as an option in the normal
        predict_disorder_domains for metapredict. Default = False. 


    Returns
    ---------
    list
        Always returns a list with three elements, as outlined below.

        [0] - Smoothed disorder score used to aid in domain boundary identification. This can be useful for understanding
              how IDRs/folded domains were identified, and will vary depending on the settings provided

        [1] - a list of elements, where each element defines the start and end position of each IDR. If a sequence was provided
              the third element in each sub-element is the IDR sequence. If no sequence was provided, then each sub-element is
              simply len=2.
 
        [2] - a list of elements, where each element defines the start and end position of each folded region. If a sequence was 
              provided the third element in each sub-element is the folded domain sequence. If no sequence was provided, then each 
              sub-element is simply len=2.

    """

    # if a sequence was provided check it makes sense in terms of type and length...
    if sequence is not None:
        try:
            if len(sequence) != len(disorder):
                raise MetapredictError('Disorder and sequence info are not length matched [disorder length = {len(disorder)}, sequence length = {len(sequence)}')
        except Exception:
            raise MetapredictError('Could not compare length of disorder and sequence parameters. Make sure sequence is a str and disorder a list')

        return_sequence = True

    # if sequence is None create a fake sequence and set return_sequence to False
    else:
        sequence = 'A'*len(disorder)
        return_sequence = False
        
            
    # run the get_domains function, passing in parameters
    return_tuple = _domain_definition.get_domains(sequence, 
                                                  disorder, 
                                                  disorder_threshold=disorder_threshold,                                            
                                                  minimum_IDR_size=minimum_IDR_size, 
                                                  minimum_folded_domain=minimum_folded_domain,
                                                  gap_closure=gap_closure,
                                                  override_folded_domain_minsize=override_folded_domain_minsize)
                                                 
    

    # if we are going to use the sequence then return 
    if return_sequence:
        return [return_tuple[0], return_tuple[1], return_tuple[2]]

    # if we are not using the sequence
    else:
        # extract out the IDR and FD boundaires, discarding the sequence info which is irrelevant
        IDRs = []
        for local_idr in return_tuple[1]:
            IDRs.append([local_idr[0],local_idr[1]])

        FDs = []
        for local_fd in return_tuple[2]:
            FDs.append([local_fd[0],local_fd[1]])
            
        return [return_tuple[0],IDRs, FDs]


    



def predict_disorder_domains(sequence, 
                             disorder_threshold=0.42, 
                             minimum_IDR_size=12, 
                             minimum_folded_domain=50,
                             gap_closure=10, 
                             normalized=True):
    """

    This function takes an amino acid sequence, a disorder score, and returns a 4-position tuple with
    the following information:

    [0] - 'Raw' disorder score; i.e. disorder propensity as predicted by metapredict

    [1] - Smoothed disorder score used to aid in domain boundary identification. This can be useful for understanding
          how IDRs/folded domains were identified, and will vary depending on minimum_region_size.

    [2] - a list of elements, where each element is itself a list where position 0 and 1 define the IDR location 
          and position 2 gives the actual IDR sequence

    [3] - a list of elements, where each element is itself a list where position 0 and 1 define the folded domain 
          location and position 2 gives the actual folded domain sequence.

    Parameters
    -------------

    sequence : str
        Amino acid sequence

    disorder_threshold : float
        Value that defines what 'disordered' is based on the metapredict disorder score. The higher the value the more
        stringent the cutoff. Default = 0.42

    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - i.e. we CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
        Defines where we expect the limit of small folded domains to be. This is NOT a hard limit and functions to modulate
        the removal of large gaps (i.e. gaps less than this size are treated less strictly). Note that, in addition, 
        gaps < 35 are evaluated with a threshold of 0.35*disorder_threshold and gaps < 20 are evaluated with a threshold 
        of 0.25*disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which
        are IDRs in isolation) often show up with reduced apparent disorder within IDRs, and but can be as short as 20-30 
        residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain 
        to be identified. Default=50.

    gap_closure : int
        Defines the largest gap that would be 'closed'. Gaps here refer to a scenario in which you have two groups
        of disordered residues seprated by a 'gap' of un-disordered residues. In general large gap sizes will favour 
        larger contigous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes
        very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps
        are increasingly rare. Default=10.

    Returns
    ---------
    list
        Always returns a list with 4 elements, as outlined below

        [0] - List of floats - this is the 'raw' disorder score; i.e. disorder propensity as predicted by metapredict

        [1] - List of floats - this is the smoothed disorder score used to aid in domain boundary identification. 
              This can be useful for understanding how IDRs/folded domains were identified, and will vary depending on 
              minimum_region_size.
          
        [2] - a list of elements, where each element is itself a list where position 0 and 1 define the IDR location 
              and position 2 gives the actual IDR sequence

        [3] - a list of elements, where each element is itself a list where position 0 and 1 define the folded domain 
              location and position 2 gives the actual folded domain sequence.


    """
    
    disorder = predict_disorder(sequence, normalized)

    return_tuple = _domain_definition.get_domains(sequence, 
                                                 disorder, 
                                                 disorder_threshold=disorder_threshold,                                            
                                                 minimum_IDR_size=minimum_IDR_size, 
                                                 minimum_folded_domain=minimum_folded_domain,
                                                 gap_closure=gap_closure)
                                                 
    
    return [disorder, return_tuple[0], return_tuple[1], return_tuple[2]]


def predict_disorder(sequence, normalized=True):
    """
    Function to return disorder of a single input sequence. Returns the
    predicted values as a list.

    Parameters
    ------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    normalized : bool
        Flag which defines in the predictor should control and normalize such that all values fall 
        between 0 and 1. The underlying learning model can, in fact output some negative values 
        and some values greater than 1. Normalization controls for this. Default = True

    Returns
    --------
    
    list
        Returns a list of floats that corresponds to the per-residue disorder score.

    """
    # make all residues upper case 
    sequence = sequence.upper()

    # return predicted values of disorder for sequence
    return _meta_predict(sequence, normalized=normalized)


def graph_disorder(sequence, 
                   title = 'Predicted protein disorder', 
                   disorder_threshold = 0.3,
                   pLDDT_scores=False,
                   shaded_regions = None,
                   shaded_region_color = 'red',
                   DPI=150, 
                   output_file=None):
    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"

    disorder_threshold : float
        Sets a threshold which draws a horizontal black line as a visual guide along
        the length of the figure. Must be a value between 0 and 1. Default = 0.3
    
    pLDDT_scores : Bool
        Sets whether to include the predicted confidence scores from
        AlphaFold2

    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red).
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, or .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    Returns
    --------

    None
        No return object, but, the graph is saved to disk or displayed locally.


    """

    # check that a valid range was passed for disorder_threshold
    _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)

    # ensure sequence is upper case
    sequence = sequence.upper()

    # check that a valid set of shaded regions was passed
    _meta_tools.valid_shaded_region(shaded_regions, len(sequence))

    # call the graph function
    _graph(sequence, title = title, disorder_threshold = disorder_threshold, 
        pLDDT_scores = pLDDT_scores, shaded_regions = shaded_regions,
        shaded_region_color = shaded_region_color, 
        DPI=DPI, output_file = output_file) 

def predict_pLDDT(sequence):
    """
    Function to return predicted pLDDT scores from
    AlphaFold2 for an input sequeunce.

    Parameters
    ------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    Returns
    --------
    
    list
        Returns a list of floats that corresponds to the per-residue pLDDT score.

    """
    # make all residues upper case 
    sequence = sequence.upper()

    # return predicted values of disorder for sequence
    return _AF2pLDDTscores.predict(sequence)


def graph_pLDDT(sequence, 
                   title = 'Predicted AF2 pLDDT Confidence Score',
                   pLDDT_scores=True,
                   disorder_scores=False, 
                   shaded_regions = None,
                   shaded_region_color = 'red',
                   DPI=150, 
                   output_file=None):
    """
    Function to plot the AF2 pLDDT scores of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"
    
    pLDDT_scores : Bool
        Sets whether to include the predicted confidence scores from
        AlphaFold2

    disorder_scores : Bool
        Whether to include disorder scores. Can set to False if you
        just want the AF2 confidence scores.

    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red).
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, or .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    Returns
    --------

    None
        No return object, but, the graph is saved to disk or displayed locally.


    """


    # ensure sequence is upper case
    sequence = sequence.upper()

    # check that a valid set of shaded regions was passed
    _meta_tools.valid_shaded_region(shaded_regions, len(sequence))

    # call the graph function
    _graph(sequence, title = title, pLDDT_scores = pLDDT_scores,
        disorder_scores=disorder_scores, shaded_regions = shaded_regions,
        shaded_region_color = shaded_region_color, 
        DPI=DPI, output_file = output_file) 



def percent_disorder(sequence, cutoff=0.3):
    """
    function to return the percent disorder for any given protein.
    By default, uses 0.3 as a cutoff (values greater than or equal
    to 0.3 will be considered disordered).

    This function rounds to a single decimal place.
    
    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    disorder_threshold : float
        Sets a threshold which defines if a residue is considered disordered
        or not. Default = 0.3.

    Returns
    -----------

    float
        Returns a floating point value between 0 and 100 that defines what
        percentage of the sequence is considered disordered.

    """
    # make all residues upper case 
    sequence = sequence.upper()

    # set dis equal to the predicted disorder for the input sequence
    dis = _meta_predict(sequence)

    # set arbitrarily chosen variable n to equal 0
    n = 0

    # for predicted disorder values in dis:
    for i in dis:
        #if predicted value is greater than cutoff, add one to n
        if i >= cutoff:
            n += 1

    """
    percent disorder is equal to n (number of residues with predicted
    value >= cutoff) divided by the total number of residues in the
    input sequence.
    """
    percent_disordered = 100*round((n / len(dis)), 3)
    #return percent_disordered
    return(percent_disordered)



#./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\
#./\./\./\./\./\./\./\./\./\./\./\./\.FASTA STUFF./\./\./\./\./\./\./\./\./\./\./\./\
#./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\././\./\

#Various functions for working with fasta files to make everyones life easier.


def predict_disorder_fasta(filepath, 
                           output_file = None,
                           normalized=True,
                           invalid_sequence_action='convert'):
    """
    Function to read in a .fasta file from a specified filepath.
    Returns a dictionary of disorder values where the key is the 
    fasta header and the values are the predicted disorder values.
    
    Parameters
    -------------

    filepath : str 
        The path to where the .fasta file is located. The filepath should end in the file name. 
        For example (on MacOS):filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"

    output_file : str
        By default, a dictionary of predicted values is returned immediately. However, you can specify 
        an output filename and path and a .csv file will be saved. This should include any file extensions.
        Default = None.

    normalized : bool
        Flag which defines in the predictor should control and normalize such that all values fall 
        between 0 and 1. The underlying learning model can, in fact output some negative values 
        and some values greater than 1. Normalization controls for this. Default = True

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino acids. Default is 
        convert, which as the name implies converts via standard rules. See 
        https://protfasta.readthedocs.io/en/latest/read_fasta.html for more information.


    Returns
    --------

    dict or None
        If output_file is set to None (as default) then this fiction returns a dictionary of sequence ID to
        disorder vector. If output_file is set to a filename then a .csv file will instead be written and 
        no return data will be provided.

    """

    # Importantly, by default this function corrects invalid residue
    # values using protfasta.read_fasta() because the disorder predictor
    # cannot have non-amino acid values as an input.

    # Test to see if the data_file exists
    test_data_file = os.path.abspath(filepath)

    if not os.path.isfile(test_data_file):
        raise FileNotFoundError('Datafile does not exist.')

    protfasta_seqs = _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action, return_list = True)

    # initialize empty dictionary to be populated with the the fasta headers (key) 
    # and the predicted disorder values (value)
    disorder_dict = {}

    # for the sequences in the protffasta_seqs list:
    for seqs in protfasta_seqs:

        # set cur_header equal to the fasta header
        cur_header = seqs[0]

        # set cur_seq equal to the sequence associated with the fasta header
        cur_seq = seqs[1]

        # make all values for curSeq uppercase so they work with predictor
        cur_seq = cur_seq.upper()

        # set cur_disorder equal to the predicted values for cur_seq
        cur_disorder = _meta_predict(cur_seq, normalized=normalized)

        disorder_dict[cur_header] = cur_disorder

    # if we did not request an output file 
    if output_file is None:
        return disorder_dict

    # else write to disk 
    else:
        _meta_tools.write_csv(disorder_dict, output_file)

def predict_pLDDT_fasta(filepath, 
                           output_file = None,
                           invalid_sequence_action='convert'):
    """
    Function to read in a .fasta file from a specified filepath.
    Returns a dictionary of pLDDT values where the key is the 
    fasta header and the values are the predicted pLDDT values.
    
    Parameters
    -------------

    filepath : str 
        The path to where the .fasta file is located. The filepath should end in the file name. 
        For example (on MacOS):filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"

    output_file : str
        By default, a dictionary of predicted values is returned immediately. However, you can specify 
        an output filename and path and a .csv file will be saved. This should include any file extensions.
        Default = None.

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino acids. Default is 
        convert, which as the name implies converts via standard rules. See 
        https://protfasta.readthedocs.io/en/latest/read_fasta.html for more information.


    Returns
    --------

    dict or None
        If output_file is set to None (as default) then this fiction returns a dictionary of sequence ID to
        pLDDT vector. If output_file is set to a filename then a .csv file will instead be written and 
        no return data will be provided.

    """

    # Importantly, by default this function corrects invalid residue
    # values using protfasta.read_fasta() because the pLDDT predictor
    # cannot have non-amino acid values as an input.

    # Test to see if the data_file exists
    test_data_file = os.path.abspath(filepath)

    if not os.path.isfile(test_data_file):
        raise FileNotFoundError('Datafile does not exist.')

    protfasta_seqs = _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action, return_list = True)

    # initialize empty dictionary to be populated with the the fasta headers (key) 
    # and the predicted confidence values (value)
    confidence_dict = {}

    # for the sequences in the protffasta_seqs list:
    for seqs in protfasta_seqs:

        # set cur_header equal to the fasta header
        cur_header = seqs[0]

        # set cur_seq equal to the sequence associated with the fasta header
        cur_seq = seqs[1]

        # make all values for curSeq uppercase so they work with predictor
        cur_seq = cur_seq.upper()

        # set cur_disorder equal to the predicted values for cur_seq
        cur_disorder = _AF2pLDDTscores.predict(cur_seq)

        confidence_dict[cur_header] = cur_disorder

    # if we did not request an output file 
    if output_file is None:
        return confidence_dict

    # else write to disk 
    else:
        _meta_tools.write_csv(confidence_dict, output_file)




def graph_disorder_fasta(filepath, 
                         pLDDT_scores=False,
                         disorder_threshold = 0.3,
                         DPI=150, 
                         output_dir = None,
                         output_filetype='png', 
                         invalid_sequence_action='convert',
                         indexed_filenames=False):

    """
    Function to make graphs of predicted disorder from the sequences
    in a specified .fasta file. By default will save the generated
    graphs to the location output_path specified in filepath.

    **WARNING**: It is unadvisable to not include an output directory if you are reading in a .fasta 
    file with many sequences! This is because each graph must be closed individually before the next 
    will appear. Therefore, you will spend a bunch of time closing each graph.

    **NB**: You cannot specify the output file name here! By default, the file name will
    be the first 14 characters of the FASTA header followed by the filetype as specified 
    by filetype. If you wish for the files to include a unique leading number (i.e. X_rest_of_name
    where X starts at 1 and increments) then set indexed_filenames to True. This can be useful if you
    have sequences where the 1st 14 characters may be identical, which would otherwise overwrite an 
    output file.

    Parameters
    -----------

    filepath : str 
        The path to where the .fasta file is located. The filepath should end in the file name. 
        For example (on MacOS):filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"

    pLDDT_scores : Bool
        Sets whether to include the predicted pLDDT scores from
        AlphaFold2

    disorder_threshold : float
        Sets a threshold which draws a horizontal black line as a visual guide along
        the length of the figure. Must be a value between 0 and 1.
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_dir : str
        If provided, the output_dir variable defines the directory where file should besaved
        to be saved. This should be a writeable filepath. Default is None. Output files are 
        saved with filename as first 14 chars of fasta header (minus bad characters) plus the
        appropriate file extension, as defined by filetype.

    output_filetype : str
        String that defines the output filetype to be used. Must be one of pdf, png, jpg.

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino acids. Default is 
        convert, which as the name implies converts via standard rules. See 
        https://protfasta.readthedocs.io/en/latest/read_fasta.html for more information.

    indexed_filenames : bool
        Bool which, if set to true, means filenames start with an unique integer.


    Returns
    ---------

    None
        No return object, but, the graph is saved to disk or displayed locally.

    """

    # Test to see if the data_file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError('Datafile [%s] does not exist'%(filepath))

    # Test to see if output directory exists
    if output_dir is not None:
        if not os.path.isdir(output_dir):
            raise FileNotFoundError('Proposed output directory could not be found')

    # validate disorder_threshold
    _meta_tools.valid_range(disorder_threshold, 0,1)

    # use protfasta to read in fasta file
    sequences =  _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action)

    # now for each sequence...
    idx_counter = 0
    for idx in sequences:
        
        # increment the index counter...
        idx_counter = idx_counter + 1

        # grab the sequence and convert to upper as well
        local_sequence = sequences[idx].upper()

        # make sure file doesn't try to save if no output dir specified
        if output_dir is not None:

            # define the full filename with filetype. NOTE - we use os.sep as an OS-independent way to define
            # filename and filepath. This may end up with the filename containing a double slash, but this is fine
            # and matplotlib deals with this appropriately. This should be a POSIX-compliant way to do cross-platform
            # file writing
            if indexed_filenames:
                filename = output_dir + os.sep + "%i_"%(idx_counter) + _meta_tools.sanitize_filename(idx)[0:14] + ".%s"%(output_filetype)
            else:
                filename = output_dir + os.sep + _meta_tools.sanitize_filename(idx)[0:14] + ".%s"%(output_filetype)

            # define title (including bad chars)
            title = idx[0:14]

            # plot!        
            graph_disorder(local_sequence, title=title, pLDDT_scores=pLDDT_scores, DPI=DPI, output_file=filename)

        # if no output_dir specified just graph the seq        
        else:
            # define title (including bad chars)
            title = idx[0:14]            
            graph_disorder(local_sequence, title=title, pLDDT_scores=pLDDT_scores, DPI=DPI)

def graph_pLDDT_fasta(filepath, 
                         DPI=150, 
                         output_dir = None,
                         output_filetype='png', 
                         invalid_sequence_action='convert',
                         indexed_filenames=False):

    """
    Function to make graphs of predicted pLDDT from the sequences
    in a specified .fasta file. By default will save the generated
    graphs to the location output_path specified in filepath.

    **WARNING**: It is unadvisable to not include an output directory if you are reading in a .fasta 
    file with many sequences! This is because each graph must be closed individually before the next 
    will appear. Therefore, you will spend a bunch of time closing each graph.

    **NB**: You cannot specify the output file name here! By default, the file name will
    be the first 14 characters of the FASTA header followed by the filetype as specified 
    by filetype. If you wish for the files to include a unique leading number (i.e. X_rest_of_name
    where X starts at 1 and increments) then set indexed_filenames to True. This can be useful if you
    have sequences where the 1st 14 characters may be identical, which would otherwise overwrite an 
    output file.

    Parameters
    -----------

    filepath : str 
        The path to where the .fasta file is located. The filepath should end in the file name. 
        For example (on MacOS):filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_dir : str
        If provided, the output_dir variable defines the directory where file should besaved
        to be saved. This should be a writeable filepath. Default is None. Output files are 
        saved with filename as first 14 chars of fasta header (minus bad characters) plus the
        appropriate file extension, as defined by filetype.

    output_filetype : str
        String that defines the output filetype to be used. Must be one of pdf, png, jpg.

    invalid_sequence_action : str
        Tells the function how to deal with sequences that lack standard amino acids. Default is 
        convert, which as the name implies converts via standard rules. See 
        https://protfasta.readthedocs.io/en/latest/read_fasta.html for more information.

    indexed_filenames : bool
        Bool which, if set to true, means filenames start with an unique integer.


    Returns
    ---------

    None
        No return object, but, the graph is saved to disk or displayed locally.

    """

    # Test to see if the data_file exists
    if not os.path.isfile(filepath):
        raise FileNotFoundError('Datafile [%s] does not exist'%(filepath))

    # Test to see if output directory exists
    if output_dir is not None:
        if not os.path.isdir(output_dir):
            raise FileNotFoundError('Proposed output directory could not be found')


    # use protfasta to read in fasta file
    sequences =  _protfasta.read_fasta(filepath, invalid_sequence_action = invalid_sequence_action)

    # now for each sequence...
    idx_counter = 0
    for idx in sequences:
        
        # increment the index counter...
        idx_counter = idx_counter + 1

        # grab the sequence and convert to upper as well
        local_sequence = sequences[idx].upper()

        # make sure file doesn't try to save if no output dir specified
        if output_dir is not None:

            # define the full filename with filetype. NOTE - we use os.sep as an OS-independent way to define
            # filename and filepath. This may end up with the filename containing a double slash, but this is fine
            # and matplotlib deals with this appropriately. This should be a POSIX-compliant way to do cross-platform
            # file writing
            if indexed_filenames:
                filename = output_dir + os.sep + "%i_"%(idx_counter) + _meta_tools.sanitize_filename(idx)[0:14] + ".%s"%(output_filetype)
            else:
                filename = output_dir + os.sep + _meta_tools.sanitize_filename(idx)[0:14] + ".%s"%(output_filetype)

            # define title (including bad chars)
            title = idx[0:14]

            # plot!        
            graph_pLDDT(local_sequence, title=title, DPI=DPI, output_file=filename)

        # if no output_dir specified just graph the seq        
        else:
            # define title (including bad chars)
            title = idx[0:14]      
            graph_pLDDT(local_sequence, title=title, DPI=DPI)



def predict_disorder_uniprot(uniprot_id, normalized=True):
    """
    Function to return disorder of a single input sequence. Uses a 
    Uniprot ID to get the sequence.

    Parameters
    ------------

    uniprot_ID : str
         The uniprot ID of the sequence to predict

    no_ID : str
         The uniprot ID of the sequence to predict

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """

    # fetch sequence from Uniprot
    sequence = _fetch_sequence(uniprot_id)
        
    # return predicted values of disorder for sequence
    return _meta_predict(sequence, normalized)



def predict_pLDDT_uniprot(uniprot_id):
    """
    Function to return pLDDT score of a single input sequence. Uses a 
    Uniprot ID to get the sequence.

    Parameters
    ------------

    uniprot_ID : str
         The uniprot ID of the sequence to predict

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """

    # fetch sequence from Uniprot
    sequence = _fetch_sequence(uniprot_id)
        
    # return predicted values of disorder for sequence
    return _AF2pLDDTscores.predict(sequence)



def graph_disorder_uniprot(uniprot_id, 
                           title = 'Predicted protein disorder',
                           pLDDT_scores=False, 
                           disorder_threshold = 0.3,
                           shaded_regions = None,
                           shaded_region_color = 'red',
                           DPI=150, 
                           output_file=None):

    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"

    pLDDT_scores : Bool
        Sets whether to include the predicted pLDDT scores from
        AlphaFold2

    disorder_threshold : float
        Sets a threshold which draws a horizontal black line as a visual guide along
        the length of the figure. Must be a value between 0 and 1.
    
    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red).
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, or .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """
    # check that a valid range was passed for 
    _meta_tools.valid_range(disorder_threshold, 0.0, 1.0)

    # grab uniprot sequence
    sequence = _fetch_sequence(uniprot_id)

    # graph sequence
    _graph(sequence, title=title, pLDDT_scores=pLDDT_scores, disorder_threshold=disorder_threshold, shaded_regions=shaded_regions, shaded_region_color=shaded_region_color, DPI=DPI, output_file = output_file) 
    



def graph_pLDDT_uniprot(uniprot_id, 
                           title = 'Predicted AF2 pLDDT Scores', 
                           shaded_regions = None,
                           shaded_region_color = 'red',
                           DPI=150, 
                           output_file=None):

    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Parameters
    -------------

    sequence : str 
        Input amino acid sequence (as string) to be predicted.

    title : str
        Sets the title of the generated figure. Default = "Predicted protein disorder"
    
    shaded_regions : list of lists
        A list of lists, where sub-elements are of length 2 and contain start and end
        values for regions to be shaded. Assumes that sanity checking on positions has
        already been done. Default is None, but if there were specific regions you wanted
        to highlight this might, for example, look like shaded_regions=[[1,10],[40,50]], 
        which would shade between 1 and 10 and then between 40 and 50. This can be useful
        to either highlight specific IDRs or specific folded domains

    shaded_region_color : str
        String that defines the color of the shaded region. The shaded region is always
        set with an alpha of 0.3 but the color can be any valid matplotlib color name
        or a hex color string (i.e. "#ff0000" is red).
    
    DPI : int
        Dots-per-inch. Defines the resolution of the generated figure. Passed to the
        dpi argument in ``matplotlib.pyplot.savefig()``.

    output_file : str
        If provided, the output_file variable defines the location and type of the file
        to be saved. This should be a file location and filename with a valid matplotlib
        extension (such as .png, or .pdf) and, if provided, this value is passed directly
        to the ``matplotlib.pyplot.savefig()`` function as the ``fname`` parameter. 
        Default = None.

    Returns
    ----------

    None
        No return object, but, the graph is saved to disk or displayed locally.
    
    """

    # grab uniprot sequence
    sequence = _fetch_sequence(uniprot_id)

    # graph sequence
    _graph(sequence, title=title, disorder_scores=False, pLDDT_scores=True, shaded_regions=shaded_regions, shaded_region_color=shaded_region_color, DPI=DPI, output_file = output_file) 
    



def predict_disorder_domains_uniprot(uniprot_id, 
                             disorder_threshold=0.42, 
                             minimum_IDR_size=12, 
                             minimum_folded_domain=50,
                             gap_closure=10, 
                             normalized=True):
    """

    This function takes an amino acid sequence, a disorder score, and returns a 4-position tuple with
    the following information:

    [0] - 'Raw' disorder score; i.e. disorder propensity as predicted by metapredict

    [1] - Smoothed disorder score used to aid in domain boundary identification. This can be useful for understanding
          how IDRs/folded domains were identified, and will vary depending on minimum_region_size.

    [2] - a list of elements, where each element is itself a list where position 0 and 1 define the IDR location 
          and position 2 gives the actual IDR sequence

    [3] - a list of elements, where each element is itself a list where position 0 and 1 define the folded domain 
          location and position 2 gives the actual folded domain sequence.


    Parameters
    -------------

    uniprot_ID : String
        The uniprot ID of the sequence to predict

    sequence : str
        Amino acid sequence

    disorder_threshold : float
        Value that defines what 'disordered' is based on the metapredict disorder score. The higher the value the more
        stringent the cutoff. Default = 0.42

    minimum_IDR_size : int
        Defines the smallest possible IDR. This is a hard limit - i.e. we CANNOT get IDRs smaller than this. Default = 12.

    minimum_folded_domain : int
        Defines where we expect the limit of small folded domains to be. This is NOT a hard limit and functions to modulate
        the removal of large gaps (i.e. gaps less than this size are treated less strictly). Note that, in addition, 
        gaps < 35 are evaluated with a threshold of 0.35*disorder_threshold and gaps < 20 are evaluated with a threshold 
        of 0.25*disorder_threshold. These two lengthscales were decided based on the fact that coiled-coiled regions (which
        are IDRs in isolation) often show up with reduced apparent disorder within IDRs, and but can be as short as 20-30 
        residues. The folded_domain_threshold is used based on the idea that it allows a 'shortest reasonable' folded domain 
        to be identified. Default=50.

    gap_closure : int
        Defines the largest gap that would be 'closed'. Gaps here refer to a scenario in which you have two groups
        of disordered residues seprated by a 'gap' of un-disordered residues. In general large gap sizes will favour 
        larger contigous IDRs. It's worth noting that gap_closure becomes relevant only when minimum_region_size becomes
        very small (i.e. < 5) because really gaps emerge when the smoothed disorder fit is "noisy", but when smoothed gaps
        are increasingly rare. Default=10.

    Returns
    ----------

    list
        Always returns a list with 4 elements, as outlined below

        [0] - List of floats - this is the 'raw' disorder score; i.e. disorder propensity as predicted by metapredict

        [1] - List of floats - this is the smoothed disorder score used to aid in domain boundary identification. 
              This can be useful for understanding how IDRs/folded domains were identified, and will vary depending on 
              minimum_region_size.
          
        [2] - a list of elements, where each element is itself a list where position 0 and 1 define the IDR location 
              and position 2 gives the actual IDR sequence

        [3] - a list of elements, where each element is itself a list where position 0 and 1 define the folded domain 
              location and position 2 gives the actual folded domain sequence.


    """
    sequence = _fetch_sequence(uniprot_id)

    disorder = predict_disorder(sequence, normalized=normalized)

    return_tuple = _domain_definition.get_domains(sequence, 
                                                 disorder, 
                                                 disorder_threshold=disorder_threshold,                                            
                                                 minimum_IDR_size=minimum_IDR_size, 
                                                 minimum_folded_domain=minimum_folded_domain,
                                                 gap_closure=gap_closure)
                                                 
    
    return [disorder, return_tuple[0], return_tuple[1], return_tuple[2]]



