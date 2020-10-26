"""
meta.py
A protein disorder predictor based on a BRNN (IDP-Parrot) trained
on the consensus disorder values from 8 disorder predictors from 
12 proteomes (see https://mobidb.bio.unipd.it) as of 08/2020.

Handles the primary functions
"""
import os
import sys

#import protfasta to read .fasta files
import protfasta
import csv

#import stuff for IDR predictor from backend
from metapredict.backend import meta_predict_disorder
from metapredict.backend.meta_predict_disorder import meta_predict

#import stuff for graphing from backend
from metapredict.backend import meta_graph
from metapredict.backend.meta_graph import graph


def predict_disorder(sequence, normalized=True):
    """
    Function to return disorder of a single input sequence. Returns the
    predicted values as a list.

    Arguments:
    ----------
    sequence - Input amino acid sequence (as string) to be predicted.

    normalized (optional) - by default predictor returns values normalized between 0 and 1.
    This is because the BRNN will output some negative values and some values greater
    than 1. Setting normalized=False will result in returning the raw predicted values.
    """
    #make all residues upper case 
    sequence=sequence.upper()
    #return predicted values of disorder for sequence
    return meta_predict(sequence, normalized=normalized)


def graph_disorder(sequence, name = " ", DPI=150):
    """
    Function to plot the disorder of an input sequece. Displays immediately.

    Arguments:
    ----------
    sequence - Input amino acid sequence (as string) to be predicted.

    name (optional) - setting the value of name will change the title of the
    graph. By default, the title is "Predicted Protein Disorder", so if you
    for example set name = "- PAB1", the title on the graph will be "Predicted
    Protein Disorder - PAB1". 

    DPI (optional) - default value is 150. Increasing this value will increase
    the resolution of the output graph. Decreasing this value will decrease
    the resolution.
    """
    #make all residues upper case 
    sequence=sequence.upper()
    #graph sequence
    graph(sequence = sequence, name = name, DPI=DPI)



def percent_disorder(sequence, cutoff=0.5):
    """
    function to return the percent disorder for any given protein.
    By default, uses 0.5 as a cutoff (values greater than or equal
    to 0.5 will be considred disordered).
    
    Arguments:
    ----------
    sequence - Input amino acid sequence (as string) to be predicted.
    
    cutoff (optional) the cutoff for the predicted value of an individual
    residue to be considered disordered. By default this value is 0.5. Increasing
    this value will make the cutoff more "strict" in that a higher predicted
    vallue will be required for a residue to be considered disordered.

    Returns the percent disorder for the input sequence as a decimal. 
    1.0 = 100% disordered,
    0.9 = 90% disordered, 
    and so on.
    """
    #make all residues upper case 
    sequence=sequence.upper()
    #set dis equal to the predicted disorder for the input sequence
    dis = meta_predict(sequence)
    #set arbitrarily chosen variable n to equal 0
    n = 0
    #for predicted disorder values in dis:
    for i in dis:
        #if predicted value is greater than cutoff, add one to n
        if i >= cutoff:
            n += 1
        #else continue through the values.
        else:
            continue
    """
    percent disorder is equal to n (number of residues with predicted
    value >= cutoff) divided by the total number of residues in the
    input sequence.
    """
    percent_disordered = (n / len(dis))
    #return percent_disordered
    return(percent_disordered)



#./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\
#./\./\./\./\./\./\./\./\./\./\./\./\.FASTA STUFF./\./\./\./\./\./\./\./\./\./\./\./\
#./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\./\

#Various functions for working with fasta files to make everyones life easier.


def predict_disorder_fasta(filepath, save=False, output_path = "", output_name = "predicted_disorder_values", normalized=True):
    """
    Function to read in a .fasta file from a specified filepath.
    Returns a dictionary of disorder values where the key is the 
    fasta header and the values are the predicted disorder values.
    
    Arguments:
    ----------
    filepath - the path to where the .fasta file is located. The filepath
    should end in the file name. For example (on MacOS):
    filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"
    
    save (optional) - by default, a dictionary of predicted values is 
    returned immediately. However, you can specify save=True in order to 
    save the output as a .csv file. 
    ***important***
    If you specify save=True, then output_path is a required argument!

    output_path - the path to where the output .csv file should be saved. 
    For example, on MacOS:
    output_path="Users/thisUser/Desktop/folder_of_cool_results/"
    ***important***
    You cannot specify the output file name here! By default, the file name will
    be predicted_values.csv. However, you can change the output file name by 
    specifying ouput_name (see below).
    
    output_name (optional) - by default is set to equal "predicted values". However,
    the user can specify output_name="my_cool_output_name" in order to specify the
    name of the output file.
    ***important***
    Do not add a file extension to output_name. The .csv file extension is added 
    automatically. If you do by accident, it will (hopefully) be removed.

    normalized - decide whether the values are normalized from 0 to 1. By default, the
    values are normalized. However, occassionally the raw values from the predictor can be
    negative or greater than 1. If you want thes values, set normalied=False.
    """

    #set variable protfastaSeqs equal to output from protfasta (with correction of invalid sequence values)
    """
    Importantly, by default this function corrects invalid residue
    values using protfasta.read_fasta() because the disorder predictor
    cannot have non-amino acid values as an input.
    """    
    # Test to see if the data_file exists
    test_data_file = os.path.abspath(filepath)
    if not os.path.isfile(test_data_file):
        raise FileNotFoundError('Datafile does not exist.')

    protfasta_seqs = protfasta.read_fasta(filepath, invalid_sequence_action = "convert", return_list = True)
    #initialize empty dictionary to be populated with the the fasta headers (key) 
    #and the predicted disorder values (value)
    disorder_dict = {}
    #for the sequences in the protffasta_seqs list:
    for seqs in protfasta_seqs:
        #set cur_header equal to the fasta header
        cur_header = seqs[0]
        #set cur_seq equal to the sequence associated with the fasta header
        cur_seq = seqs[1]
        #make all values for curSeq uppercase so they work with predictor
        cur_seq = cur_seq.upper()
        #set cur_disorder equal to the predicted values for cur_seq
        cur_disorder = meta_predict(cur_seq, normalized=normalized)
        disorder_dict[cur_header] = cur_disorder

    #if save=False (default), immediately return the dictionary disorder_dict
    if save == False:
        return disorder_dict

    #if save=True, save the disorder_dict to the specified output_path
    else:
        # Test to see that the output path is valid
        test_output_path = os.path.abspath(output_path)
        if not os.path.exists(test_output_path):
            raise FileNotFoundError('Output path is not valid.')

        #Check if there is a .csv in output_name (which there shouldn't be)
        #set try_output_name = output_name
        try_output_name = output_name
        #if there is .csv in try_output_name
        if ".csv" in try_output_name:
            #split try_output_name and set output_file_name equal to everything before .csv
            output_file_name = try_output_name.split(".csv")[0]
        else:
            #if .csv is not in try_output_name, set final output_final_name equal to args.output_name
            output_file_name = output_name

        """
        Make sure output_path ends in / (mac) or \\ (windows).
        This is necessary because earlier when testing the output path using OS,
        a valid output path can still not end in a / or \\. When the path does not
        end in a / or \\, then the file does not get saved correctly but pandas
        doesn't raise an error. I'm not sure this is totally necessary, but
        I made this mistake a few times while testing this stuff so I figured it might
        be a nice feature.
        """
        #Set final_output_path_character = last character in output_path
        final_output_path_character = output_path[-1]
        #if / in output_path (user is using MacOS or linux)
        if "/" in output_path:
            #if the final character in the path does not equal a /
            if final_output_path_character != "/":
                #add in a / to complete file path
                output_path += "/"
        #if \ in output_path (user is using Windows)
        elif "\\" in output_path:
            #if the last character does not equal \
            if final_output_path_character != "\\":
                #add in a \ to output path
                output_path += "\\"

        #finalize output path
        final_output = "{}{}.csv".format(output_path, output_file_name)
        #try to export .csv to path
        try:
            with open(final_output, 'w', newline='') as csvfile:
                csvWriter=csv.writer(csvfile, dialect='excel')
                for header, predictions in disorder_dict.items():
                    temp_predictions=[]
                    temp_predictions.append(header)
                    for i in predictions:
                        predicted_space = "{} ".format(i)
                        temp_predictions.append(predicted_space)
                    csvWriter.writerow(temp_predictions)
        #if this fails...
        except IOError:
            #print IO error
            print("IO error")

def graph_disorder_fasta(filepath, DPI=150, save=True, output_path="", remove_characters=False):
    """
    Function to make graphs of predicted disorder from the sequences
    in a specified .fasta file. By default will save the generated
    graphs to the location output_path specified in filepath.
    
    Arguments:
    ----------
    filepath - the path to where the .fasta file is located. The filepath
    should end in the file name. For example (on MacOS):
    filepath="/Users/thisUser/Desktop/folder_of_seqs/interesting_proteins.fasta"
    
    DPI (optional) - default value is 150. Increasing this value will increase
    the resolution of the output graph. Decreasing this value will decrease
    the resolution. 

    save (optional) - by default, the generated graphs are saved. This can be set
    to False, which will result in the graphs being sequentially shown.
    ***important***
    It is unadvisable to set save=False if you are inputting a large .fasta file! This
    is because each graph must be closed individually before the next will appear. Therefore,
    you will spend a bunch of time closing each graph.

    output_path - the path to where the output graphs should be saved. 
    For example, on MacOS:
    output_path="Users/thisUser/Desktop/folder_of_cool_results/"
    ***important***
    You cannot specify the output file name here! By default, the file name will
    be predicted_disorder followed by 6 characters from the .fasta header (which ideally
    should be a unique identifier that can be input into uniprot) followed by .png. 
    For example, predicted_disorder_sp|O43150|.png

    remove_characters (optional) - allows all non-alphabetic characters to be removed
    from the output file names. If user is on an OS that doesn't allow specific characters
    to be used in file names, this should be a way to get around that.
    """

    # Test to see if the data_file exists
    test_data_file = os.path.abspath(filepath)
    if not os.path.isfile(test_data_file):
        raise FileNotFoundError('Datafile does not exist.')

    #use protfasta to read in fasta file
    """
    Importantly, by default this function corrects invalid residue
    values using protfasta.read_fasta() because the disorder predictor
    cannot have non-amino acid values as an input.
    """
    sequences = protfastaSeqs = protfasta.read_fasta(filepath, invalid_sequence_action = "convert")

    #for key, value in sequences.items (which are the items in the dict returned by protfasta)
    for i, v in sequences.items():
        #set title of graph equal to the first 14 characters of the fasta header after >
        #if the title is long enough to suppor that. Otherwise, use longest possible title
        if len(i) >= 14:
            title = i[0:14]
        else:
            title = i[0:]
        #if remove_characters is False:
        if remove_characters == False:
            #set name equal to the first 14 characters of the fasta header after >
            if len (i) >= 14:
                name = (i[0:14])
            else:
                name = i[0:]
        else:
            #initializing empty string
            empty_name = ""
            #removing all common characters (non-alphabetic) from the fasta header
            for j in i:
                if j==">":
                    continue
                elif j=="|":
                    continue
                elif j=="=":
                    continue
                elif j=="-":
                    continue
                elif j==" ":
                    continue
                else:
                    empty_name += j
            #set final name equal to the first 14 characters from the fasta header with
            #the various characters removed.
            if len(empty_name)>=14:
                name = empty_name[0:14]
            else:
                name = empty_name[0:]

        #set the sequence equal to the amino acid sequence associated with
        #the fasta header and make all amino acids uppercase.
        sequence = v.upper()
        #If save is True (default)
        if save == True:
            # Test to see that the output path is valid
            test_output_path = os.path.abspath(output_path)
            if not os.path.exists(test_output_path):
                raise FileNotFoundError('Output path is not valid.')


            """
            Make sure output_path ends in / (mac) or \\ (windows).
            This is necessary because earlier when testing the output path using OS,
            a valid output path can still not end in a / or \\. When the path does not
            end in a / or \\, then the file does not get saved correctly but pandas
            doesn't raise an error. I'm not sure this is totally necessary, but
            I made this mistake a few times while testing this stuff so I figured it might
            be a nice feature.
            """
            #Set final_output_path_character = last character in output_path
            final_output_path_character = output_path[-1]
            #if / in output_path (user is using MacOS or linux)
            if "/" in output_path:
                #if the final character in the path does not equal a /
                if final_output_path_character != "/":
                    #add in a / to complete file path
                    output_path += "/"
            #if \ in output_path (user is using Windows)
            elif "\\" in output_path:
                #if the last character does not equal \
                if final_output_path_character != "\\":
                    #add in a \ to output path
                    output_path += "\\"

            #set variable output equal to the output_path folowed by the file name which is
            #predicted_disorder_{name}.png, where name is the name specified earlier (first 10 characters
            #of the fasta header either as is or with characters removed if remove_characters is set to true).
            output = "{}predicted_disorder_{}.png".format(output_path, name)
            #use the graph function (specified in meta_graph from the backend) to save the graph.
            graph(sequence = sequence, name = title, DPI = DPI, save_fig = True, output_file = output)
        else:
            #if save was set to False, then just graph the sequences from the .fasta file and show them immediately.
            graph(sequence = sequence, name = title, DPI = DPI)

